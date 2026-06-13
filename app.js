// ─── State ───
let facts = [];
let countryCodes = {};

// ─── Darkmode ───
function initTheme() {
  const stored = localStorage.getItem('theme');
  const theme = stored || 'dark';
  document.documentElement.dataset.theme = theme;
  if (!stored) localStorage.setItem('theme', 'dark');
  updateThemeButton(theme);
}

function updateThemeButton(theme) {
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = theme === 'dark' ? '🌙' : '☀️';
}

function toggleTheme() {
  const current = document.documentElement.dataset.theme;
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('theme', next);
  updateThemeButton(next);
}

// ─── Get country code for flag ───
function getCountryCode(countryName) {
  return countryCodes[countryName] || '';
}

// ─── Render Cards ───
function renderFacts(filtered) {
  const container = document.getElementById('facts-container');
  container.innerHTML = '';

  if (!filtered || filtered.length === 0) {
    container.innerHTML = '<div class="empty-state">No facts match your search.</div>';
    return;
  }

  for (const fact of filtered) {
    const card = document.createElement('div');
    card.className = 'fact-card';

    // Image
    const img = document.createElement('img');
    img.className = 'fact-image';
    img.loading = 'lazy';
    if (fact.image) {
      img.src = fact.image;
      img.alt = fact.alt || '';
      img.onerror = function () {
        this.outerHTML =
          '<div class="fact-image" style="display:flex;align-items:center;justify-content:center;background:var(--badge-bg);border-radius:8px;color:var(--muted);font-size:0.85rem">No image</div>';
      };
    } else {
      img.style.display = 'none';
      const placeholder = document.createElement('div');
      placeholder.className = 'fact-image';
      placeholder.style.cssText =
        'display:flex;align-items:center;justify-content:center;background:var(--badge-bg);border-radius:8px;color:var(--muted);font-size:0.85rem';
      placeholder.textContent = 'No image';
      card.appendChild(placeholder);
    }
    if (fact.image) card.appendChild(img);

    // Content wrapper
    const content = document.createElement('div');
    content.className = 'fact-content';

    // Country badges with flags
    const badges = document.createElement('div');
    badges.className = 'country-badges';
    if (fact.countries && fact.countries.length) {
      for (const country of fact.countries) {
        const code = getCountryCode(country);

        // Flag icon outside the badge (for visibility)
        if (code) {
          const flagWrap = document.createElement('span');
          flagWrap.className = 'flag-wrap';
          const flagImg = document.createElement('img');
          flagImg.className = 'flag-icon';
          flagImg.src = `assets/flags/${code}.svg`;
          flagImg.alt = code;
          flagWrap.appendChild(flagImg);

          // Popover: larger flag preview on hover
          const popImg = document.createElement('img');
          popImg.className = 'flag-popover';
          popImg.src = `assets/flags/${code}.svg`;
          popImg.alt = code;
          popImg.loading = 'lazy';
          flagWrap.appendChild(popImg);

          badges.appendChild(flagWrap);
        }

        // Badge with country name only
        const span = document.createElement('span');
        span.className = 'badge';
        span.textContent = country;
        badges.appendChild(span);
      }
    }
    content.appendChild(badges);

    // Tags
    const tags = document.createElement('div');
    tags.className = 'tags';
    if (fact.tags && fact.tags.length) {
      for (const tag of fact.tags) {
        const span = document.createElement('span');
        span.className = 'tag';
        span.textContent = tag;
        tags.appendChild(span);
      }
    }
    content.appendChild(tags);

    // Fact text
    const textDiv = document.createElement('div');
    textDiv.className = 'fact-text';
    textDiv.innerHTML = fact.fact;
    content.appendChild(textDiv);

    card.appendChild(content);
    container.appendChild(card);
  }
}

// ─── HTML stripping ───
function getPlainText(html) {
  const div = document.createElement('div');
  div.innerHTML = html;
  return div.textContent || '';
}

