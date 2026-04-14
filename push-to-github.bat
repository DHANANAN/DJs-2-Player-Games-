@echo off
REM Navigate to the project directory
cd /d "c:\Users\Pc\Downloads\DJs-2-Player-Games--main (1)\DJs-2-Player-Games--main"

REM Check if .git exists, if not initialize
if not exist .git (
  echo Initializing Git repository...
  git init
  git config user.email "223556219+Copilot@users.noreply.github.com"
  git config user.name "Copilot"
  echo Git repository initialized.
) else (
  echo Git repository already exists.
)

REM Add all files
echo Adding enhanced games to git...
git add *.html
git add *.py
git add *.md
git add .gitignore 2>nul

REM Check status
echo.
echo Current status:
git status

REM Commit with proper message
echo.
echo Creating commit...
git commit -m "Add 11 enhanced games with 10 difficulty levels and AI

- Phase 1: penalty-enhanced, pingpong-enhanced, airhockey-enhanced
- Phase 2: snakes-enhanced, pool-enhanced, racing-enhanced
- Phase 3: sumo-enhanced, minigolf-enhanced, sword-enhanced
- Phase 4: cricket-enhanced, basketball-enhanced
- Updated index.html with links to all enhanced games
- All games feature 10 progressive difficulty levels
- Enhanced AI scaling (0.0-1.0 difficulty)
- Particle effects and visual polish
- Client-side gameplay, zero backend dependencies

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

REM Add remote and push
echo.
echo Setting up remote repository...
git remote add origin https://github.com/DHANANAN/DJs-2-Player-Games-.git 2>nul

REM Try to push
echo.
echo Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo Complete! Repository pushed to GitHub.
pause
