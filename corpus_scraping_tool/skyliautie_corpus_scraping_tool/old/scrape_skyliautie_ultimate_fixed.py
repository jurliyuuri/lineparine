# scrape_skyliautie_ultimate_fixed.py  ← これで絶対に動きます！
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://sites.google.com/site/skyliautie/"
LIST_URL = "https://sites.google.com/site/skyliautie/shi/d"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

def sanitize_filename(title: str) -> str:
    title = title.strip().lower()
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'[^\w\-]', '', title)
    return title if title else "untitled"

def extract_exact_18_lines(soup: BeautifulSoup) -> str:
    """「Ban missen tonir l'es birleen alefis io」で始まる18行を確実に抽出"""
    full_text = soup.get_text(separator="\n")
    lines = [line.strip() for line in full_text.split("\n") if line.strip()]

    start_idx = -1
    for i, line in enumerate(lines):
        if "ban missen tonir" in line.lower() and "birleen alefis io" in line.lower():
            start_idx = i
            break
    
    if start_idx == -1:
        return ""

    # 開始行から連続して18行取得（詩は空行なしなのでそのまま18個取る）
    poem_lines = []
    for j in range(start_idx, min(start_idx + 20, len(lines))):
        line = lines[j].strip()
        if line:
            poem_lines.append(line)
        if len(poem_lines) == 18:
            break

    if len(poem_lines) == 18:
        return "\n".join(poem_lines)
    
    return ""

def get_poem_title(soup: BeautifulSoup, url: str) -> str:
    if soup.title and soup.title.string:
        text = soup.title.string
        if " - Skyliautie" in text:
            return text.split(" - Skyliautie")[0].strip()
    return os.path.basename(url.split("?")[0])

def get_all_poem_links() -> list:
    r = requests.get(LIST_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")
    
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/shi/lech/" in href and not href.endswith("/shi/lech"):
            full_url = urljoin(BASE_URL, href)
            if "?authuser=0" not in full_url:
                full_url += "?authuser=0"
            title = a.get_text(strip=True)
            if not title:
                title = os.path.basename(href.split("?")[0])
            links.append((title, full_url))
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
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "html.parser")
            
            poem = extract_exact_18_lines(soup)
            
            if poem.count("\n") + 1 != 18:
                print("    ⚠️  18行詩が見つかりませんでした")
                continue
                
            title = get_poem_title(soup, url)
            safe_title = sanitize_filename(title)
            filename = f"Skyl.X-X（{safe_title}）.txt"
            
            counter = 1
            orig_name = filename
            while os.path.exists(filename):
                filename = f"Skyl.X-X（{safe_title}_{counter}）.txt"
                counter += 1
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(poem + "\n")
            
            print(f"    ✅ 保存 → {filename}")
            success += 1
            
        except Exception as e:
            print(f"    ❌ エラー: {e}")
    
    print(f"\n🎉 完了！ {success}/{len(links)} 件の純粋な18行リパライン語詩を保存しました！")
    print("   フォルダ: riparline_corpus")

if __name__ == "__main__":
    main()