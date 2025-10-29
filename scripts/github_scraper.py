#!/usr/bin/env python3
"""
Github-run scraper for JobList365 (jiblist.github.io)

Reads:  data/JobList365_data.csv
Writes: data/JobList365_data_updated.csv   <-- DOES NOT overwrite original master

Output columns (exact order):
companyName, CompanyStatecode, companyindustrialclassication, website, Roles, Linkedin
"""

import os
import re
import time
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

# ---------- CONFIG ----------
INPUT_PATH = "data/JobList365_data.csv"
OUTPUT_PATH = "data/JobList365_data_updated.csv"
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY", "")
LIMIT = 1000                # process at most this many rows (set None to process all)
MAX_WORKERS = 20            # threads
SAVE_EVERY = 100            # autosave after this many processed
REQUEST_TIMEOUT = 15
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobList365Bot/1.0)"}
# ----------------------------

if not SCRAPERAPI_KEY:
    raise SystemExit("ERROR: SCRAPERAPI_KEY not found in environment. Add to GitHub Secrets.")

def scraperapi_get(url):
    """Fetch a given URL via ScraperAPI (returns text or empty)."""
    api = "http://api.scraperapi.com"
    params = {"api_key": SCRAPERAPI_KEY, "url": url, "render": "false", "country_code": "in"}
    try:
        r = requests.get(api, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return ""

def pick_official_site_from_search_html(html):
    """Extract most-likely official site from Google search HTML returned by ScraperAPI."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    # Google often returns /url?q= link structure in search result anchors
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # pattern: /url?q=https://example.com/&sa=...
        if href.startswith("/url?q="):
            m = re.search(r"/url\?q=(https?://[^&]+)", href)
            if m:
                candidates.append(m.group(1))
        elif href.startswith("http"):
            candidates.append(href)
    bad = ("linkedin.com", "facebook.com", "youtube.com", "twitter.com", "instagram.com", "justdial", "indiamart", "tradeindia")
    for c in candidates:
        cl = c.lower()
        if any(b in cl for b in bad):
            continue
        return c.split("&")[0]
    # fallback
    return candidates[0].split("&")[0] if candidates else ""

def google_search_company_site(company):
    q = quote_plus(f"{company} official website")
    url = f"https://www.google.com/search?q={q}"
    html = scraperapi_get(url)
    return pick_official_site_from_search_html(html)

def google_search_linkedin(company):
    q = quote_plus(f"site:linkedin.com/company {company}")
    url = f"https://www.google.com/search?q={q}"
    html = scraperapi_get(url)
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    # look for linkedin company link in search anchors
    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = re.search(r"/url\?q=(https?://[^&]+)", href)
        if m:
            link = m.group(1)
            if "linkedin.com/company" in link.lower():
                return link.split("&")[0]
        if href.startswith("http") and "linkedin.com/company" in href.lower():
            return href.split("&")[0]
    return ""

def extract_roles_from_linkedin(linkedin_url, company):
    """Try to find roles from LinkedIn jobs page or from LinkedIn search results."""
    roles = []
    if not linkedin_url:
        # fallback: search site:linkedin.com/jobs <company>
        q = quote_plus(f"site:linkedin.com/jobs {company}")
        url = f"https://www.google.com/search?q={q}"
        html = scraperapi_get(url)
        if not html:
            return roles
        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        roles += find_role_terms_in_text(text)
        return list(dict.fromkeys(roles))[:20]

    # try LinkedIn jobs page patterns
    try_urls = []
    ln = linkedin_url.rstrip("/")
    try_urls.append(ln + "/jobs")
    try_urls.append(ln + "/jobs/")
    # also search Google for site:linkedin.com/jobs company-name
    q = quote_plus(f"site:linkedin.com/jobs {company}")
    try_urls_html = scraperapi_get(f"https://www.google.com/search?q={q}")
    # parse possible job links from search HTML
    if try_urls_html:
        soup = BeautifulSoup(try_urls_html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            m = re.search(r"/url\?q=(https?://[^&]+)", href)
            if m:
                link = m.group(1)
                if "linkedin.com/jobs" in link.lower() or "linkedin.com/company" in link.lower():
                    try_urls.append(link.split("&")[0])

    seen = set()
    for url in try_urls:
        if not url or url in seen:
            continue
        seen.add(url)
        html = scraperapi_get(url)
        if not html:
            continue
        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        found = find_role_terms_in_text(text)
        for f in found:
            if f not in roles:
                roles.append(f)
        if roles:
            break
    return roles[:20]

def find_role_terms_in_text(text):
    """Return candidate role strings by regex/heuristic from search/snippet text."""
    roles = []
    # basic role keywords (expandable)
    pattern = r"\b(software engineer|senior software engineer|developer|data scientist|data engineer|analyst|manager|consultant|associate|officer|executive|qa engineer|test engineer|project manager|nurse|doctor|medical coder|claims analyst|revenue cycle|receptionist|sales executive|marketing manager)\b"
    found = re.findall(pattern, text, flags=re.IGNORECASE)
    for f in found:
        candidate = f.title()
        if candidate not in roles:
            roles.append(candidate)
        if len(roles) >= 20:
            break
    return roles

def worker(i, company):
    result = {"index": i, "companyName": company, "website": "", "Linkedin": "", "Roles": ""}
    try:
        site = google_search_company_site(company)
        if site:
            result["website"] = site
        lnk = google_search_linkedin(company)
        if lnk:
            result["Linkedin"] = lnk
        if result["Linkedin"]:
            roles = extract_roles_from_linkedin(result["Linkedin"], company)
            if roles:
                result["Roles"] = ", ".join(roles)
        # fallback: if no LinkedIn roles, try extracting from company site search snippets
        if not result["Roles"]:
            # search "<company> jobs" snippets
            q = quote_plus(f"{company} jobs")
            html = scraperapi_get(f"https://www.google.com/search?q={q}")
            if html:
                text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
                found = find_role_terms_in_text(text)
                if found:
                    result["Roles"] = ", ".join(found[:20])
    except Exception:
        pass
    return result

def main():
    if not os.path.exists(INPUT_PATH):
        raise SystemExit(f"Input file missing: {INPUT_PATH}")
    df = pd.read_csv(INPUT_PATH, dtype=str)
    # ensure columns exist (original master columns)
    expected_cols = ["companyName", "CompanyStatecode", "companyindustrialclassication"]
    for c in expected_cols:
        if c not in df.columns:
            raise SystemExit(f"Input CSV missing expected column: {c}")

    n_total = len(df)
    n = LIMIT if (LIMIT and LIMIT <= n_total) else n_total
    print(f"Loaded {n_total} rows. Processing first {n} rows.")

    # create out dataframe copy to preserve master and append empty target cols
    out_df = df.copy()
    if "website" not in out_df.columns:
        out_df["website"] = ""
    if "Roles" not in out_df.columns:
        out_df["Roles"] = ""
    if "Linkedin" not in out_df.columns:
        out_df["Linkedin"] = ""

    indices = list(range(n))
    processed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = {exe.submit(worker, i, str(out_df.at[i, "companyName"])): i for i in indices}
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                res = fut.result()
                if res:
                    out_df.at[i, "website"] = res.get("website","") or out_df.at[i,"website"]
                    out_df.at[i, "Linkedin"] = res.get("Linkedin","") or out_df.at[i,"Linkedin"]
                    out_df.at[i, "Roles"] = res.get("Roles","") or out_df.at[i,"Roles"]
                    processed += 1
            except Exception:
                pass

            # occasional autosave
            if processed and processed % SAVE_EVERY == 0:
                out_df.to_csv(OUTPUT_PATH, index=False)
                print(f"Auto-saved progress: {processed} processed -> {OUTPUT_PATH}")

    # final save - enforce exact column order required by you
    final_cols = ["companyName", "CompanyStatecode", "companyindustrialclassication", "website", "Roles", "Linkedin"]
    # ensure columns exist, create empties if needed
    for c in final_cols:
        if c not in out_df.columns:
            out_df[c] = ""
    out_df = out_df[final_cols]
    out_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Done. Processed: {processed}. Output saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
