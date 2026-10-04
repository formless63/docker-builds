#!/usr/bin/env python3
"""Resolve mutable upstream refs once for every architecture in a workflow run."""
import argparse
import json
import os
import re
import subprocess

SOURCES = {
    'bitmappery': ('igorski/bitmappery', 'master'),
    'supersync': ('super-productivity/super-productivity', 'master'),
    'iframely': ('itteco/iframely', None),
    'maxun-browser': ('getmaxun/maxun', 'develop'),
}


def stable_tag(refs):
    tags = {}
    for line in refs.splitlines():
        sha, ref = line.split()
        name = ref.removeprefix('refs/tags/').removesuffix('^{}')
        if re.fullmatch(r'v?\d+\.\d+\.\d+', name):
            # Prefer the commit behind annotated tags rather than the tag object.
            if name not in tags or ref.endswith('^{}'):
                tags[name] = sha
    if not tags:
        raise ValueError('No stable numeric upstream release tags found')
    name = max(tags, key=lambda tag: (tuple(map(int, tag.lstrip('v').split('.'))), tag))
    return name, tags[name]


def resolve(target, owner, repository, definition_revision):
    if target == 'code-server-baked':
        repo, sha, version = repository, definition_revision, ''
    else:
        repo, branch = SOURCES[target]
        url = f'https://github.com/{repo}.git'
        if branch is None:
            refs = subprocess.check_output(['git', 'ls-remote', '--tags', url], text=True)
            version, sha = stable_tag(refs)
        else:
            refs = subprocess.check_output(['git', 'ls-remote', '--exit-code', url, f'refs/heads/{branch}'], text=True)
            sha = refs.split()[0]
            version = branch if target == 'maxun-browser' else ''
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Upstream did not resolve to a full commit SHA')
    image = f'ghcr.io/{repository.lower()}/maxun-browser' if target == 'maxun-browser' else f'ghcr.io/{owner.lower()}/{target}'
    architectures = [{'arch': 'amd64', 'runner': 'ubuntu-latest'}]
    if target != 'maxun-browser':
        architectures.append({'arch': 'arm64', 'runner': 'ubuntu-24.04-arm'})
    return dict(repository=repo, revision=sha, short=sha[:7], version=version,
                image=image, matrix=json.dumps({'include': architectures}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('target', choices=[*SOURCES, 'code-server-baked'])
    p.add_argument('--owner', required=True)
    p.add_argument('--repository', required=True)
    p.add_argument('--definition-revision', required=True)
    args = p.parse_args()
    values = resolve(args.target, args.owner, args.repository, args.definition_revision)
    output = '\n'.join(f'{key}={value}' for key, value in values.items()) + '\n'
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(output)
    else:
        print(output, end='')
