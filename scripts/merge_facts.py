#!/usr/bin/env python3
"""
Merge geometas facts into existing facts.json with smart bold formatting.
Sort all facts by country name alphabetically.
"""
import json, re, os

COUNTRY_NAME_MAP = {
    "United Kingdom": "United Kingdom",
    "Czech Republic": "Czech Republic",
    "North Macedonia": "North Macedonia",
    "United States of America": "United States of America",
    "U.S. Virgin Islands": "Virgin Islands (U.S.)",
    "U.S. Minor Outlying Islands": "United States Minor Outlying Islands",
    "Palestine": "State of Palestine",
    "Hong Kong": "Hong Kong",
    "South Korea": "South Korea",
    "United Arab Emirates": "United Arab Emirates",
    "Isle of Man": "Isle of Man",
    "Christmas Island": "Christmas Island",
    "American Samoa": "American Samoa",
    "Northern Mariana Islands": "Northern Mariana Islands",
    "Faroe Islands": "Faroe Islands",
    "Greenland": "Greenland",
    "Puerto Rico": "Puerto Rico",
    "Dominican Republic": "Dominican Republic",
}

def smart_bold(text):
    if '<strong>' in text or '<b>' in text:
        return text

    # "Subject — description" or "Subject - description"
    m = re.match(r'^(.+?)\s*[—–-]\s*(.*)', text)
    if m:
        subject = m.group(1).strip()
        desc = m.group(2).strip()
        return f"<strong>{subject}</strong> — {desc}"

    # "Subject: description"
    m = re.match(r'^([^:]+):\s*(.*)', text)
    if m and m.group(1).strip() and len(m.group(1).strip()) < 60:
        subject = m.group(1).strip()
        desc = m.group(2).strip()
        return f"<strong>{subject}:</strong> {desc}"

    # "In [Country], [subject] [verb]..." → bold the subject
    m = re.match(r'^(In\s+\w+[^,]*,\s*)([^.]+)', text)
    if m:
        prefix = m.group(1)
        key_info = m.group(2).strip()
        return f"{prefix}<strong>{key_info}</strong>"

    # "[Subject] [are/have/is/use/feature/typically]..." — bold subject that starts the sentence
    for word in [' are ', ' have ', ' is ', ' use ', ' feature ', ' typically ', ' often ', ' tend ']:
        idx = text.lower().find(word)
        if idx and idx < len(text) * 0.35:
            subject = text[:idx]
            rest = text[idx:]
            return f"<strong>{subject}</strong>{rest}"

    # Bold first few key identifying words
    words = text.split()
    if len(words) >= 4:
        bold_end = 0
        char_count = 0
        for i, w in enumerate(words):
            char_count += len(w) + 1
            if char_count > 50 and i >= 2:
                bold_end = i
                break
        if bold_end == 0:
            bold_end = min(3, len(words))
        bold_part = ' '.join(words[:bold_end])
        rest = ' '.join(words[bold_end:])
        if rest:
            return f"<strong>{bold_part}</strong> {rest}"

    return f"<strong>{text}</strong>"


def main():
    facts_path = '/opt/hermes-agents/arthur/home/web-geoteachr/facts.json'

    with open(facts_path) as f:
        flag_facts = json.load(f)

    print(f"Current facts.json: {len(flag_facts)} facts (expected: flag facts only)")

    with open('/tmp/all_geometas_facts.json') as f:
        scraped = json.load(f)

    raw_facts = scraped.get('facts', [])
    errors = scraped.get('errors', [])

    print(f"Scraped facts: {len(raw_facts)}")
    print(f"Errors: {len(errors)}")
    if errors:
        for e in errors[:15]:
            print(f"  - {e}")

    # Apply name mapping, bold formatting, deduplicate tags
    new_facts = []
    for fact in raw_facts:
        country = fact['countries'][0]
        mapped = COUNTRY_NAME_MAP.get(country, country)
        fact['countries'] = [mapped]
        fact['fact'] = smart_bold(fact['fact'])
        # Deduplicate tags
        seen = set()
        unique_tags = []
        for tag in fact.get('tags', []):
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        fact['tags'] = unique_tags
        new_facts.append(fact)

    # Check per-country counts
    geo_counts = {}
    for f in new_facts:
        c = f['countries'][0]
        geo_counts[c] = geo_counts.get(c, 0) + 1
    print(f"\nCountries with geometas facts: {len(geo_counts)}")
    for c in sorted(geo_counts.keys()):
        print(f"  {c}: {geo_counts[c]} facts")

    # Merge and sort: all facts sorted by country name alphabetically
    all_facts = flag_facts + new_facts
    all_facts.sort(key=lambda f: (f['countries'][0].lower(), f.get('fact', '')))

    print(f"\nTotal facts after merge: {len(all_facts)}")
    print(f"Sorted alphabetically by country name ✓")

    with open(facts_path, 'w') as f:
        json.dump(all_facts, f, indent=2)

    print(f"Written to {facts_path}")

    summary = {
        'flag_facts': len(flag_facts),
        'geometas_facts': len(new_facts),
        'total': len(all_facts),
        'countries_with_geometas': sorted(list(geo_counts.keys())),
    }
    with open('/tmp/merge_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)


if __name__ == '__main__':
    main()
