#!/usr/bin/python3
import sys
import json

TONES = ["formal", "casual", "friendly", "concise"]
EMOJI_LEVELS = ["none", "minimal", "moderate", "generous"]

TONE_DESCRIPTIONS = {
    "formal":   "Professional and structured",
    "casual":   "Relaxed, like messaging a teammate",
    "friendly": "Warm and approachable",
    "concise":  "Brief — every unnecessary word cut",
}

EMOJI_DESCRIPTIONS = {
    "none":     "No emoji anywhere in the output",
    "minimal":  "At most 1 emoji, only if it fits naturally",
    "moderate": "2–4 emoji where they add warmth or clarity",
    "generous": "Emoji throughout — lively Slack culture",
}

query = " ".join(sys.argv[1:]).strip()
words = query.split()
first = words[0].lower() if words else ""

if not query:
    items = [{
        "title": "Type your message to optimize for Slack",
        "subtitle": "Prefix with a tone (formal/casual/friendly/concise) or emoji level (none/minimal/moderate/generous)",
        "valid": False,
    }]

elif first in TONES and len(words) == 1:
    items = [{
        "title": f"[{first.capitalize()}] — type your message after the tone",
        "subtitle": TONE_DESCRIPTIONS[first],
        "valid": False,
    }]

elif first in EMOJI_LEVELS and len(words) == 1:
    items = [{
        "title": f"[{first.capitalize()} emoji] — type your message after",
        "subtitle": EMOJI_DESCRIPTIONS[first],
        "valid": False,
    }]

elif first in TONES:
    # Tone prefix + message — single result
    message = " ".join(words[1:])
    items = [{
        "title": f"Optimize for Slack [{first.capitalize()}]",
        "subtitle": message,
        "arg": query,
        "valid": True,
    }]

elif first in EMOJI_LEVELS:
    # Emoji prefix + message — single result
    message = " ".join(words[1:])
    items = [{
        "title": f"Optimize for Slack [{first.capitalize()} emoji]",
        "subtitle": message,
        "arg": query,
        "valid": True,
    }]

else:
    # Plain message — show default, then emoji variants, then tone variants
    items = [
        {
            "title": "Optimize for Slack",
            "subtitle": query,
            "arg": query,
            "valid": True,
        }
    ]
    for level in EMOJI_LEVELS:
        items.append({
            "title": f"Optimize for Slack [{level.capitalize()} emoji]",
            "subtitle": EMOJI_DESCRIPTIONS[level],
            "arg": f"{level} {query}",
            "valid": True,
        })
    for tone in TONES:
        items.append({
            "title": f"Optimize for Slack [{tone.capitalize()}]",
            "subtitle": TONE_DESCRIPTIONS[tone],
            "arg": f"{tone} {query}",
            "valid": True,
        })

print(json.dumps({"items": items}))
