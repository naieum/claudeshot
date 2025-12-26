---
description: Capture screenshots (screen, window, web pages) and analyze them
allowed-tools:
  - Bash
  - Read
argument-hint: "[mode|--web URL] [--small|--tiny|--jpeg] [prompt]"
---

# ClaudeShot - Screenshot Capture

Capture screenshots and analyze them in the current conversation. Supports screen capture, window capture, and **full-page web screenshots**.

**Screenshots are saved to `.claudeshots/` in the current project.**

## NEVER Use Playwright Unless Explicitly Asked

**DO NOT use Playwright for screenshots. Use this tool instead.**

Playwright MCP tools (`browser_navigate`, `browser_take_screenshot`, `browser_snapshot`) should **ONLY** be used when the user explicitly says "use Playwright" or "use the browser tool".

For ANY screenshot request, use `/screenshot`:

| User says | You do |
|-----------|--------|
| "screenshot the page" | `/screenshot --web URL` |
| "check how it looks" | `/screenshot --web URL` |
| "capture the site" | `/screenshot --web URL` |
| "take a picture of..." | `/screenshot --web URL` |
| "use Playwright to screenshot" | Then use Playwright |
| "use browser tools" | Then use Playwright |

**Why this matters:**
- Playwright returns 524KB base64 blobs per screenshot
- ClaudeShot returns 45 bytes (just the file path)
- That's 99.99% less token overhead

**Only use Playwright when the user explicitly requests it OR needs:**
- Interactive testing (clicking buttons, filling forms)
- Multi-step browser automation
- Waiting for specific elements to appear

## Quick Usage

```
/screenshot                     # Select a region
/screenshot full                # Full screen
/screenshot window              # Click a window
/screenshot --small             # Selection, resized (saves tokens)
/screenshot --tiny              # Selection, max compression
/screenshot --web http://localhost:3000   # Full-page web screenshot
/screenshot --web https://stripe.com --small  # Web screenshot, compressed
/screenshot --web http://localhost:3000 --dom  # Screenshot + HTML for debugging
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

**Viewports:**
- `--mobile` - iPhone viewport (390x844)
- `--tablet` - iPad viewport (768x1024)
- `--viewport WxH` - Custom dimensions (e.g., `--viewport 375x667`)
- `--fullpage` - Capture full scrollable page (default)
- `--web-viewport` - Capture only visible area

## Token-Saving Options

| Flag | Width | Use Case |
|------|-------|----------|
| `--small` | 1280px | Good balance of detail and size |
| `--tiny` | 640px | Maximum token savings |
| `--resize WxH` | Custom | e.g., `--resize 800x600` |
| `--jpeg` | N/A | JPEG format (smaller files than PNG) |

## All Options

```bash
# Script location (use CLAUDE_PLUGIN_ROOT if set, otherwise find relative to this command file)
scripts/screenshot [OPTIONS] [PROMPT]
```

| Flag | Description |
|------|-------------|
| `-m, --mode MODE` | `selection` (default), `window`, `full` |
| `--small` | Resize to 1280px width |
| `--tiny` | Resize to 640px width |
| `--resize WxH` | Custom resize (e.g., `800x600`) |
| `--jpeg` | Save as JPEG (smaller files) |
| `--web URL` | Full-page web screenshot |
| `--mobile` | Mobile viewport (390x844) |
| `--tablet` | Tablet viewport (768x1024) |
| `--viewport WxH` | Custom viewport (e.g., 375x667) |
| `--fullpage` | Full scrollable page (default) |
| `--web-viewport` | Visible area only |
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
scripts/screenshot -m full --small -q

# Web screenshot of local dev server
scripts/screenshot --web http://localhost:3000 --small -q

# Capture with context
scripts/screenshot --web http://localhost:3000 -q "check if navbar matches design"

# Compare to reference site
scripts/screenshot --web https://stripe.com --small -q "reference design"
```

## Instructions for Claude

**CRITICAL: NEVER use Playwright for screenshots unless the user explicitly says "use Playwright" or "use browser tools".**

Any request involving screenshots, checking pages, seeing how things look, capturing sites, etc. = use `/screenshot`, NOT Playwright.

**When invoked via `/screenshot [args]`:**

**Finding the script:** The screenshot script is located at `scripts/screenshot` relative to the plugin root directory. Use the directory containing this command file's parent as the root:
- If `CLAUDE_PLUGIN_ROOT` is set: `${CLAUDE_PLUGIN_ROOT}/scripts/screenshot`
- Otherwise, use the path relative to where you found `commands/screenshot.md`

1. Parse arguments:
   - `--web URL` → Web screenshot mode (PREFERRED for web pages)
   - `--small` → Add resize flag
   - `--tiny` → Add resize flag
   - `--jpeg` → Save as JPEG (smaller files)
   - `--dom` → Capture HTML alongside screenshot (USE FOR BUG FIXING)
   - `clear` → Run with `--clear` flag
   - `list` → Run with `-l` flag
   - `window` → `-m window`
   - `full` → `-m full`
   - `-` → `-ht`
   - Default → `-m selection`

2. Run the command with `-q` for quiet output:
   ```bash
   /path/to/plugin/scripts/screenshot [options] -q ["prompt"]
   ```

3. Read output: Line 1 = path, Line 2 = prompt (if any)

4. Use Read tool to view the screenshot (and .html file if `--dom` was used)

5. If a prompt was provided, address that specific request

**IMPORTANT - Bug Fixing Workflow:**
When the user reports a bug or asks you to fix something visual, ALWAYS use `--dom`:
```bash
scripts/screenshot --web URL --dom -q
```
This captures both the screenshot AND the page HTML, so you can see the visual problem AND inspect the DOM structure to diagnose CSS/layout issues.

**Workflow Example - Building a Website:**
1. User: "make a landing page like stripe.com"
2. Screenshot stripe.com for reference: `--web https://stripe.com --small -q`
3. Build the page
4. Screenshot the result: `--web http://localhost:3000 --small -q`
5. Compare and iterate

**Workflow Example - Fixing a Bug:**
1. User: "the sidebar is overlapping the content"
2. Screenshot with DOM: `--web http://localhost:3000 --dom -q`
3. Read both the .png AND .html files
4. Diagnose the CSS issue from the HTML structure
5. Fix and screenshot again to verify

## Defaults Configuration

Create `.claudeshot.conf` in project root:
```bash
# Always compress screenshots
RESIZE="1280"

# Web defaults
WEB_WIDTH=1440
```

Arguments: $ARGUMENTS
