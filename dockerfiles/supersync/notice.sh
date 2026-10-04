#!/bin/sh
set -eu
if [ "${SUPERSYNC_HIDE_UPSTREAM_NOTICE:-false}" != "true" ]; then
    printf '%s\n' \
        '[community image] This SuperSync image remains available for existing users.' \
        '[community image] The original creators now publish ghcr.io/super-productivity/supersync.' \
        '[community image] Consider switching after reviewing upstream deployment and database migration instructions:' \
        '[community image] https://github.com/super-productivity/super-productivity/tree/master/packages/super-sync-server' \
        '[community image] No image, configuration, or data migration is performed by this notice.'
fi
exec "$@"
