# name=Auto Track Assigner
# Assigns every unassigned Channel Rack channel to a unique, unused Mixer track.
#
# HOW TO TRIGGER
#   Default : send MIDI CC 112 with any value > 0
#   Also    : send MIDI Note 127 with any velocity > 0
#   Or set RUN_ON_STARTUP = True to run automatically when FL Studio loads the script
#
# HOW TO SET UP A TRIGGER (if you don't have a free CC on a controller)
#   1. In FL Studio: Options > MIDI settings > enable a virtual MIDI port
#   2. Use any MIDI utility (e.g. BOME, LoopMIDI + a DAW track) to fire CC 112
#   — OR just set RUN_ON_STARTUP = True and reload the script whenever you want it to run

import channels
import ui

from midi import *

# ── Configuration ─────────────────────────────────────────────────────────────
TRIGGER_CC      = 112   # CC number that fires assignment  (send any value > 0)
TRIGGER_NOTE    = 127   # Note number that fires assignment (send any velocity > 0)
RUN_ON_STARTUP  = True  # True = auto-run the moment FL Studio loads this script
MAX_MIXER_TRACK = 125   # FL Studio supports mixer tracks 1–125
# ─────────────────────────────────────────────────────────────────────────────


def OnInit():
    print("Auto Track Assigner: ready.  CC " + str(TRIGGER_CC) +
          " or Note " + str(TRIGGER_NOTE) + " to assign.")
    ui.setHintMsg("Auto Track Assigner: send CC " + str(TRIGGER_CC) + " to assign tracks")
    if RUN_ON_STARTUP:
        _autoAssign()


def OnMidiMsg(event):
    triggered = False

    # CC trigger (any MIDI channel)
    if event.midiId == 0xB0 and event.data1 == TRIGGER_CC and event.data2 > 0:
        triggered = True
    # Note-on trigger (any MIDI channel)
    elif event.midiId == 0x90 and event.data1 == TRIGGER_NOTE and event.data2 > 0:
        triggered = True

    if triggered:
        event.handled = True  # prevent the note/CC from leaking into the project
        _autoAssign()


def _autoAssign():
    count = channels.channelCount()

    # ── Pass 1: collect every mixer track already in use ────────────────────
    used = set()
    for i in range(count):
        t = channels.getTargetFXTrack(i)
        if t > 0:           # 0 = Master = unassigned
            used.add(t)

    # ── Pass 2: assign each unassigned channel to the next free slot ─────────
    nextSlot = 1
    assigned = 0
    skipped  = 0

    for i in range(count):
        if channels.getTargetFXTrack(i) != 0:
            continue        # already assigned — leave it alone

        # Advance past any already-used slots
        while nextSlot in used:
            nextSlot += 1

        if nextSlot > MAX_MIXER_TRACK:
            skipped += 1
            continue        # mixer is full

        channels.setTargetFXTrack(i, nextSlot)

        # Verify the write actually took (API is writable in FL Studio 20.8+)
        if channels.getTargetFXTrack(i) == nextSlot:
            used.add(nextSlot)
            assigned += 1
        else:
            # setTargetFXTrack is read-only in this FL Studio version — stop early
            _hint("Error: setTargetFXTrack is read-only in this FL version", error=True)
            return

    # ── Report ───────────────────────────────────────────────────────────────
    if assigned == 0 and skipped == 0:
        _hint("No unassigned channels found")
    elif skipped > 0:
        _hint("Assigned " + str(assigned) + " channel(s); " +
              str(skipped) + " skipped — mixer is full")
    else:
        _hint("Assigned " + str(assigned) + " channel(s) to unique mixer tracks")


def _hint(msg, error=False):
    prefix = "Auto Track Assigner: "
    ui.setHintMsg(prefix + msg)
    print(prefix + msg)
