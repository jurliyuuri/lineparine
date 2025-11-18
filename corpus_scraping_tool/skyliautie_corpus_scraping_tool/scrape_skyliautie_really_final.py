# scrape_skyliautie_really_final.py  ← 今度こそ本当に最終版です！！！
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://sites.google.com/site/skyliautie/"

CATEGORIES = [
    "https://sites.google.com/site/skyliautie/shi/lech",
    "https://sites.google.com/site/skyliautie/shi/d",
    "https://sites.google.com/site/skyliautie/shi/y",
    "https://sites.google.com/site/skyliautie/shi/k",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def sanitize_filename(title: str) -> str:
    title = title.strip().lower()
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'[^\w\-]', '', title)
    return title if title else "untitled"

def extract_ban_missen_18lines(soup: BeautifulSoup) -> str:
    full_text = soup.get_text(separator="\n")
    lines = [line.strip() for line in full_text.split("\n") if line.strip()]

    start_idx = -1
    for i, line in enumerate(lines):
        if re.search(r"ban\s+missen\s+tonir.*birleen.*alefis\s+io", line, re.IGNORECASE):
            start_idx = i
            break
    
    if start_idx == -1:
        return ""

    poem_lines = []
    idx = start_idx
    while len(poem_lines) < 18 and idx < len(lines):
        line = lines[idx].strip()
        if line:
            poem_lines.append(line)
        idx += 1

    if len(poem_lines) == 18:
        return "\n".join(poem_lines)
    
    return ""

def get_poem_title(soup: BeautifulSoup, url: str) -> str:
    if soup.title and soup.title.string:
        text = soup.title.string.strip()
        if " - Skyliautie" in text:
            return text.split(" - Skyliautie")[0].strip()
    return os.path.basename(url.split("?")[0])

def get_all_individual_links(category_url: str) -> list:
    """最新Google Sites対応：どんなhrefでも/shi/以下で個別ページっぽいものを全部取る"""
    try:
        r = requests.get(category_url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        links = []
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            
            # 条件を大幅に緩和（最新構造対応）
            if "/site/skyliautie/shi/" in href or href.startswith("/site/skyliautie/shi/"):
                # カテゴリトップ自体は除外
                if href.endswith(("/lech", "/d", "/y", "/k")):
                    continue
                full_url = urljoin("https://sites.google.com", href)
                if "?authuser=0" not in full_url:
                    full_url += "?authuser=0"
                    
                title = text if text else os.path.basename(href.split("?")[0])
                links.append((title, full_url))
                
        return links
    except Exception as e:
        print(f"カテゴリ読み込みエラー {category_url}: {e}")
        return []

def main():
    os.makedirs("riparline_corpus", exist_ok=True)
    os.chdir("riparline_corpus")

    all_links = []
    for cat in CATEGORIES:
        print(f"\nカテゴリ読み込み中: {cat}")
        links = get_all_individual_links(cat)
        print(f"  → {len(links)} 件の個別ページを発見！")
        all_links.extend(links)

    # 重複除去
    seen = set()
    unique_links = []
    for title, url in all_links:
        if url not in seen:
            seen.add(url)
            unique_links.append((title, url))

    print(f"\n総発見ページ数（重複除去後）: {len(unique_links)} ページ\n")

    success = 0
    for i, (_, url) in enumerate(unique_links, 1):
        print(f"[{i:03d}/{len(unique_links)}] 処理中 → {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "html.parser")

            poem = extract_ban_missen_18lines(soup)

            if poem.count("\n") + 1 != 18:
                print("    → このページにはBan missen...の18行詩は含まれていません（スキップ）")
                continue

            title = get_poem_title(soup, url)
            safe_title = sanitize_filename(title)
            filename = f"Skyl.X-X（{safe_title}）.txt"

            counter = 1
            while os.path.exists(filename):
                filename = f"Skyl.X-X（{safe_title}_{counter}）.txt"
                counter += 1

            with open(filename, "w", encoding="utf-8") as f:
                f.write(poem + "\n")

            print(f"    ✅ 保存完了 → {filename}")
            success += 1

        except Exception as e:
            print(f"    ❌ エラー: {e}")

    print(f"\n🎉🎉🎉 大成功！合計 {success} 篇の純粋リパライン語叙事詩を保存しました！")
    print("   フォルダ: riparline_corpus")
    print("   形式: Skyl.X-X（タイトル）.txt ← 完璧です！！")

if __name__ == "__main__":
    main()