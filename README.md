# GeoTeachr

A simple, static tool for browsing GeoGuessr country-identification tricks.

## What it is

A filterable reference of geographic tells — road lines, bollards, poles,
signs, license plates, vegetation, language, Google cars — with images and
descriptions. All data lives in `facts.json` so you can easily add your own.

## Run

```bash
cd web-geoteachr
tar c . | docker build --tag web-geoteachr -f Containerfile -
docker run -d -p 8080:80 web-geoteachr
```

Open http://localhost:8080.

## Usage

- **Search** — type to fuzzy-filter across countries, tags, and fact text.
  Results sorted by best match (words close together rank higher).
- **Multi-filter** — separate multiple queries with `;` to find facts matching
  *all* parts. E.g. `bollards; france` shows only French bollard facts.
- **Flag descriptions** — each country has a flag entry (tag: `flag`) with
  its colors. Search e.g. `flag; red, white, blue` to find countries by flag.
- **`/`** — focus search from anywhere on the page.
- **`Enter`** — focus search (when not in a text input).
- **`Escape`** — clear the current search and blur the input.
- **🌙/☀️** — toggle dark/light mode (persisted to localStorage).

## Project structure

```
index.html           — page layout
styles.css           — dark/light theme, responsive, flag badges
app.js               — search, rendering, keyboard shortcuts, multi-filter
facts.json           — all fact data + flag descriptions
country-codes.json   — ISO alpha-2 codes for country flags
assets/flags/*.svg   — country flag SVG icons (flagicons.lipis.dev)
Containerfile        — Caddy container
```

## Add facts

Edit `facts.json` — each entry needs `countries`, `tags`, `image` (or empty),
and `fact` (HTML formatting only — no Markdown. Use `<strong>bold</strong>`
instead of `**bold**`, `<em>italic</em>` instead of `*italic*`, etc.).

## Sources

Facts derived from the video *"The Best Meta for EVERY Country in GeoGuessr"*
by **Zigzag** ([watch on YouTube](https://www.youtube.com/watch?v=Lnfwp9EGsAo)).
Tags and categorization inspired by [Geometas](https://geometas.com/).
Flag icons from [flag-icons](https://flagicons.lipis.dev/) by Lipis.