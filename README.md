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
| Geo identification facts | 556 |
| Domain name extensions (ccTLDs) | 267 |
| **Total** | **1,074** |
| Country flag SVGs | 249 |
| Fact images | 556 |

Each geo fact includes a **region tag** (`nordics`, `south-southeast-asia`, etc.)
and one or more **category tags** (`bollards`, `street-sign`, `license-plate`,
`language`, `google-car`...). Images are stored locally in `assets/fact-images/`.

## Sources

- [Geometas](https://geometas.com/) — primary source for geo identification facts
- [flag-icons](https://flagicons.lipis.dev/) — country flag SVGs by Lipis