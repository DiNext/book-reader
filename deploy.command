#!/bin/bash
# Double-click to publish the latest story to GitHub Pages.
# Rebuilds the static snapshot from /kingdom-story, then commits & pushes it.
cd "$(dirname "$0")" || exit 1

echo "📦 Building static site from kingdom-story…"
python3 build.py || { echo "Build failed."; read -r -p "Press Enter to close."; exit 1; }

if git diff --quiet -- docs; then
  echo "✓ Nothing changed — site already up to date."
  read -r -p "Press Enter to close."
  exit 0
fi

echo "🚀 Pushing to GitHub…"
git add docs
git commit -m "Update story ($(date '+%Y-%m-%d %H:%M'))" || { echo "Commit failed."; read -r -p "Press Enter to close."; exit 1; }
git push || { echo "Push failed — is the 'origin' remote set up?"; read -r -p "Press Enter to close."; exit 1; }

echo "✅ Done. The live site will refresh in a minute or two."
read -r -p "Press Enter to close."
