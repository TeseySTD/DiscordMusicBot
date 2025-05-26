#!/usr/bin/env sh
set -e

mkdir -p /config/cookies

if [ -f /etc/secrets/cookies.txt ]; then
  cp /etc/secrets/cookies.txt /config/cookies/cookies.txt
  echo "✅ Copied cookies.txt to /config/cookies/"
else
  echo "⚠️ /etc/secrets/cookies.txt not found, skipping copy"
fi

exec python run.py
