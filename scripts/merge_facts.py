#!/usr/bin/env python3
"""
Merge geometas facts into existing facts.json with smart bold formatting.
Also maps country names to match our country-codes.json.
"""
import json, re, os

# Name mapping: geometas display name -> our facts.json country name
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
    "Réunion": "Réunion",
    "Curaçao": "Curaçao",
    "U.S. Virgin Islands": "Virgin Islands (U.S.)",
}

def smart_bold(text):
    """
    Bold the most scannable/salient parts of a geo fact.
    Strategy:
    - Bold the subject/key identifier (before em dash, colon, period, or 'are'/'is'/'have')
    - If there's a short identifying phrase at the start, bold it
    - For comparison facts, bold the unique identifier
    """
    # Already has HTML? Skip
    if '<strong>' in text or '<b>' in text:
        return text
    
    # Pattern 1: "Subject — description" or "Subject - description"
    m = re.match(r'^(.+?)\s*[—–-]\s*(.*)', text)
    if m:
        subject = m.group(1).strip()
        desc = m.group(2).strip()
        return f"<strong>{subject}</strong> — {desc}"
    
    # Pattern 2: "Subject: description"
    m = re.match(r'^([^:]+):\s*(.*)', text)
    if m:
        subject = m.group(1).strip()
        desc = m.group(2).strip()
        return f"<strong>{subject}:</strong> {desc}"
    
    # Pattern 3: "Subject are/have/use/feature/is ..."
    for word in [' are ', ' have ', ' is ', ' use ', ' feature ', ' typically ']:
        idx = text.lower().find(word)
        if idx and idx < len(text) * 0.4:  # only if early in the sentence
            subject = text[:idx]
            rest = text[idx:]
            return f"<strong>{subject}</strong>{rest}"
    
    # Pattern 4: Bold the first 3-5 key words (majority of the identifying info)
    words = text.split()
    if len(words) >= 4:
        # Find a good break point - try to keep it under 60 chars
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
    # Read current facts.json (flag facts)
    facts_path = '/opt/hermes-agents/arthur/home/web-geoteachr/facts.json'
    with open(facts_path) as f:
        flag_facts = json.load(f)
    
    print(f"Current facts.json: {len(flag_facts)} flag facts")
    
    # Read scraped geometas facts
    with open('/tmp/all_geometas_facts.json') as f:
        scraped = json.load(f)
    
    raw_facts = scraped.get('facts', [])
    errors = scraped.get('errors', [])
    
    print(f"Scraped facts: {len(raw_facts)}")
    print(f"Errors: {len(errors)}")
    if errors:
        for e in errors[:10]:
            print(f"  - {e}")
    
    # Apply name mapping and bold formatting
    new_facts = []
    skipped = 0
    for fact in raw_facts:
        country = fact['countries'][0]
        mapped_country = COUNTRY_NAME_MAP.get(country, country)
        
        # Apply bold formatting
        fact['fact'] = smart_bold(fact['fact'])
        
        # Update country name
        fact['countries'] = [mapped_country]
        
        new_facts.append(fact)
    
    # Check which countries have both flag and geometas facts
    flag_countries = set()
    for f in flag_facts:
        for c in f.get('countries', []):
            flag_countries.add(c)
    
    geo_countries = set()
    for f in new_facts:
        for c in f.get('countries', []):
            geo_countries.add(c)
    
    overlap = flag_countries & geo_countries
    only_flag = flag_countries - geo_countries
    only_geo = geo_countries - flag_countries
    
    print(f"\nCountries in both: {len(overlap)}")
    print(f"Countries only in flags: {len(only_flag)}")
    print(f"Countries only in geometas: {len(only_geo)}")
    
    # Merge: flag facts first, then geometas facts
    all_facts = flag_facts + new_facts
    
    print(f"\nTotal facts after merge: {len(all_facts)}")
    
    # Write updated facts.json
    with open(facts_path, 'w') as f:
        json.dump(all_facts, f, indent=2)
    
    print(f"Written to {facts_path}")
    
    # Also save a summary
    summary = {
        'flag_facts': len(flag_facts),
        'geometas_facts': len(new_facts),
        'total': len(all_facts),
        'errors': errors,
        'countries_with_geometas': sorted(list(geo_countries)),
    }
    with open('/tmp/merge_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary written to /tmp/merge_summary.json")


if __name__ == '__main__':
    main()
