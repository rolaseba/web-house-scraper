#!/bin/bash
# Script to serve the documentation locally
cd "$(dirname "$0")/../docs" || exit
echo "Starting documentation server at http://localhost:8000"
python3 -m http.server 8000
