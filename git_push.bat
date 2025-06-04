@echo off
cd /d "D:\Gpt engeeneir\sit8"
echo Adding all changes...
git add -A
echo Committing changes...
git commit -m "feat: major updates including enhanced backend APIs, frontend improvements, and new features - Version 2.0"
echo Pushing to GitHub...
git push origin main
echo Done!
pause 