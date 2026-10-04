# Docker builds: BitMappery, SuperSync, code-server, iframely, and Maxun

Community Docker container images for projects that needed a convenient image
or benefit from additional tooling. Builds track upstream source, retain useful
version tags, and run functional smoke checks before publishing release tags.

| Project | Image | Purpose |
| --- | --- | --- |
| [BitMappery](https://github.com/igorski/bitmappery) | `ghcr.io/formless63/bitmappery` | Pixel editor, built with its npm lockfile and served as static production assets on port **5173** by non-root nginx. |
| [SuperSync / Super Productivity](https://github.com/super-productivity/super-productivity) | `ghcr.io/formless63/supersync` | Continued community builds for existing users, using the current upstream Dockerfile plus a startup notice. |
| [code-server](https://github.com/linuxserver/docker-code-server) | `ghcr.io/formless63/code-server-baked` | LinuxServer code-server with Node, Python, PHP, Composer, database clients, and development CLI tools. |
| [iframely](https://github.com/itteco/iframely) | `ghcr.io/formless63/iframely` | Builds of the latest stable numeric upstream release, tested on native AMD64 and ARM64 runners. |
| [Maxun browser](https://github.com/getmaxun/maxun) | `ghcr.io/formless63/docker-builds/maxun-browser` | Standalone Playwright Chromium browser service from Maxun's `develop` branch. AMD64, ports **3001** (WebSocket) and **3002** (health). |

## SuperSync continuity and the upstream image

`ghcr.io/formless63/supersync` remains available. Super Productivity now also
publishes **`ghcr.io/super-productivity/supersync`**. Consider moving to the
original project's image after reviewing its
[deployment and migration instructions](https://github.com/super-productivity/super-productivity/tree/master/packages/super-sync-server).
The community startup notice is informational: it does not modify your image,
configuration, or data. Set `SUPERSYNC_HIDE_UPSTREAM_NOTICE=true` to hide it.

These builds preserve upstream's command, user, and migration defaults. Current
upstream images default to `RUN_MIGRATIONS_ON_STARTUP=false`; merely pulling a new
image and restarting may leave database migrations unapplied. Use upstream's
deployment procedure, with a backup and the correct image revision, rather than
assuming an image update migrates an existing database. The build passes
`VCS_REF` and records the last commit affecting upstream image inputs in `org.opencontainers.image.revision`
for upstream's revision checks. Never point a newer deploy script at an older
image. The smoke test runs migrations against a disposable database, not yours.

## Tags and provenance

- Existing `latest`, date (`YYYY-MM-DD`), and project-specific tags remain.
- `upstream-<seven-character SHA>` identifies upstream source. SuperSync,
  BitMappery, and iframely support AMD64 and ARM64; code-server does too.
- iframely retains its stable release tag; Maxun retains `develop` and adds date
  and upstream commit tags. Maxun remains AMD64, matching its existing image.
- code-server retains `sha-<build-definition SHA>` tags. Its source is this repo.
- `org.opencontainers.image.revision` records the upstream image revision (for
  SuperSync, the last commit affecting server image inputs, matching upstream).
  `io.github.formless63.upstream-revision` records the full checked-out commit;
  `io.github.formless63.build-revision` records the build definitions separately.
- `candidate-<run>-<attempt>-<architecture>` tags contain individually tested
  images staged for manifest assembly. A release tag is promoted only after all
  required architecture jobs pass. Candidate tags are not release channels.

Scheduled builds and relevant pushes to `main` publish. Pull requests only
validate. Manual runs default to validation; explicitly enable **publish** on
`main` to release. New runs supersede older runs for the same image and Git ref.
Source refs are resolved once, then every architecture checks out that exact
commit. Builds and smoke tests run natively, without QEMU.

Commit tags identify source, not a guarantee of byte-for-byte rebuilds: base
image tags, OS packages, and some upstream installers remain moving inputs.
Use an image digest when you need to deploy the exact tested image.

## Development and validation

The workflows use `scripts/resolve.py`, `scripts/prepare.py`, and
`scripts/smoke.py`. Stage upstream sources outside this checkout, following the
selected workflow's resolved commit. `prepare.py` copies community files into
the disposable source context; it does not require copying the entire build
repository into an image. Then build locally and test, for example:

```sh
python3 scripts/prepare.py bitmappery --source /path/to/bitmappery --definitions "$PWD"
docker build -f /path/to/bitmappery/.community/Dockerfile -t local/bitmappery /path/to/bitmappery
python3 scripts/smoke.py bitmappery local/bitmappery
python3 -m unittest discover -s tests -v
```

Smoke checks verify BitMappery's compiled assets, SuperSync migrations and
database health, code-server startup and tools as `abc` with `/config` mounted
across restart, iframely metadata extraction from a local fixture, and Maxun's
real WebSocket browser connection and page rendering. Temporary containers,
networks, and volumes are cleaned up. Docker and Python 3 are required.

code-server ships Node **24.19.0** and pinned global npm CLI versions. The Node
archive and Composer installer are checksum-verified. Installed versions are
recorded in `/usr/local/share/baked-tools/`, outside the user-mounted `/config`.

## Finding these builds on GitHub

Repository search is not limited to titles. This README names each build and its
upstream project; use `in:readme` to include README content explicitly, for
example `bitmappery in:readme user:formless63`. Repository descriptions and topics
also help discovery. Suggested topics: `docker`, `docker-images`, `ghcr`,
`bitmappery`, `supersync`, `super-productivity`, `code-server`, `iframely`, `maxun`,
and `playwright`. README changes do not automatically set repository topics or
guarantee search ranking.

Suggested repository description: **Community Docker images for BitMappery,
SuperSync / Super Productivity, code-server, iframely, and Maxun browser, with
automated builds and smoke tests.**

See [VALIDATION.md](VALIDATION.md) for checks completed during this maintenance
pass and the remaining local/CI checks.
