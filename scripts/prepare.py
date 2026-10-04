#!/usr/bin/env python3
"""Apply community build files to a disposable upstream checkout."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess


def image_revision(target, source):
    if target == 'supersync':
        # Match upstream deploy.sh's image compatibility check, which ignores
        # unrelated frontend/docs commits after the last server input change.
        paths = ['.dockerignore', '.github/workflows/supersync-docker.yml',
                 'package.json', 'package-lock.json', 'packages/shared-schema',
                 'packages/sync-core', 'packages/super-sync-server']
        revision = subprocess.check_output(['git', '-C', str(source), 'log', '-1', '--format=%H', '--', *paths], text=True).strip()
        if not revision:
            raise ValueError('Cannot determine SuperSync image input revision')
        return revision
    return subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()


def prepare(target, source, definitions):
    community = source / '.community'
    community.mkdir(exist_ok=True)
    if target in ('bitmappery', 'code-server-baked'):
        shutil.copyfile(definitions / 'dockerfiles' / target / 'Dockerfile', community / 'Dockerfile')
        if target == 'bitmappery':
            shutil.copyfile(definitions / 'dockerfiles' / target / 'nginx.conf', community / 'nginx.conf')
        dockerfile = community / 'Dockerfile'
    elif target == 'supersync':
        original = (source / 'packages/super-sync-server/Dockerfile').read_text()
        # Preserve upstream CMD, USER, migration defaults, and signal forwarding.
        # Fail for review if upstream introduces its own entrypoint.
        if any(line.strip().upper().startswith('ENTRYPOINT ') for line in original.splitlines()):
            raise ValueError('Upstream added ENTRYPOINT; review notice integration before building')
        shutil.copyfile(definitions / 'dockerfiles/supersync/notice.sh', community / 'notice.sh')
        dockerfile = community / 'Dockerfile'
        dockerfile.write_text(original + '\nCOPY --chmod=755 .community/notice.sh /usr/local/bin/community-notice\nENTRYPOINT ["/usr/local/bin/community-notice"]\n')
    else:
        dockerfile = source / ('browser/Dockerfile' if target == 'maxun-browser' else 'Dockerfile')
    # Upstream COPY . must never sweep in our nested checkout or Git metadata.
    ignore = source / '.dockerignore'
    existing = ignore.read_text() if ignore.exists() else ''
    exclusions = '\n.git\n_build\n**/__pycache__\n'
    if target in ('bitmappery', 'code-server-baked'):
        exclusions += 'node_modules\ndist\n'
    ignore.write_text(existing + exclusions)
    return dockerfile.resolve()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('target', choices=['bitmappery', 'supersync', 'code-server-baked', 'iframely', 'maxun-browser'])
    p.add_argument('--source', type=Path, default=Path.cwd())
    p.add_argument('--definitions', type=Path, required=True)
    a = p.parse_args()
    dockerfile = prepare(a.target, a.source.resolve(), a.definitions.resolve())
    revision = image_revision(a.target, a.source.resolve())
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f'dockerfile={dockerfile}\n')
            f.write(f'image_revision={revision}\n')
    print(dockerfile)
