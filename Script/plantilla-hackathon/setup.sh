#!/bin/sh
# Lanzador: el instalador real vive en .hackathon/
exec sh "$(cd "$(dirname "$0")" && pwd)/.hackathon/setup.sh" "$@"
