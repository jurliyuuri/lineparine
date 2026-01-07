# scrape_skyliautie_ultimate.py  ← これが最終究極版です！
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://sites.google.com/site/skyliautie/"
LIST_URL = "https://sites.google.com/site/skyliautie/shi/lech"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/义务"
}

def sanitize_filename(title: str) -> str:
    title = title.strip().lower()
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'[^\w\-]', '', title)
    return title if title else "untitled"

def extract_exact_18_lines(soup: BeautifulSoup) -> str:
    """Ban missen tonir... で始まる18行を正確に抽出"""
    full_text = soup.get_text(separator="\n")
    lines = [line.strip() for line in full_text.split("\n") if line.strip()]

    # 正確な開始行を探す（大文字小文字無視）
    start_idx = -1
    for i, line in enumerate(lines):
        if "ban missen tonir l'es birleen alefis io" in line.lower():
            start_idx = i
            break
    
    if start_idx == -1:
        return ""  # 見つからなかった

    # 開始行から連続18行を取る（空行は飛ばさない、詩は空行なしのはず）
    poem_lines = []
    idx = start_idx
    while len(poem_lines) < 18 and idx < len(lines):
        line = lines[idx].strip()
        if line:  # 空行はスキップ（念のため）
            poem_lines.append(line)
        idx += 1

    # ちょうど18行あれば採用
    if len(poem_lines) == 18:
        return "\n".join(poem_lines)
    
    return ""

def get_poem_title(soup: BeautifulSoup, url: str) -> str:
    if soup.title and soup.title.string:
        title = soup.title.string
        if " - Skyliautie" in title:
            return title.split(" - Skyliautie")[0].strip()
        if " - " in title:
            return title.split(" - ")[0].strip()
    return os.path.basename(url.split("?")[0])

def get_all_poem_links() -> list:
    r = requests.get(LIST_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")
    
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/shi/lech/" in href and href.count("/") >= 6:  # 個別ページの深さでフィルタ
            full_url = urljoin("https://sites.google.com", href)
            if "?authuser=0" not in full_url:
                full_url += "?authuser=0"
            display_title = a.get_text(strip=True)
            if not display_title:
                display_title = os.path.basename(href.split("?")[0])
            links.append((display_title, full_url))
    return links

def main():
    os.makedirs("riparline_corpus", exist_ok=True)
    os.chdir("riparline_corpus")
    
    links = get_all_poem_links()
    print(f"検出された詩ページ: {len(links)} 個\n")

    success = 0
    for i, (_, url) in enumerate(links, 1):
        print(f"[{i:02d}/{len(links)}] {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "html.parser")
            
            poem = extract_exact_