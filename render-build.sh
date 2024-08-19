#!/usr/bin/env bash

# Install Pipenv if it's not already installed
pip install pipenv

# Install dependencies from Pipfile
pipenv install --dev

# Run database migrations
pipenv run flask db upgrade

# Seed database
pipenv run python seed.py
