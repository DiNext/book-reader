#!/bin/bash
# Double-click to launch the Kingdom Story reader.
cd "$(dirname "$0")" || exit 1
exec python3 server.py
