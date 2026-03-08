# Alfred Slack Message Optimizer

An Alfred workflow that rewrites your Slack messages using OpenAI — fixing grammar, spelling, and applying proper Slack `mrkdwn` formatting — then copies the result straight to your clipboard.

## Installation

1. Double-click `dist/Slack-Message-Optimizer.alfredworkflow` to import into Alfred
2. Open the workflow in Alfred Preferences and set your **OpenAI API Key** in the workflow configuration

## Usage

Open Alfred and type your keyword (default: `smo`) followed by your message:

```
smo hey just wanted to follow up on that PR we talked about yesterday can you take a look when you get a chance
```

- **Enter** — optimize and copy to clipboard, then press `⌘V` to paste into Slack
- **⌘Enter** — preview the optimized message before copying

### Tone modifiers

Prefix your message with an optional tone keyword:

| Prefix | Effect |
|--------|--------|
| `formal` | Professional and formal tone |
| `casual` | Relaxed, teammate-style tone |
| `friendly` | Warm and approachable tone |
| `concise` | Stripped down to the essentials |

```
smo concise hey just wanted to follow up on that PR...
```

## Configuration

Configure these variables in Alfred's workflow environment:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your API key from platform.openai.com |
| `KEYWORD` | Yes | Alfred trigger keyword (default: `smo`) |
| `EMOJI_USAGE` | No | `none`, `minimal` (default), `moderate`, or `generous` |
| `JIRA_BASE_URL` | No | Base URL for Jira, e.g. `https://yourcompany.atlassian.net/browse` |
| `JIRA_TICKET_PREFIX` | No | Ticket prefixes to auto-link, e.g. `BAT,OPS,MEDIA` |

## Requirements

- [Alfred](https://www.alfredapp.com/) with Powerpack
- macOS (uses `pbcopy` and `osascript`)
- Python 3 (pre-installed on macOS)
- An OpenAI API key
