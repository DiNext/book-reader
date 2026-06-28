#!/bin/bash
# Double-click to publish the latest story to GitHub Pages.
# Rebuilds the static snapshot from /kingdom-story, commits it if changed,
# and pushes any local commits that haven't reached GitHub yet.
cd "$(dirname "$0")" || exit 1

echo "📦 Building static site from kingdom-story…"
python3 build.py || { echo "Build failed."; read -r -p "Press Enter to close."; exit 1; }

# Stage the rebuilt site and commit only if something actually changed.
git add docs
if git diff --cached --quiet; then
  echo "✓ Сборка не изменилась (новых правок в тексте нет)."
else
  git commit -m "Update story ($(date '+%Y-%m-%d %H:%M'))" \
    || { echo "Commit failed."; read -r -p "Press Enter to close."; exit 1; }
  echo "✓ Изменения закоммичены."
fi

# Push if the local branch is ahead of its upstream (handles the case where
# changes were already committed earlier but never pushed).
if ! git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
  echo "⚠️  Нет upstream-ветки. Один раз выполните:"
  echo "    git push -u origin main"
  read -r -p "Press Enter to close."
  exit 1
fi

ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null)
if [ "${ahead:-0}" -eq 0 ]; then
  echo "✅ Уже опубликовано — пушить нечего."
  read -r -p "Press Enter to close."
  exit 0
fi

echo "🚀 Отправляю $ahead коммит(ов) на GitHub…"
git push || { echo "Push failed."; read -r -p "Press Enter to close."; exit 1; }

echo "✅ Готово. Сайт обновится через минуту-другую."
read -r -p "Press Enter to close."
