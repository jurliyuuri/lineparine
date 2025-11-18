# scrape_skyliautie_final_perfect.py  ← これで本当に完璧です！
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
    for j in range(start_idx, start_idx + 30):
        if j >= len(lines):
            break
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
        text = soup.title.string.strip()
        if " - Skyliautie" in text:
            return text.split(" - Skyliautie")[0].strip()
        if " - " in text:
            return text.split(" - ")[0].strip()
    return os.path.basename(url.split("?")[0])

def get_all_individual_links(category_url: str) -> list:
    try:
        r = requests.get(category_url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/shi/" in href and href.count("/") >= 6 and not href.endswith(("/d", "/y", "/k", "/lech")):
                full_url = urljoin(BASE_URL, href)
                if "?authuser=0" not in full_url:
                    full_url += "?authuser=0"
                title = a.get_text(strip=True) or os.path.basename(href.split("?")[0])
                links.append((title, full_url))
        return links
    except:
        return []

def main():
    os.makedirs("riparline_corpus", exist_ok=True)
    os.chdir("riparline_corpus")

    all_links = []
    for cat in CATEGORIES:
        print(f"カテゴリ読み込み: {cat}")
        links = get_all_individual_links(cat)
        all_links.extend(links)
        print(f"  → {len(links)} 件発見")

    # 重複除去
    seen = set()
    unique_links = []
    for title, url in all_links:
        if url not in seen:
            seen.add(url)
            unique_links.append((title, url))

    print(f"\n総計（重複除去後）: {len(unique_links)} ページ\n")

    success = 0
    for i, (_, url) in enumerate(unique_links, 1):
        print(f"[{i:03d}/{len(unique_links)}] {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "html.parser")

            poem = extract_ban_missen_18lines(soup)

            if poem.count("\n") + 1 != 18:
                print("    → Ban missen... で始まる18行詩は見つかりませんでした")
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

            print(f"    ✅ 保存 → {filename}")
            success += 1

        except Exception as e:
            print(f"    ❌ エラー: {e}")

    print(f"\n🎉 すべて完了！合計 {success} 篇の純粋リパライン語叙事詩を保存しました！")
    print("   フォルダ: riparline_corpus")
    print("   ファイル名形式: Skyl.X-X（タイトル）.txt ← ご希望通りです！")

if __name__ == "__main__":
    main()