#!/usr/bin/env bash

set -e  # Exit immediately if a command exits with a non-zero status

# Install Pipenv if it's not already installed
pip install pipenv

# Install dependencies from Pipfile
pipenv install --dev


echo "Using database: $DATABASE_URL"

# Run database migrations
echo "Running database migrations..."
pipenv run flask db upgrade

# Check if migrations were successful
if [ $? -ne 0 ]; then
    echo "Migrations failed!"
    exit 1
fi

# Seed database
echo "Seeding database..."
pipenv run python seed.py

# Check if seeding was successful
if [ $? -ne 0 ]; then
    echo "Seeding failed!"
    exit 1
fi

echo "Build completed successfully."
