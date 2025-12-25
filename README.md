# ClaudeShot

A screenshot plugin for Claude Code. Takes screenshots of your screen or any webpage and brings them into your conversation.

I built this because I kept wanting Claude to see what I was looking at - error messages, UI bugs, designs I wanted to replicate. Now I can just `/screenshot` and it's in the conversation.

## What it does

- **Screen capture** - grab a region, window, or your whole screen
- **Web screenshots** - point it at any URL and get a full-page capture
- **Auto-resize** - shrink images to save tokens (a 217K screenshot becomes 11K)

## Install

```bash
claude --plugin-dir /path/to/claudeshot
```

Or clone it somewhere and point to that directory.

## Usage

Basic stuff:

```
/screenshot                  # select a region
/screenshot full             # whole screen
/screenshot window           # click a window
```

Web pages:

```
/screenshot --web http://localhost:3000
/screenshot --web https://stripe.com
```

To save tokens, add `--small` (1280px) or `--tiny` (640px):

```
/screenshot full --tiny
/screenshot --web http://localhost:3000 --small
```

The `--tiny` flag cuts file size by about 95%. Still readable, way fewer tokens.

## The workflow I use

When building a UI, I'll do something like:

1. Screenshot a site I want to reference: `/screenshot --web https://stripe.com --small`
2. Ask Claude to build something similar
3. Screenshot my localhost to check the result: `/screenshot --web http://localhost:3000 --small`
4. Point out what's off, iterate

It's faster than copy-pasting descriptions of what things look like.

## All the flags

```
--small           resize to 1280px width
--tiny            resize to 640px width
--resize WxH      custom size (e.g. --resize 800x600)
--web URL         screenshot a webpage
--web-width PX    browser width (default 1280)
--web-height PX   viewport height (default 800)
--web-viewport    just the viewport, not full page
-d, --delay N     wait N seconds before capture
-c, --clipboard   copy to clipboard too
-t, --tmp         save to /tmp instead of .claudeshots
```

Management:

```
/screenshot list    # show recent screenshots
/screenshot clear   # delete session screenshots
/screenshot open    # open the folder
```

## Configuration

If you want defaults, create `.claudeshot.conf` in your project:

```bash
RESIZE="1280"
WEB_WIDTH=1440
```

## Platform support

Works on macOS, Linux, and Windows.

- macOS uses the built-in `screencapture`
- Linux uses whatever you have installed (gnome-screenshot, scrot, maim, etc.)
- Windows uses PowerShell or Snipping Tool
- Web screenshots need Chrome or Chromium installed

## Files

Screenshots go to `.claudeshots/` in your current directory. Add it to `.gitignore` if you don't want them in version control.

## License

MIT
