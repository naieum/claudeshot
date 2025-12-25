---
description: Capture screenshots (screen, window, web pages) and analyze them
allowed-tools:
  - Bash
  - Read
argument-hint: "[mode|--web URL] [--small|--tiny] [prompt]"
---

# ClaudeShot - Screenshot Capture

Capture screenshots and analyze them in the current conversation. Supports screen capture, window capture, and **full-page web screenshots**.

**Screenshots are saved to `.claudeshots/` in the current project.**

## Quick Usage

```
/screenshot                     # Select a region
/screenshot full                # Full screen
/screenshot window              # Click a window
/screenshot --small             # Selection, resized (saves tokens)
/screenshot --tiny              # Selection, max compression
/screenshot --web http://localhost:3000   # Full-page web screenshot
/screenshot --web https://stripe.com --small  # Web screenshot, compressed
```

## Screen Capture Modes

| Command | Description |
|---------|-------------|
| `/screenshot` | Interactive region selection |
| `/screenshot window` | Click to capture a window |
| `/screenshot full` | Capture entire screen |
| `/screenshot - full` | Full screen, hide terminal |

## Web Screenshots

Capture full-page screenshots of websites (great for reviewing your work):

```
/screenshot --web http://localhost:3000         # Local dev server
/screenshot --web https://example.com           # Any URL
/screenshot --web http://localhost:3000 --small # Compressed for fewer tokens
```

**Web options:**
- `--web-width PX` - Browser width (default: 1280)
- `--web-height PX` - Viewport height (default: 800)
- `--web-viewport` - Capture only visible viewport (not full page)

## Token-Saving Options

| Flag | Width | Use Case |
|------|-------|----------|
| `--small` | 1280px | Good balance of detail and size |
| `--tiny` | 640px | Maximum token savings |
| `--resize WxH` | Custom | e.g., `--resize 800x600` |

## All Options

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/screenshot [OPTIONS] [PROMPT]
```

| Flag | Description |
|------|-------------|
| `-m, --mode MODE` | `selection` (default), `window`, `full` |
| `--small` | Resize to 1280px width |
| `--tiny` | Resize to 640px width |
| `--resize WxH` | Custom resize (e.g., `800x600`) |
| `--web URL` | Full-page web screenshot |
| `--web-width PX` | Browser width (default: 1280) |
| `--web-height PX` | Viewport height (default: 800) |
| `--web-viewport` | Capture only viewport |
| `-ht, --hide-terminal` | Minimize terminal (macOS) |
| `-d, --delay SECS` | Wait before capturing |
| `-c, --clipboard` | Copy to clipboard |
| `-o, --output PATH` | Custom output path |
| `-t, --tmp` | Save to /tmp |
| `-q, --quiet` | Output only file path |
| `-l, --list` | List screenshots |
| `--open` | Open .claudeshots folder |
| `--clear` | Clear session screenshots |

## Programmatic Examples

```bash
# Full screen, compressed for token efficiency
${CLAUDE_PLUGIN_ROOT}/scripts/screenshot -m full --small -q

# Web screenshot of local dev server
${CLAUDE_PLUGIN_ROOT}/scripts/screenshot --web http://localhost:3000 --small -q

# Capture with context
${CLAUDE_PLUGIN_ROOT}/scripts/screenshot --web http://localhost:3000 -q "check if navbar matches design"

# Compare to reference site
${CLAUDE_PLUGIN_ROOT}/scripts/screenshot --web https://stripe.com --small -q "reference design"
```

## Instructions for Claude

**When invoked via `/screenshot [args]`:**

1. Parse arguments:
   - `--web URL` → Web screenshot mode
   - `--small` → Add resize flag
   - `--tiny` → Add resize flag
   - `clear` → Run `${CLAUDE_PLUGIN_ROOT}/scripts/screenshot --clear`
   - `list` → Run `${CLAUDE_PLUGIN_ROOT}/scripts/screenshot -l`
   - `window` → `-m window`
   - `full` → `-m full`
   - `-` → `-ht`
   - Default → `-m selection`

2. Run the command with `-q` for quiet output:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/scripts/screenshot [options] -q ["prompt"]
   ```

3. Read output: Line 1 = path, Line 2 = prompt (if any)

4. Use Read tool to view the screenshot

5. If a prompt was provided, address that specific request

**Workflow Example - Building a Website:**
1. User: "make a landing page like stripe.com"
2. Screenshot stripe.com for reference: `--web https://stripe.com --small -q`
3. Build the page
4. Screenshot the result: `--web http://localhost:3000 --small -q`
5. Compare and iterate

## Defaults Configuration

Create `.claudeshot.conf` in project root:
```bash
# Always compress screenshots
RESIZE="1280"

# Web defaults
WEB_WIDTH=1440
```

Arguments: $ARGUMENTS
