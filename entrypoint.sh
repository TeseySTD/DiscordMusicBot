#!/usr/bin/env sh
set -e

mkdir -p /app/config/cookies

if [ -f /etc/secrets/cookies.txt ]; then
  cp /etc/secrets/cookies.txt /app/config/cookies/cookies.txt
  echo "✅ Copied cookies.txt to /app/config/cookies/"
else
  echo "⚠️ /etc/secrets/cookies.txt not found, skipping copy"
fi

exec python run.py
