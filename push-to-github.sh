#!/bin/bash
# Git setup and push script for DJ's 2-Player Games

cd "c:\Users\Pc\Downloads\DJs-2-Player-Games--main (1)\DJs-2-Player-Games--main"

# Initialize git if needed
if [ ! -d .git ]; then
    echo "Initializing repository..."
    git init
    git config user.email "223556219+Copilot@users.noreply.github.com"
    git config user.name "Copilot"
fi

# Stage all files
echo "Staging files..."
git add index.html
git add *-enhanced.html
git add *.md
git add README.md 2>/dev/null

# Status
echo ""
echo "Repository status:"
git status

# Commit
echo ""
echo "Creating commit..."
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

# Setup remote and push
echo ""
echo "Setting up GitHub remote..."
git remote add origin https://github.com/DHANANAN/DJs-2-Player-Games-.git 2>/dev/null || git remote set-url origin https://github.com/DHANANAN/DJs-2-Player-Games-.git

echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Complete! Repository pushed to GitHub."
