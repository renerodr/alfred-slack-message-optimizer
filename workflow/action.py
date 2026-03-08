#!/usr/bin/python3
import sys
import os
import json
import urllib.request
import urllib.error

TONES = {"formal", "casual", "friendly", "concise"}
EMOJI_LEVELS = {"none", "minimal", "moderate", "generous"}

raw = " ".join(sys.argv[1:]).strip()

if not raw:
    sys.exit(1)

api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key:
    print("Error: OPENAI_API_KEY not set in workflow environment variables", file=sys.stderr)
    sys.exit(1)

words = raw.split()
remaining = words[:]

tone = None
if remaining and remaining[0].lower() in TONES:
    tone = remaining[0].lower()
    remaining = remaining[1:]

emoji_override = None
if remaining and remaining[0].lower() in EMOJI_LEVELS:
    emoji_override = remaining[0].lower()
    remaining = remaining[1:]

query = " ".join(remaining).strip()

if not query:
    sys.exit(1)

emoji_usage = emoji_override or os.environ.get("EMOJI_USAGE", "minimal").strip().lower()

jira_base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
jira_prefixes = [
    p.strip() for p in os.environ.get("JIRA_TICKET_PREFIX", "").split(",") if p.strip()
]

jira_instruction = ""
if jira_base_url and jira_prefixes:
    rules = " ".join(
        f"Any ticket reference matching {prefix}-XXXX should become the bare URL {jira_base_url}/{prefix}-XXXX with no surrounding angle brackets or pipe characters."
        for prefix in jira_prefixes
    )
    jira_instruction = rules + " "

tone_instruction = ""
if tone == "formal":
    tone_instruction = "Use a professional and formal tone throughout. "
elif tone == "casual":
    tone_instruction = "Use a relaxed, casual tone as if messaging a teammate. "
elif tone == "friendly":
    tone_instruction = "Use a warm, friendly, and approachable tone. "
elif tone == "concise":
    tone_instruction = "Be as brief as possible — cut every unnecessary word. "


def notify_error(message):
    import subprocess
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "Slack Message Optimizer" subtitle "Error"'
    ])


def call_openai(api_key, messages, model="gpt-4.1-mini"):
    payload = json.dumps({"model": model, "messages": messages, "max_tokens": 1024}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


system_prompt = """\
You are an expert Slack communicator. You rewrite messages to be clear, professional, and \
well-formatted for Slack's message composer using Slack mrkdwn syntax.

SLACK MRKDWN RULES — use ONLY these, never standard Markdown:
- *bold* (single asterisk, not double)
- _italic_ (single underscore)
- ~strikethrough~
- `inline code` for function names, method names, variable names, file names, commands, and technical terms
- ```code block``` for multi-line code or terminal output
- > blockquote for quoting someone
- Bullet lists: each item on its own line starting with •  or -
- Numbered lists: each item on its own line starting with 1. 2. 3.
- Separate paragraphs with a blank line
- DO NOT use # headers — Slack does not render them
- DO NOT use **double asterisk** bold — it does not render in Slack
- DO NOT use [text](url) links — paste bare URLs instead, Slack auto-links them

FORMATTING BEHAVIOUR:
- The input is typed as one long unbroken block of text with no line breaks
- Break it into natural paragraphs wherever the topic, thought, or intent shifts — do not let a single paragraph run longer than 2-3 sentences
- Any sentence over ~20 words that contains a natural pause (e.g. "and", "but", "so", "also", "additionally") is a candidate for splitting into two sentences or a new line
- If the message mentions 2 or more items, tickets, tasks, names, or examples — put each on its own bullet line. Do not list them inline with commas in a single sentence. Always introduce a bullet list with a short lead-in sentence ending in a colon
- For short casual messages (under 20 words): keep formatting minimal, do not force structure
- Never add formatting just to look busy — only apply it where it genuinely improves readability
- Preserve all @mentions and emoji exactly as written

EMOJI USAGE: {emoji_instruction}""".format(emoji_instruction={
    "none":     "Do not add any emoji anywhere in the output.",
    "minimal":  "Add at most 1 emoji, only if it fits naturally. When in doubt, omit it.",
    "moderate": "Add 2–4 emoji where they add warmth or clarity — at the start of bullet points or to close a message.",
    "generous": "Use emoji freely throughout to match a lively Slack culture — on bullet points, section openers, and sign-offs.",
}.get(emoji_usage, "Add at most 1 emoji, only if it fits naturally."))

user_content = (
    f"Fix grammar and spelling. {tone_instruction}"
    f"{jira_instruction}"
    "Preserve the original intent. "
    "Return ONLY the rewritten message — no explanation, no preamble, no quotes.\n\n"
    f"Message:\n{query}"
)

try:
    result = call_openai(api_key, [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ])
except urllib.error.URLError as e:
    msg = "Request timed out after 30 seconds." if "timed out" in str(e.reason).lower() else str(e)[:100]
    notify_error(msg)
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    notify_error(str(e)[:100])
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

import subprocess

# Copy directly via pbcopy — bypasses Alfred's {query} substitution which URL-encodes | to %7C
subprocess.run(["pbcopy"], input=result.encode("utf-8"), check=True)

# Notify user to paste
subprocess.run([
    "osascript", "-e",
    'display notification "Optimized message copied — press ⌘V to paste into Slack" with title "Slack Message Optimizer"'
])

# Write to temp file for the preview dialog path
with open("/tmp/smo_preview.txt", "w", encoding="utf-8") as f:
    f.write(result)

print(result, end="")
sys.stdout.flush()
