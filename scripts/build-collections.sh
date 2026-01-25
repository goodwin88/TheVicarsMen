#!/bin/bash

# This is a robust script to build collections

set -euo pipefail  # Exit on error, undefined variable, or failed command in a pipeline

# Define functions
function log() {
    echo "[INFO] $(date +'%Y-%m-%d %H:%M:%S') - $1"
}

function cleanup() {
    log "Cleaning up..."
    # Put cleanup commands here
}

trap cleanup EXIT

log "Starting build process..."

# Build commands here

log "Build completed successfully."