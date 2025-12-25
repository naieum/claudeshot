# ClaudeShot

A screenshot plugin for Claude Code. Takes screenshots of your screen or any webpage and brings them into your conversation.

I built this because I kept wanting Claude to see what I was looking at - error messages, UI bugs, designs I wanted to replicate. Now I can just `/screenshot` and it's in the conversation.

## What it does

- **Screen capture** - grab a region, window, or your whole screen
- **Web screenshots** - point it at any URL and get a full-page capture
- **Auto-resize** - shrink images to save tokens (a 217K screenshot becomes 11K)

## Example output

Desktop (1280px):

![Desktop](examples/desktop.png)

Mobile (390px):

![Mobile](examples/mobile.png)

Tablet (768px):

![Tablet](examples/tablet.png)

## Install

```bash
git clone https://github.com/naieum/claudeshot.git ~/.claude-plugins/claudeshot
claude --plugin-dir ~/.claude-plugins/claudeshot
```

Or add it permanently to your settings so it loads every session.

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

## Examples

**Replicating a design**

I wanted a landing page similar to Stripe's. Instead of describing it:

```
/screenshot --web https://stripe.com --small
```

"Build me a hero section like this but for a developer tool."

Then check my work:

```
/screenshot --web http://localhost:3000 --small
```

"The spacing on the nav feels off. Can you fix it?"

**Debugging UI issues**

Something looks wrong but it's hard to describe:

```
/screenshot
```

Select the broken area and say "This dropdown is rendering behind the modal. Why?"

Way faster than trying to explain what's happening.

**Quick feedback loop**

When iterating on a component, I'll just keep screenshotting:

```
/screenshot --web http://localhost:3000/dashboard --tiny
```

"The sidebar is too wide. Also the icons aren't aligned."

Fix, screenshot again, repeat. The `--tiny` flag keeps token usage low so you can do this all day.

**Testing mobile layouts**

Check how your site looks on phone and tablet:

```
/screenshot --web http://localhost:3000 --mobile
```

"The nav hamburger menu isn't showing. The breakpoint should kick in at this width."

```
/screenshot --web http://localhost:3000 --tablet
```

"Looks good on tablet but the cards should be 2 columns, not 3."

## All the flags

```
--small           resize to 1280px width
--tiny            resize to 640px width
--resize WxH      custom size (e.g. --resize 800x600)
--web URL         screenshot a webpage
--mobile          mobile viewport (390x844)
--tablet          tablet viewport (768x1024)
--viewport WxH    custom viewport (e.g., 375x667)
--fullpage        capture full scrollable page (default)
--web-viewport    just the visible viewport
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
