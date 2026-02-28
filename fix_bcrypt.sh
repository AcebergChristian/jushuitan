#!/bin/bash
# Fix bcrypt compatibility issue

cd backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Uninstall current bcrypt
pip uninstall -y bcrypt

# Install compatible version
pip install bcrypt==3.2.2

echo "Bcrypt has been downgraded to version 3.2.2 for compatibility with passlib"
