#!/bin/sh

set -eu

if [ -n "${NVM_BIN:-}" ] && [ -x "${NVM_BIN}/node" ]; then
  NODE_BIN="${NVM_BIN}/node"
else
  NODE_BIN="$(command -v node)"
fi

exec "${NODE_BIN}" ./node_modules/next/dist/bin/next "$@"
