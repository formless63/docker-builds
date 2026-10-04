# Build maintenance validation — 2026-10-04

Changes were validated in the current cloud checkout. No image was pushed and
no workflow was run on GitHub. Compose stacks were left unchanged.

| Target | Local AMD64 build | Functional smoke check |
| --- | --- | --- |
| BitMappery | Passed | Compiled HTML and JS assets, SPA fallback, missing asset 404, non-root web server |
| SuperSync | Passed | Fresh PostgreSQL migrations, database health endpoint, startup notice, opt-out, custom command |
| code-server-baked | Passed | HTTP startup/login, development CLI tools as abc, mounted /config writes and persistence across restart |
| iframely | Passed | Metadata extraction from a local HTTP fixture using the stable v26.10.01 source |
| Maxun browser | Blocked | Not run: fetching the Node base image failed with HTTP 503 |

Six source-selection and SuperSync compatibility tests passed. actionlint 1.7.12
validated every workflow (local ShellCheck integration was unavailable). Python
source parsing, notice shell syntax, and git diff whitespace checks passed.
The validation workflow also enables actionlint's shell checking on GitHub's
hosted runner. Native ARM64 jobs are defined but have not run in this session.

Upstream sources inspected/built:

- BitMappery: 93d5bdb9696607e72185b1003f3d160def58f3dd.
- SuperSync: ab46b6a0cf874093be7ea73960b06dac9cee8dbc.
  Its upstream-compatible image input revision is
  86f5349b314014e96157bb2792660f2810a28ea5.
- iframely v26.10.01: 965ad6dbb512605deff88874e1cb7dacdc27728d.
- Maxun develop: 1ec47a5aa8ab510c5b3141594c0059d8e6748bd3 (build blocked).

Local builds used temporary adapters outside the repository to mount the cloud
proxy CA and enable supported proxy handling, with TLS verification retained.
The local SuperSync adapter combined adjacent builder commands to fit Docker's
VFS storage driver in the 32 GB filesystem; it executed the same upstream build
commands. CI keeps the original upstream Dockerfile plus the notice wrapper.
Disposable iframely source permissions were normalized for non-root execution.
All smoke-test containers, networks, and volumes were removed after checks.

Maxun's failure was diagnosed as an environment proxy transport problem:
Docker Hub, Google's mirror, and npm requests all returned HTTP 503 with an
Envoy/Cloudflare tunnel connection failure. It needs a functioning proxy before
the local build and real WebSocket browser test can be completed. GitHub's new
validation jobs must pass before publishing release tags, including Maxun.

Repository description and topic updates were attempted for discoverability,
but GitHub rejected both with HTTP 403, Resource not accessible by integration.
They remain unchanged. Apply the proposed description and topics in README.md
through the repository's About editor if desired.
