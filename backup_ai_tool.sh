#!/bin/bash

cd ~/my-docs

# Add all changes
git add .

# Commit with timestamp
commit_message="Automated backup on $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$commit_message"

# Push to GitHub
git push
