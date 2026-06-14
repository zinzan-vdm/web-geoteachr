#!/usr/bin/env python3
"""Scrape Geometas facts for a single country, download image, output JSON fact."""

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
        return True  # already exists
    try:
        r = subprocess.run(['curl', '-s', '-o', dest_path, '--max-time', '20', url],
                          capture_output=True, timeout=25)
        return r.returncode == 0 and os.path.getsize(dest_path) > 0
    except Exception:
        return False

def parse_facts(html, region, country_name, images_dir):
    """Extract facts from country page HTML."""
    facts = []
    # Split by mb-10 divs (each fact is one)
    blocks = re.split(r'<div class="mb-10">', html)[1:]  # skip first
    
    for block in blocks:
        # Extract image URL
        img_match = re.search(r'<img src="([^"]+)"', block)
        if not img_match:
            continue
        image_url = img_match.group(1)
        
        # Extract fact text (the anchor text after the image)
        text_match = re.search(r'<a[^>]*>([^<]+)</a>\s*</div>\s*</div>\s*<div class="[^"]*">\s*<div class="flex flex-wrap[^"]*">', block)
        if not text_match:
            # Try simpler pattern
            text_match = re.search(r'<a[^>]*href="/metas/detail/[^"]+/"[^>]*>([^<]+)</a>', block)
        if not text_match:
            continue
        fact_text = text_match.group(1).strip()
        
        # Extract category tags
        categories = re.findall(r'<span[^>]*class="[^"]*bg-stone-300[^"]*"[^>]*>([^<]+)</span>', block)
        if not categories:
            # Try another pattern
            categories = re.findall(r'<span[^>]*class="[^"]*rounded-xl[^"]*"[^>]*>([^<]+)</span>', block)
        
        # Generate a unique ID for the image
        img_hash = hashlib.md5(image_url.encode()).hexdigest()
        img_filename = f"{img_hash[:8]}-{uuid_mod.uuid4().hex[:8]}.jpg"
        img_local_path = os.path.join(images_dir, img_filename)
        
        # Download the image
        dl_ok = download_image(image_url, img_local_path)
        
        # Build tags
        tags = [region]
        for cat in categories:
            tag = cat.strip().lower().replace(' ', '-')
            tags.append(tag)
        
        # Bold the first key phrase (usually the first few words before common phrases)
        # We'll do smart bolding later at assembly time
        # For now, store the raw text
        
        fact_entry = {
            'countries': [country_name],
            'tags': tags,
            'image': f'assets/fact-images/{img_filename}' if dl_ok else '',
            'fact': fact_text,
            'source_url': image_url,
            '_categories': [c.strip() for c in categories],
            '_image_downloaded': dl_ok,
            '_image_url': image_url,
        }
        facts.append(fact_entry)
    
    return facts

if __name__ == '__main__':
    import sys
    # Args: region country_name country_slug images_dir output_file
    if len(sys.argv) < 6:
        # Test mode
        region = sys.argv[1] if len(sys.argv) > 1 else 'western-europe'
        country_name = sys.argv[2] if len(sys.argv) > 2 else 'Monaco'
        country_slug = sys.argv[3] if len(sys.argv) > 3 else 'monaco'
        images_dir = sys.argv[4] if len(sys.argv) > 4 else '/opt/hermes-agents/arthur/home/web-geoteachr/assets/fact-images'
        output = sys.argv[5] if len(sys.argv) > 5 else '/dev/stdout'
    else:
        region = sys.argv[1]
        country_name = sys.argv[2]
        country_slug = sys.argv[3]
        images_dir = sys.argv[4]
        output = sys.argv[5]
    
    url = f'https://geometas.com/metas/countries/{country_slug}/'
    html = fetch(url)
    
    if not html:
        result = {'country': country_name, 'facts': [], 'error': 'Failed to fetch page'}
        with open(output, 'w') as f:
            json.dump(result, f)
        sys.exit(1)
    
    facts = parse_facts(html, region, country_name, images_dir)
    result = {'country': country_name, 'facts': facts, 'error': None}
    
    with open(output, 'w') as f:
        json.dump(result, f)
    
    print(f"{country_name}: {len(facts)} facts", file=sys.stderr)