#!/usr/bin/env python3
"""
Github-run scraper for JobList365 (joblist365.github.io)

Reads:  data/JobList365_data.csv
Writes: data/JobList365_data_updated.csv   <-- safe incremental update

Columns:
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
INPUT_PATH = "JobList365_data.csv"
OUTPUT_PATH = "data/JobList365_data_updated.csv"
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY", "")
LIMIT = 1000                # process at most this many rows per run
MAX_WORKERS = 20            # threads
SAVE_EVERY = 100            # autosave after this many processed
REQUEST_TIMEOUT = 15
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobList365Bot/1.0)"}
# ----------------------------

if not SCRAPERAPI_KEY:
    raise SystemExit("❌ ERROR: SCRAPERAPI_KEY not found. Add it to GitHub Secrets.")

# ---------- HELPERS ----------
def scraperapi_get(url):
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
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
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
    return candidates[0].split("&")[0] if candidates else ""

def google_search_company_site(company):
    q = quote_plus(f"{company} official website")
    html = scraperapi_get(f"https://www.google.com/search?q={q}")
    return pick_official_site_from_search_html(html)

def google_search_linkedin(company):
    q = quote_plus(f"site:linkedin.com/company {company}")
    html = scraperapi_get(f"https://www.google.com/search?q={q}")
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
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

def find_role_terms_in_text(text):
    pattern = r"\b(software engineer|developer|data scientist|data engineer|analyst|manager|consultant|associate|officer|executive|qa engineer|project manager|nurse|doctor|medical coder|claims analyst|revenue cycle|receptionist|sales executive|marketing manager)\b"
    found = re.findall(pattern, text, flags=re.IGNORECASE)
    roles = []
    for f in found:
        role = f.title()
        if role not in roles:
            roles.append(role)
        if len(roles) >= 20:
            break
    return roles

def extract_roles_from_linkedin(linkedin_url, company):
    roles = []
    if not linkedin_url:
        q = quote_plus(f"site:linkedin.com/jobs {company}")
        html = scraperapi_get(f"https://www.google.com/search?q={q}")
        if not html:
            return roles
        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        return find_role_terms_in_text(text)
    ln = linkedin_url.rstrip("/")
    possible_urls = [ln + "/jobs", ln + "/jobs/"]
    for url in possible_urls:
        html = scraperapi_get(url)
        if not html:
            continue
        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        found = find_role_terms_in_text(text)
        if found:
            return found
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
        if not result["Roles"]:
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

# ---------- MAIN ----------
def main():
    if not os.path.exists(INPUT_PATH):
        raise SystemExit(f"❌ Input file missing: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH, dtype=str)
    for col in ["website", "Roles", "Linkedin"]:
        if col not in df.columns:
            df[col] = ""

    out_df = df.copy()

    # Resume support
    if os.path.exists(OUTPUT_PATH):
        print(f"🧩 Found existing progress file: {OUTPUT_PATH}")
        old = pd.read_csv(OUTPUT_PATH, dtype=str)
        for col in ["website", "Roles", "Linkedin"]:
            if col not in old.columns:
                old[col] = ""
        out_df = out_df.merge(
            old[["companyName", "website", "Roles", "Linkedin"]],
            on="companyName", how="left", suffixes=("", "_old")
        )
        for col in ["website", "Roles", "Linkedin"]:
            out_df[col] = out_df[col].fillna(out_df[f"{col}_old"])
            out_df.drop(columns=[f"{col}_old"], inplace=True)
        resume_from = out_df.query("website == '' and Linkedin == ''").index.min() or 0
        completed = out_df["website"].astype(bool).sum()
        print(f"🔄 Resumed progress. Completed: {completed} entries. Resuming from row {resume_from + 1}")
    else:
        resume_from = 0
        print("🆕 Starting fresh scrape...")

    n_total = len(out_df)
    n = LIMIT if LIMIT and LIMIT <= n_total else n_total
    indices = list(range(resume_from, n))
    print(f"Processing {len(indices)} companies (threads={MAX_WORKERS})...")

    processed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = {exe.submit(worker, i, str(out_df.at[i, "companyName"])): i for i in indices}
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                res = fut.result()
                if res:
                    out_df.at[i, "website"] = res.get("website", "") or out_df.at[i, "website"]
                    out_df.at[i, "Linkedin"] = res.get("Linkedin", "") or out_df.at[i, "Linkedin"]
                    out_df.at[i, "Roles"] = res.get("Roles", "") or out_df.at[i, "Roles"]
                    processed += 1
            except Exception:
                pass
            if processed and processed % SAVE_EVERY == 0:
                out_df.to_csv(OUTPUT_PATH, index=False)
                print(f"💾 Auto-saved progress: {processed} processed")

    final_cols = ["companyName", "CompanyStatecode", "companyindustrialclassication", "website", "Roles", "Linkedin"]
    for c in final_cols:
        if c not in out_df.columns:
            out_df[c] = ""
    out_df = out_df[final_cols]
    out_df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Done. Total processed: {processed}. Output saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
