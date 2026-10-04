#!/usr/bin/env python3
"""Exercise a built image without external services or persistent user data."""
import argparse
import json
from pathlib import Path
import re
import secrets
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


def docker(*args, check=True):
    p = subprocess.run(['docker', *args], text=True, capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f'docker {args[0]} failed:\n{p.stdout}\n{p.stderr}')
    return p.stdout.strip()


def wait_for(probe, seconds=120):
    deadline = time.monotonic() + seconds
    last = None
    while time.monotonic() < deadline:
        try:
            return probe()
        except Exception as exc:
            last = exc
            time.sleep(2)
    raise RuntimeError(f'Readiness check timed out: {last}')


def request(url):
    # Published loopback ports are local tests, independent of inherited HTTP proxies.
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(url, timeout=5) as r:
        assert r.status == 200
        return r.read().decode()


def smoke(target, image):
    prefix = f'build-smoke-{uuid.uuid4().hex[:12]}'
    containers, volumes = [], []
    network = prefix + '-net'
    docker('network', 'create', network)

    def run(name, *args):
        name = prefix + '-' + name
        containers.append(name)
        docker('run', '-d', '--name', name, '--network', network, *args)
        return name

    def address(name, port):
        bindings = json.loads(docker('inspect', name))[0]['NetworkSettings']['Ports']
        return 'http://127.0.0.1:' + bindings[f'{port}/tcp'][0]['HostPort']

    try:
        with tempfile.TemporaryDirectory(prefix='build-smoke-') as tmp:
            if target == 'bitmappery':
                app = run('app', '-p', '127.0.0.1::5173', image)
                url = address(app, 5173)
                html = wait_for(lambda: request(url + '/'))
                assert '<title>BitMappery</title>' in html and '/@vite/client' not in html
                scripts = re.findall(r'<script\b[^>]*\bsrc="([^"]+)"', html)
                assert scripts, 'Production JavaScript bundle missing'
                for script in scripts:
                    assert len(request(urllib.parse.urljoin(url + '/', script))) > 100
                assert '<title>BitMappery</title>' in request(url + '/editor')
                try:
                    request(url + '/assets/missing-smoke-test.js')
                    raise AssertionError('Missing asset incorrectly returned HTTP 200')
                except urllib.error.HTTPError as exc:
                    assert exc.code == 404
                assert docker('exec', app, 'id', '-u') != '0', 'Web server must be non-root'

            elif target == 'code-server-baked':
                volume = prefix + '-config'
                docker('volume', 'create', volume)
                volumes.append(volume)
                app = run('app', '-v', f'{volume}:/config', '-e', 'PUID=1000', '-e', 'PGID=1000',
                          '-e', 'PASSWORD=local-smoke-password', '-p', '127.0.0.1::8443', image)
                url = address(app, 8443)
                health = wait_for(lambda: json.loads(request(url + '/healthz')), seconds=180)
                # code-server reports "expired" until a browser establishes a
                # heartbeat; it still serves healthy HTTP/login requests.
                assert health['status'] in ('alive', 'expired')
                assert 'code-server' in request(url + '/login').lower()
                tools = ('git', 'python3', 'pipx', 'node', 'npm', 'php', 'composer', 'pnpm',
                         'ncu', 'prettier', 'eslint', 'tsc', 'tsx', 'psql', 'mysql', 'redis-cli')
                for tool in tools:
                    docker('exec', '--user', 'abc', app, tool, '--version')
                docker('exec', '--user', 'abc', app, 'sh', '-ec',
                       'test "$(id -u)" = 1000; test -r /usr/local/share/baked-tools/npm.json; '
                       'printf persistent > /config/.smoke-persistence')
                docker('restart', app)
                # Docker may assign a new ephemeral host port after restart.
                url = address(app, 8443)
                wait_for(lambda: json.loads(request(url + '/healthz')), seconds=180)
                assert docker('exec', '--user', 'abc', app, 'cat', '/config/.smoke-persistence') == 'persistent'

            elif target == 'supersync':
                password = secrets.token_hex(16)
                db = run('db', '--network-alias', 'smoke-db', '-e', 'POSTGRES_USER=smoke',
                         '-e', f'POSTGRES_PASSWORD={password}', '-e', 'POSTGRES_DB=smoke', 'postgres:16-alpine')
                wait_for(lambda: docker('exec', db, 'pg_isready', '-U', 'smoke', '-d', 'smoke'))
                db_url = f'postgresql://smoke:{password}@smoke-db:5432/smoke?connection_limit=5&pool_timeout=10'
                migration = prefix + '-migrate'
                containers.append(migration)
                # Migrations complete before starting the server, matching upstream deployment.
                docker('run', '--name', migration, '--network', network, '-e', f'DATABASE_URL={db_url}',
                       '-e', 'REQUIRE_DATABASE_POOL_LIMITS=true', image, 'sh', 'scripts/migrate-deploy.sh')
                assert docker('exec', db, 'psql', '-U', 'smoke', '-d', 'smoke', '-tAc',
                              'SELECT count(*) FROM _prisma_migrations WHERE finished_at IS NOT NULL;').isdigit()
                assert int(docker('exec', db, 'psql', '-U', 'smoke', '-d', 'smoke', '-tAc',
                                  'SELECT count(*) FROM _prisma_migrations WHERE finished_at IS NOT NULL;')) > 0
                app = run('app', '-e', f'DATABASE_URL={db_url}', '-e', f'JWT_SECRET={secrets.token_hex(32)}',
                          '-e', 'PUBLIC_URL=https://supersync.example.com',
                          '-e', 'WEBAUTHN_RP_ID=supersync.example.com',
                          '-e', 'WEBAUTHN_ORIGIN=https://supersync.example.com', '-e', 'HOST=0.0.0.0',
                          '-p', '127.0.0.1::1900', image)
                health = wait_for(lambda: json.loads(request(address(app, 1900) + '/health')), seconds=180)
                assert health['status'] == 'ok' and health['db'] == 'connected'
                assert 'ghcr.io/super-productivity/supersync' in docker('logs', app)
                command = 'printf overridden-command-ok'
                output = docker('run', '--rm', '-e', 'SUPERSYNC_HIDE_UPSTREAM_NOTICE=true', image, 'sh', '-c', command)
                assert output == 'overridden-command-ok', 'Notice must preserve custom commands and support opt-out'

            elif target == 'iframely':
                config = Path(tmp) / 'config.local.js'
                config.write_text('export default {host: "0.0.0.0", port: 8061, WHITELIST_URL: null, IGNORE_DOMAINS_RE: []};\n')
                config.chmod(0o644)
                fixture_js = ('require("http").createServer((req,res)=>{res.setHeader("Content-Type","text/html");'
                              'res.end("<html><head><title>Build smoke fixture</title><meta property=\\\"og:title\\\" '
                              'content=\\\"Build smoke fixture\\\"></head><body>Fixture</body></html>");}).listen(80,"0.0.0.0")')
                fixture = run('fixture', '--network-alias', 'fixture.example.com', '--user', '0', '--entrypoint', 'node', image, '-e', fixture_js)
                wait_for(lambda: docker('exec', fixture, 'node', '-e',
                                        'fetch("http://127.0.0.1/").then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))'))
                app = run('app', '-v', f'{config}:/iframely/config.local.js:ro',
                          '-e', 'NO_PROXY=localhost,127.0.0.1,fixture.example.com',
                          '-p', '127.0.0.1::8061', image)
                endpoint = address(app, 8061) + '/iframely?url=' + urllib.parse.quote('http://fixture.example.com/', safe='')
                result = wait_for(lambda: json.loads(request(endpoint)))
                assert result['meta']['title'] == 'Build smoke fixture', result

            elif target == 'maxun-browser':
                app = run('app', '--shm-size', '256m', '-p', '127.0.0.1::3002', image)
                health = wait_for(lambda: json.loads(request(address(app, 3002) + '/health')), seconds=180)
                assert health['status'] == 'healthy' and health['wsEndpoint'].startswith('ws://')
                # Connect to the real browser server and render a local fixture, not a public site.
                script = '''
const http = require('http');
const { chromium } = require('playwright');
(async () => {
  const server = http.createServer((req, res) => res.end('<title>Build smoke fixture</title><h1>Rendered</h1>'));
  await new Promise(resolve => server.listen(8090, '127.0.0.1', resolve));
  let browser;
  try {
    const health = await (await fetch('http://127.0.0.1:3002/health')).json();
    browser = await chromium.connect(health.wsEndpoint);
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:8090');
    if (await page.title() !== 'Build smoke fixture') throw new Error('Browser did not render fixture');
    if (await page.locator('h1').textContent() !== 'Rendered') throw new Error('DOM assertion failed');
    await page.close();
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
'''
                docker('exec', app, 'node', '-e', script)
            else:
                raise ValueError(f'Unknown target: {target}')
            print(f'{target}: functional smoke checks passed')
    except Exception:
        for container in containers:
            print(f'--- {container} logs ---')
            p = subprocess.run(['docker', 'logs', '--tail', '100', container], text=True, capture_output=True)
            print(p.stdout + p.stderr)
        raise
    finally:
        for container in reversed(containers):
            docker('rm', '-f', '-v', container, check=False)
        for volume in volumes:
            docker('volume', 'rm', volume, check=False)
        docker('network', 'rm', network, check=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('target', choices=['bitmappery', 'supersync', 'code-server-baked', 'iframely', 'maxun-browser'])
    p.add_argument('image')
    args = p.parse_args()
    smoke(args.target, args.image)
