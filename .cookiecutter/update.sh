#!/bin/bash
set -e

PROJECT_DIR=$(pwd)/..

python update_from_repo.py

# Add post-cookiecutter commands that you always want run here:
git checkout -- $PROJECT_DIR/README.md
git checkout -- $PROJECT_DIR/AUTHORS.rst
git checkout -- $PROJECT_DIR/Pipfile
git checkout -- $PROJECT_DIR/.cookiecutter/update.sh

# Enter patch mode on remaining diffs:
git add -p
