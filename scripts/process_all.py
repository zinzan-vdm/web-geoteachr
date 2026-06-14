#!/usr/bin/env python3
"""
Process all Geometas countries and add facts to facts.json.
Run as background with: python3 scripts/process_all.py
Outputs: /tmp/all_facts.json (intermediate), then merges into facts.json
"""
import json, sys, os, subprocess, glob, time, re

REGIONS = {
    "western-europe": [
        ("Andorra", "andorra"), ("Austria", "austria"), ("Belgium", "belgium"),
        ("France", "france"), ("Germany", "germany"), ("Greece", "greece"),
        ("Ireland", "ireland"), ("Isle of Man", "isle_of_man"), ("Italy", "italy"),
        ("Luxembourg", "luxembourg"), ("Malta", "malta"), ("Monaco", "monaco"),
        ("Netherlands", "netherlands"), ("Portugal", "portugal"), ("Spain", "spain"),
        ("Switzerland", "switzerland"), ("United Kingdom", "united_kingdom"),
    ],
    "eastern-europe": [
        ("Albania", "albania"), ("Bulgaria", "bulgaria"), ("Croatia", "croatia"),
        ("Czech Republic", "czech_republic"), ("Hungary", "hungary"),
        ("Montenegro", "montenegro"), ("North Macedonia", "north_macedonia"),
        ("Poland", "poland"), ("Romania", "romania"), ("Russia", "russia"),
        ("Serbia", "serbia"), ("Slovakia", "slovakia"), ("Slovenia", "slovenia"),
        ("Ukraine", "ukraine"),
    ],
    "nordics": [
        ("Denmark", "denmark"), ("Faroe Islands", "faroe_islands"),
        ("Finland", "finland"), ("Greenland", "greenland"),
        ("Iceland", "iceland"), ("Norway", "norway"), ("Sweden", "sweden"),
    ],
    "baltics": [
        ("Estonia", "estonia"), ("Latvia", "latvia"), ("Lithuania", "lithuania"),
    ],
    "latin-america": [
        ("Argentina", "argentina"), ("Bolivia", "bolivia"), ("Brazil", "brazil"),
        ("Chile", "chile"), ("Colombia", "colombia"), ("Costa Rica", "costa_rica"),
        ("Dominican Republic", "dominican_republic"), ("Ecuador", "ecuador"),
        ("Guatemala", "guatemala"), ("Mexico", "mexico"), ("Panama", "panama"),
        ("Peru", "peru"), ("Puerto Rico", "puerto_rico"),
        ("U.S. Virgin Islands", "us_virgin_islands"), ("Uruguay", "uruguay"),
    ],
    "north-america": [
        ("Bermuda", "bermuda"), ("Canada", "canada"),
        ("United States of America", "united_states_of_america"),
    ],
    "south-southeast-asia": [
        ("Bangladesh", "bangladesh"), ("Bhutan", "bhutan"),
        ("Cambodia", "cambodia"), ("Christmas Island", "christmas_island"),
        ("India", "india"), ("Indonesia", "indonesia"), ("Laos", "laos"),
        ("Malaysia", "malaysia"), ("Pakistan", "pakistan"),
        ("Philippines", "philippines"), ("Singapore", "singapore"),
        ("Sri Lanka", "sri_lanka"), ("Thailand", "thailand"), ("Vietnam", "vietnam"),
    ],
    "rest-of-asia": [
        ("China", "china"), ("Hong Kong", "hong_kong"), ("Japan", "japan"),
        ("Kyrgyzstan", "kyrgyzstan"), ("Mongolia", "mongolia"),
        ("South Korea", "south_korea"), ("Taiwan", "taiwan"),
    ],
    "oceania": [
        ("American Samoa", "american_samoa"), ("Australia", "australia"),
        ("Guam", "guam"), ("New Zealand", "new_zealand"),
        ("Northern Mariana Islands", "northern_mariana_islands"),
        ("U.S. Minor Outlying Islands", "us_minor_outlying_islands"),
    ],
    "africa": [
        ("Botswana", "botswana"), ("Eswatini", "eswatini"), ("Ghana", "ghana"),
        ("Kenya", "kenya"), ("Lesotho", "lesotho"), ("Madagascar", "madagascar"),
        ("Nigeria", "nigeria"), ("Rwanda", "rwanda"), ("Senegal", "senegal"),
        ("South Africa", "south_africa"), ("Uganda", "uganda"),
    ],
    "middle-east": [
        ("Israel", "israel"), ("Jordan", "jordan"), ("Palestine", "palestine"),
        ("Qatar", "qatar"), ("Tunisia", "tunisia"), ("Turkey", "turkey"),
        ("United Arab Emirates", "united_arab_emirates"),
    ],
}

SCRIPT = "/opt/hermes-agents/arthur/home/web-geoteachr/scripts/scrape_country.py"
IMAGES_DIR = "/opt/hermes-agents/arthur/home/web-geoteachr/assets/fact-images"
TMP_DIR = "/tmp/geometas_scrape"

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

all_facts = []
errors = []

for region, countries in REGIONS.items():
    for country_name, slug in countries:
        outfile = os.path.join(TMP_DIR, f"{slug}.json")
        cmd = [
            sys.executable, SCRIPT,
            region, country_name, slug,
            IMAGES_DIR, outfile
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                errors.append(f"{country_name}: exit {r.returncode} - {r.stderr[:200]}")
                continue
            with open(outfile) as f:
                data = json.load(f)
            if data.get('error'):
                errors.append(f"{country_name}: {data['error']}")
            for fact in data.get('facts', []):
                # Clean up internal fields before merging
                fact.pop('source_url', None)
                fact.pop('_categories', None)
                fact.pop('_image_downloaded', None)
                fact.pop('_image_url', None)
                all_facts.append(fact)
            print(f"  ✓ {country_name} ({len(data.get('facts', []))} facts)", flush=True)
        except subprocess.TimeoutExpired:
            errors.append(f"{country_name}: timeout")
            print(f"  ✗ {country_name}: timeout", flush=True)
        except Exception as e:
            errors.append(f"{country_name}: {e}")
            print(f"  ✗ {country_name}: {e}", flush=True)

print(f"\nTotal facts scraped: {len(all_facts)}")
print(f"Errors: {len(errors)}")
if errors:
    for e in errors[:10]:
        print(f"  - {e}")

# Write intermediate output
with open('/tmp/all_geometas_facts.json', 'w') as f:
    json.dump({'facts': all_facts, 'errors': errors}, f, indent=2)
print(f"\nWritten to /tmp/all_geometas_facts.json")