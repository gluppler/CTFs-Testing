#!/bin/bash
# Writeup-derived known credentials — optional, loaded only when available.
# These are machine-specific passwords found in previous solves.
# In blackbox mode, delete or rename this file to skip writeup-derived creds.
# Source this file from pipeline.sh: [ -f "$SCRIPTS/creds-writeup.sh" ] && source "$SCRIPTS/creds-writeup.sh"

# Windows AD machine-specific creds
KNOWN_WIN_WRITEUP=(
    "trainee:trainee"        # Retro — default weak password
    "BANKING\$:banking"      # Retro — pre-created machine account
    "SA:\$Retr09009"         # Retro — service account
    "ldapreader:ppYaVcB5R"   # RetroTwo — VBA script extraction
)

# Linux machine-specific SSH creds
KNOWN_SSH_WRITEUP="sadm:7lE2PAfVHfjz4HpE boris:beautiful1 aleks:1uY3w22uc-Wr{xNHR~+E} limesvc:5W5HN4K4GCXf9E"
