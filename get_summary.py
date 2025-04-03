import httpx
import asyncio
from datetime import datetime, time
import pytz
import pandas as pd
import argparse
import xml.etree.ElementTree as ET
from typing import List, Tuple
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
MAX_IDS_PER_REQUEST = 200
MAX_REQUESTS_PER_SECOND = 3
UPLOAD_FOLDER = "upload_data/"

# For timing restrictions based on NCBI requirements
def is_request_allowed():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    if now.weekday() >= 5:
        return True  # Saturday or Sunday
    if time(21, 0) <= now.time() or now.time() <= time(5, 0):
        return True  # Between 9 PM and 5 AM
    return False

# Search IDs by term and save into WebEnv on NCBI
async def fetch_esearch(term: str, retmax: int = 100000) -> Tuple[List[str], str, str]:
    url = f"{NCBI_BASE}/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": term,
        "retmax": retmax,
        "retmode": "json",
        "usehistory": "y"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()["esearchresult"]
        return data["idlist"], data["webenv"], data["querykey"]

# Get data by term in batches
async def fetch_efetch_batch(webenv: str, query_key: str, retstart: int) -> str:
    url = f"{NCBI_BASE}/efetch.fcgi"
    params = {
        "db": "pubmed",
        "query_key": query_key,
        "WebEnv": webenv,
        "retstart": retstart,
        "retmax": MAX_IDS_PER_REQUEST,
        "retmode": "xml"
    }
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(url, params=params)
    #     response.raise_for_status()
    #     return response.text
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.text
        except httpx.ConnectTimeout:
            print(f"Timeout on batch {retstart}, attempt {attempt + 1}/3")
            await asyncio.sleep(5)
    raise RuntimeError(f"Failed to fetch batch starting at {retstart} after 3 attempts.")

async def fetch_all_efetch(webenv: str, query_key: str, total_count: int) -> List[str]:
    xml_chunks = []
    steps = range(0, total_count, MAX_IDS_PER_REQUEST)
    for start in tqdm(steps, desc="Downloading records", unit="batch"):
        xml_data = await fetch_efetch_batch(webenv, query_key, start)
        xml_chunks.append(xml_data)
        await asyncio.sleep(1 / MAX_REQUESTS_PER_SECOND)
    return xml_chunks

def parse_pubmed_xml(xml_chunks: List[str]) -> pd.DataFrame:
    records = []
    for xml in tqdm(xml_chunks, desc="Parsing XML", unit="chunk"):
        root = ET.fromstring(xml)
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID")
            title = article.findtext(".//ArticleTitle")
            abstract = " ".join([abst.text or '' for abst in article.findall(".//AbstractText")])
            authors = [
                f"{a.findtext('ForeName', '')} {a.findtext('LastName', '')}".strip()
                for a in article.findall(".//Author")
                if a.findtext('LastName')
            ]
            author_str = ", ".join(authors)
            affiliations = [a.findtext("Affiliation") for a in article.findall(".//AffiliationInfo") if a.findtext("Affiliation")]
            affiliation_str = "; ".join(affiliations)
            journal = article.findtext(".//Journal/Title")
            pub_date = article.findtext(".//PubDate/Year") or article.findtext(".//PubDate/MedlineDate") or ''
            year = pub_date[:4] if pub_date else ''
            keywords = [k.text for k in article.findall(".//Keyword") if k.text]
            keyword_str = ", ".join(keywords)
            doi = ""
            for eid in article.findall(".//ArticleId"):
                if eid.attrib.get("IdType") == "doi":
                    doi = eid.text
            records.append({
                "PMID": pmid,
                "Title": title,
                "Abstract": abstract,
                "Authors": author_str,
                "Affiliation": affiliation_str,
                "Year": year,
                "Keywords": keyword_str,
                "Journal": journal,
                "DOI": doi
            })
    return pd.DataFrame(records)

async def main(term: str):
    if not is_request_allowed():
        print("Requests are only allowed on weekends or between 9 PM and 5 AM Eastern Time.")
        return

    ids, webenv, query_key = await fetch_esearch(term)
    total_count = len(ids)
    xml_chunks = await fetch_all_efetch(webenv, query_key, total_count)
    df = parse_pubmed_xml(xml_chunks)
    df.to_csv(f"{UPLOAD_FOLDER}/output.csv", index=False)
    print(f"Fetched {len(df)} records. Saved to output.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch PubMed records with EFetch and save to CSV.")
    parser.add_argument("--term", type=str, required=True, help="Search term for PubMed")
    args = parser.parse_args()
    asyncio.run(main(args.term))
