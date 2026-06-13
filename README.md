# GeoTeachr

A simple, static tool for browsing GeoGuessr country-identification tricks.

## What it is

A filterable reference of geographic tells — road lines, bollards, poles,
signs, license plates, vegetation, sun direction — with images and descriptions.
All data lives in `facts.json` so you can easily add your own.

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
- **`/`** — focus search from anywhere on the page.
- **`Enter`** — focus search (when not in a text input).
- **`Escape`** — clear the current search and blur the input.
- **🌙/☀️** — toggle dark/light mode (persisted to localStorage).

## Project structure

```
index.html       — page layout
styles.css       — dark/light theme, responsive
app.js           — search, rendering, keyboard shortcuts
facts.json       — all fact data
Containerfile    — Caddy container
```

## Add facts

Edit `facts.json` — each entry needs `countries`, `tags`, `image` (or empty),
and `fact` (can include `<strong>`, `<em>`, etc.).