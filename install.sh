#!/usr/bin/env bash
# Copies the script into FL Studio's MIDI Hardware scripts folder
DEST="$HOME/Documents/Image-Line/FL Studio/Settings/Hardware/Auto Track Assigner"
mkdir -p "$DEST"
cp device_AutoTrackAssigner.py "$DEST/"
echo "Installed to: $DEST"
