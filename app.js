// ─── State ───
let facts = [];

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

    // Country badges
    const badges = document.createElement('div');
    badges.className = 'country-badges';
    if (fact.countries && fact.countries.length) {
      for (const country of fact.countries) {
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
  if (matched === 0) return null; // no match

  // Determine tier: 0=country, 1=tag, 2=text
  let tier;
  if (countryMatches > 0) tier = 0;
  else if (tagMatches > 0) tier = 1;
  else tier = 2;

  // Base score: percentage of words matched
  let score = matched / total;

  // Proximity bonus: if multiple words matched in text, reward closeness
  if (textPositions.length > 1) {
    textPositions.sort((a, b) => a - b);
    const avgGap = textPositions.reduce((sum, pos, i) => {
      if (i === 0) return sum;
      return sum + (pos - textPositions[i - 1]);
    }, 0) / (textPositions.length - 1);
    // Bonus for words within 50 chars of each other
    if (avgGap < 50) score += 0.2;
    else if (avgGap < 100) score += 0.1;
  }

  return { tier, score, index: fact._index };
}

function filterFacts(query) {
  if (!query || query.trim() === '') return facts;

  const words = query.trim().toLowerCase().split(/\s+/).filter(w => w.length > 0);
  if (words.length === 0) return facts;

  const results = [];

  for (let i = 0; i < facts.length; i++) {
    facts[i]._index = i; // track original order for stable tiebreaking
    const result = scoreFact(facts[i], words);
    if (result) results.push(result);
  }

  // Sort: tier ASC, score DESC, index ASC (stable)
  results.sort((a, b) => {
    if (a.tier !== b.tier) return a.tier - b.tier;
    if (b.score !== a.score) return b.score - a.score;
    return a.index - b.index;
  });

  return results.map(r => facts[r.index]);
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
  // '/' focuses search (prevent typing it)
  if (e.key === '/' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
    e.preventDefault();
    focusSearch();
    return;
  }
  // Enter focuses search when not already in an input
  if (e.key === 'Enter' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
    e.preventDefault();
    focusSearch();
    return;
  }
}

// ─── Init ───
async function init() {
  initTheme();

  // Theme toggle event
  const toggleBtn = document.getElementById('theme-toggle');
  if (toggleBtn) toggleBtn.addEventListener('click', toggleTheme);

  // Search input event
  const searchInput = document.getElementById('search-input');
  if (searchInput) searchInput.addEventListener('input', onSearchInput);

  // Escape in search input clears filter
  if (searchInput) searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      this.value = '';
      this.blur();
      onSearchInput();
    }
  });

  // Global keyboard shortcuts
  document.addEventListener('keydown', handleGlobalKeydown);

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

  // Initial render
  renderFacts(facts);
}

document.addEventListener('DOMContentLoaded', init);