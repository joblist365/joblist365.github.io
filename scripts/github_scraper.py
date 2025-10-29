#!/usr/bin/env python3
"""
JobList365 (joblist365.github.io)
Scraper for first 20 companies — fetches Website, LinkedIn, Roles via ScraperAPI
Output → data/JobList365_data_updated_20.csv
"""

import os
import re
import time
import random
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

# ---------- CONFIG ----------
INPUT_PATH = "JobList365_data.csv"
OUTPUT_PATH = "data/JobList365_data_updated_20.csv"
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY", "").strip()
LIMIT = 20
MAX_WORKERS = 20
SAVE_EVERY = 10
REQUEST_TIMEOUT = 20
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobList365Bot/1.0)"}
# ----------------------------

if not SCRAPERAPI_KEY:
    raise SystemExit("❌ ERROR: SCRAPERAPI_KEY not found. Add it to GitHub Secrets.")

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

def scraperapi_get(url, render=True, retries=2):
    api = "http://api.scraperapi.com"
    params = {
        "api_key": SCRAPERAPI_KEY,
        "url": url,
        "render": "true" if render else "false",
        "country_code": "in",
    }
    for _ in range(retries + 1):
        try:
            r = requests.get(api, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200 and "<html" in r.text.lower():
                return r.text
        except Exception:
            pass
        time.sleep(random.uniform(0.5, 1.2))
    return ""

def pick_site_from_html(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    bad = ("linkedin.com", "facebook.com", "twitter.com", "youtube.com", "justdial", "indiamart")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/url?q="):
            match = re.search(r"/url\?q=(https?://[^&]+)", href)
            if match:
                url = match.group(1)
                if not any(b in url.lower() for b in bad):
                    return url
    return ""

def google_search_site(company):
    q = quote_plus(f"{company} official website")
    html = scraperapi_get(f"https://www.google.com/search?q={q}")
    return pick_site_from_html(html)

def google_search_linkedin(company):
    q = quote_plus(f"site:linkedin.com/company {company}")
    html = scraperapi_get(f"https://www.google.com/search?q={q}")
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        match = re.search(r"/url\?q=(https?://[^&]+)", href)
        if match and "linkedin.com/company" in match.group(1).lower():
            return match.group(1)
    return ""

ROLE_RE = re.compile(
    r"\b(software engineer|developer|data scientist|data engineer|analyst|manager|consultant|associate|officer|executive|qa engineer|project manager|nurse|doctor|medical coder|claims analyst|revenue cycle|receptionist|sales executive|marketing manager)\b",
    re.I,
)

def extract_roles_from_text(text):
    roles = list({m.title() for m in ROLE_RE.findall(text or "")})
    return roles[:20]

def extract_roles(company, linkedin_url):
    roles = []
    if linkedin_url:
        html = scraperapi_get(linkedin_url + "/jobs")
        if html:
            roles += extract_roles_from_text(html)
    if not roles:
        q = quote_plus(f"{company} jobs")
        html = scraperapi_get(f"https://www.google.com/search?q={q}")
        roles += extract_roles_from_text(html)
    return list(dict.fromkeys(roles))[:20]

def worker(i, company):
    result = {"CompanyName": company, "Website": "", "LinkedIn": "", "Roles": ""}
    try:
        site = google_search_site(company)
        if site:
            result["Website"] = site
            print(f"✅ [{i}] Website found for {company}: {site}")
        link = google_search_linkedin(company)
        if link:
            result["LinkedIn"] = link
            print(f"✅ [{i}] LinkedIn: {link}")
        roles = extract_roles(company, link)
        if roles:
            result["Roles"] = ", ".join(roles)
            print(f"   → Roles: {result['Roles']}")
        else:
            print(f"⚠️ [{i}] No roles found for {company}")
    except Exception as e:
        print(f"❌ [{i}] Error: {e}")
    return result

def main():
    df = pd.read_csv(INPUT_PATH, dtype=str)
    for c in ["Website", "Roles", "LinkedIn"]:
        if c not in df.columns:
            df[c] = ""
    df = df.head(LIMIT)
    out = df.copy()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = {exe.submit(worker, i, str(out.at[i, 'CompanyName'])): i for i in range(len(out))}
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                res = fut.result()
                for k in ["Website", "Roles", "LinkedIn"]:
                    out.at[i, k] = res.get(k, "")
            except Exception as e:
                print(f"❌ Worker {i} failed: {e}")
            if (i + 1) % SAVE_EVERY == 0:
                out.to_csv(OUTPUT_PATH, index=False)
                print(f"💾 Auto-saved {i+1}/{len(out)}")

    out.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Done. Saved {len(out)} companies → {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
