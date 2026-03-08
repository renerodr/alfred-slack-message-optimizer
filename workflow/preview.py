#!/usr/bin/python3
import subprocess

try:
    with open("/tmp/smo_preview.txt", encoding="utf-8") as f:
        text = f.read().strip()
except FileNotFoundError:
    text = "No preview available — run an optimization first."

script = '''on run argv
    display dialog (item 1 of argv) with title "Slack Message Optimizer — Preview" buttons {"Close"} default button 1
end run
'''

subprocess.run(["osascript", "-e", script, text])
