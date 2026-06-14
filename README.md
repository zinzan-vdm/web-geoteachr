# GeoTeachr

A filterable reference of GeoGuessr country-identification tells — bollards,
license plates, road markings, language scripts, Google cars, poles, signs,
vegetation, coverage, and flag colors. Static HTML/JS/CSS, no backend.

## Features

- **Keyword search** — type any terms; results filtered by country > tag > text
  matching. All words must match (AND semantics).
- **Multi-filter** — use `;` to combine independent queries. E.g. `bollards; france`
  finds facts matching *both* filter groups.
- **Flag lookup** — each country has a flag-color entry (tag: `flag`). Search
  `flag; red white blue` to find countries by flag colors.
- **Image zoom** — click any fact image to view at native resolution in a dark overlay; click or press Escape to close.
- **Dark/light theme** — toggle persisted to `localStorage`.
- **Keyboard shortcuts** — `/` or `Enter` to focus search, `Escape` to clear.

## Run

```bash
docker build --tag web-geoteachr -f Containerfile .
docker run -d -p 8080:80 web-geoteachr
```

Or serve directly with any static server:
```bash
python3 -m http.server 8080
```

👉 **Live at** [zinzan-vdm.github.io/web-geoteachr](https://zinzan-vdm.github.io/web-geoteachr/)

## Data

| Category | Count |
|----------|-------|
| Flag facts (colors) | 251 |
| Geo identification facts | 568 |
| Domain name extensions (ccTLDs) | 267 |
| **Total** | **1,086** |
| Country flag SVGs | 249 |
| Fact images | 581 |

### Usefulness Scoring

Each fact includes a `usefulness` score (0–10) to help prioritize the most definitive tells:

| Score | Count | What |
|-------|-------|------|
| 10 | 251 | Flag colors — the most definitive identifier |
| 9 | 13 | Undisputed geo tells |
| 8 | 296 | Domain extensions + strong geo consensus |
| 7 | 25 | Solid, reasonably confident |
| 6 | 5 | Useful but caveated |
| 0 | 496 | Supplementary (unscored) |

Within each country, facts are sorted by usefulness descending — highest-signal tells first.

Each geo fact includes a **region tag** (`nordics`, `south-southeast-asia`, etc.)
and one or more **category tags** (`bollards`, `street-sign`, `license-plate`,
`language`, `google-car`...). Images are stored locally in `assets/fact-images/`.

## Sources

- [Geometas](https://geometas.com/) — primary source for geo identification facts
- [Zigzag's "Best Meta for Every Country"](https://www.youtube.com/watch?v=Lnfwp9EGsAo) — community survey used for usefulness scoring of geo tells
- [flag-icons](https://flagicons.lipis.dev/) — country flag SVGs by Lipis