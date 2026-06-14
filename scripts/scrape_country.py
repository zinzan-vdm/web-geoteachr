#!/usr/bin/env python3
"""Scrape ALL Geometas facts for a single country, download images, output JSON."""

import re, json, sys, os, subprocess, hashlib, uuid as uuid_mod

def fetch(url, timeout=30):
    try:
        r = subprocess.run(['curl', '-s', '--max-time', str(timeout), url],
                          capture_output=True, text=True, timeout=timeout+5)
        return r.stdout if r.returncode == 0 else ''
    except Exception:
        return ''

def download_image(url, dest_path):
    if os.path.exists(dest_path):
        return True
    try:
        r = subprocess.run(['curl', '-s', '-o', dest_path, '--max-time', '20', url],
                          capture_output=True, timeout=25)
        return r.returncode == 0 and os.path.getsize(dest_path) > 0
    except Exception:
        return False

def parse_facts(html, region, country_name, images_dir):
    """Extract ALL facts from country page HTML."""
    facts = []
    # Each fact is inside: <div class="py-6 -mx-4 px-4 sm:-mx-8 sm:px-8">
    blocks = re.split(r'<div class="py-6 -mx-4 px-4 sm:-mx-8 sm:px-8">', html)[1:]
    
    for block in blocks:
        # Extract image URL
        img_match = re.search(r'<img src="([^"]+)"', block)
        if not img_match:
            continue
        image_url = img_match.group(1)
        
        # Extract fact text - look for the <a> tag with the detail href containing text
        text_match = re.search(r'<a[^>]*href="/metas/detail/[^"]+/"[^>]*>([^<]+)</a>', block)
        if not text_match:
            continue
        fact_text = text_match.group(1).strip()
        
        # Extract ALL category tags (there can be multiple per fact)
        categories = re.findall(r'<span[^>]*class="[^"]*bg-stone-300[^"]*rounded-xl[^"]*"[^>]*>([^<]+)</span>', block)
        if not categories:
            categories = re.findall(r'<span[^>]*class="[^"]*rounded-xl[^"]*"[^>]*>([^<]+)</span>', block)
        
        # Generate unique filename for this image
        img_hash = hashlib.md5(image_url.encode()).hexdigest()
        img_filename = f"{img_hash[:8]}-{uuid_mod.uuid4().hex[:8]}.jpg"
        img_local_path = os.path.join(images_dir, img_filename)
        
        # Download the image
        dl_ok = download_image(image_url, img_local_path)
        
        # Build tags: region first, then categories
        tags = [region]
        for cat in categories:
            tag = cat.strip().lower().replace(' ', '-')
            tags.append(tag)
        
        fact_entry = {
            'countries': [country_name],
            'tags': tags,
            'image': f'assets/fact-images/{img_filename}' if dl_ok else '',
            'fact': fact_text,
        }
        facts.append(fact_entry)
    
    return facts

if __name__ == '__main__':
    region = sys.argv[1]
    country_name = sys.argv[2]
    country_slug = sys.argv[3]
    images_dir = sys.argv[4]
    output = sys.argv[5]
    
    url = f'https://geometas.com/metas/countries/{country_slug}/'
    html = fetch(url)
    
    if not html:
        result = {'country': country_name, 'slug': country_slug, 'facts': [], 'error': 'Failed to fetch page'}
        with open(output, 'w') as f:
            json.dump(result, f)
        sys.exit(0)
    
    facts = parse_facts(html, region, country_name, images_dir)
    result = {'country': country_name, 'slug': country_slug, 'facts': facts, 'error': None}
    
    with open(output, 'w') as f:
        json.dump(result, f)
    
    print(f"{country_name}: {len(facts)} facts", file=sys.stderr)