// ─── Fuzzy Search ───
function scoreFact(fact, words) {
  const countries = (fact.countries || []).map(c => c.toLowerCase());
  const tags = (fact.tags || []).map(t => t.toLowerCase());
  const text = getPlainText(fact.fact).toLowerCase();

  let countryMatches = 0;
  let tagMatches = 0;
  let textMatches = 0;
  let textPositions = [];

  for (const word of words) {
    // Country match
    if (countries.some(c => c.includes(word))) {
      countryMatches++;
      continue;
    }
    // Tag match
    if (tags.some(t => t.includes(word))) {
      tagMatches++;
      continue;
    }
    // Text match
    const idx = text.indexOf(word);
    if (idx !== -1) {
      textMatches++;
      textPositions.push(idx);
    }
  }

  const total = words.length;
  const matched = countryMatches + tagMatches + textMatches;
  // Every word must match at least one field (compounding filter)
  if (matched !== total) return null;

  let tier;
  if (countryMatches > 0) tier = 0;
  else if (tagMatches > 0) tier = 1;
  else tier = 2;

  let score = matched / total;

  if (textPositions.length > 1) {
    textPositions.sort((a, b) => a - b);
    const avgGap = textPositions.reduce((sum, pos, i) => {
      if (i === 0) return sum;
      return sum + (pos - textPositions[i - 1]);
    }, 0) / (textPositions.length - 1);
    if (avgGap < 50) score += 0.2;
    else if (avgGap < 100) score += 0.1;
  }

  return { tier, score, index: fact._index };
}

// ─── Multi-filter: split on `;`, require ALL parts to match ───
function filterFacts(query) {
  if (!query || query.trim() === '') return facts;

  // Split by semicolon for multi-filter
  const parts = query.split(';').map(p => p.trim()).filter(p => p.length > 0);
  if (parts.length === 0) return facts;

  // For each part, get matching fact indices
  const matchSets = parts.map(part => {
    const words = part.toLowerCase().split(/\s+/).filter(w => w.length > 0);
    if (words.length === 0) return new Set(facts.map((_, i) => i));

    const results = [];
    for (let i = 0; i < facts.length; i++) {
      facts[i]._index = i;
      const result = scoreFact(facts[i], words);
      if (result) {
        results.push({ ...result, index: i });
      }
    }

    // Sort and return just the indices
    results.sort((a, b) => {
      if (a.tier !== b.tier) return a.tier - b.tier;
      if (b.score !== a.score) return b.score - a.score;
      return a.index - b.index;
    });

    return new Set(results.map(r => r.index));
  });

  // Intersection: facts matching ALL parts
  const intersection = new Set();
  if (matchSets.length > 0) {
    // Find the smallest set first for efficiency
    const [first, ...rest] = matchSets.sort((a, b) => a.size - b.size);
    for (const idx of first) {
      if (rest.every(s => s.has(idx))) {
        intersection.add(idx);
      }
    }
  }

  // For single part (no semicolons), use the scored sort
  if (parts.length === 1) {
    // Re-score and sort single-part queries
    const words = parts[0].toLowerCase().split(/\s+/).filter(w => w.length > 0);
    const results = [];
    for (const idx of intersection) {
      const result = scoreFact(facts[idx], words);
      if (result) results.push(result);
    }
    results.sort((a, b) => {
      if (a.tier !== b.tier) return a.tier - b.tier;
      if (b.score !== a.score) return b.score - a.score;
      return a.index - b.index;
    });
    return results.map(r => facts[r.index]);
  }

  // For multi-part queries, return in original array order
  return Array.from(intersection).sort((a, b) => a - b).map(i => facts[i]);
}

function onSearchInput() {
  const input = document.getElementById('search-input');
  const query = input ? input.value : '';
  const filtered = filterFacts(query);
  renderFacts(filtered);
}

// ─── Keyboard Shortcuts ───
function focusSearch() {
  const input = document.getElementById('search-input');
  if (input) {
    input.focus();
    input.select();
  }
}

function handleGlobalKeydown(e) {
  if (e.key === '/' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
    e.preventDefault();
    focusSearch();
    return;
  }
  if (e.key === 'Enter' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
    e.preventDefault();
    focusSearch();
    return;
  }
}

// ─── Init ───
async function init() {
  initTheme();

  const toggleBtn = document.getElementById('theme-toggle');
  if (toggleBtn) toggleBtn.addEventListener('click', toggleTheme);

  const searchInput = document.getElementById('search-input');
  if (searchInput) searchInput.addEventListener('input', onSearchInput);
  if (searchInput) searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      this.value = '';
      this.blur();
      onSearchInput();
    }
  });

  document.addEventListener('keydown', handleGlobalKeydown);

  // Fetch country codes
  try {
    const res = await fetch('country-codes.json');
    if (res.ok) countryCodes = await res.json();
  } catch (err) {
    console.warn('Failed to load country-codes.json:', err);
  }

  // Fetch facts
  try {
    const res = await fetch('facts.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    facts = await res.json();
  } catch (err) {
    console.error('Failed to load facts.json:', err);
    const container = document.getElementById('facts-container');
    if (container) {
      container.innerHTML =
        '<div class="empty-state">Failed to load facts. Please try again later.</div>';
    }
    return;
  }

  renderFacts(facts);
}

document.addEventListener('DOMContentLoaded', init);