#!/usr/bin/env bash

#run database migrations
flask db upgrade

#seed database
python seed.py