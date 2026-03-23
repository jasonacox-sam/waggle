#!/usr/bin/env bash
# waggle-mail setup
set -euo pipefail

echo "Installing waggle-mail..."
pip install "waggle-mail[rich]" --quiet

echo ""
echo "✅ waggle installed!"
echo ""
echo "Now add your SMTP credentials to ~/.openclaw/openclaw.json:"
echo '  { "skills": { "entries": { "waggle": { "env": {'
echo '    "WAGGLE_HOST": "smtp.example.com",'
echo '    "WAGGLE_PORT": "465",'
echo '    "WAGGLE_USER": "you@example.com",'
echo '    "WAGGLE_PASS": "yourpassword",'
echo '    "WAGGLE_FROM": "you@example.com",'
echo '    "WAGGLE_NAME": "Your Name"'
echo '  }}}}}'
echo ""
echo "Start a new OpenClaw session to activate the skill."
