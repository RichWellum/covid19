#!/bin/bash
# Simple bash script to run covid19 infinitely
# Wait 1 hour between refreshes
while true; do ./covid19.py; sleep 3600; done