# scrape_skyliautie_final.py
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://sites.google.com/site/skyliautie/"
LIST_URL = "https://sites.google.com/site/skyliautie/shi/lech"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def sanitize_filename(title: str) -> str:
    title = title.strip().lower()
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'[^\w\-]', '', title)
    return title if title else "untitled"

def extract_riparline_poem(soup: BeautifulSoup) -> str:
    # 1. <pre>タグがあれば最優先（古いページ用）
    pre = soup.find("pre")
    if pre:
        text = pre.get_text()
        if any(c in "áéíóúäëïöüãõñç'’" for c in text):
            return text.strip()

    # 2. Courier New / monospace フォントのブロックを探す（現在の主流）
    candidates = []
    for elem in soup.find_all(["div", "span", "p", "pre"], style=True):
        style = elem.get("style", "").lower()
        if any(font in style for font in ["courier", "monospace", "font-family"]):
            text = elem.get_text(separator="\n").strip()
            if len(text) > 80 and any(c in "áéíóúäëïöüãõñç'" for c in text):
                candidates.append(text)

    if candidates:
        return max(candidates, key=len)  # 一番長いブロック＝詩本文

    # 3. メインコンテンツからリパライン語っぽい行だけを集める（最終手段）
    main_content = soup.find("div", role="main") or soup.find("div", class_=re.compile(r"content|main", re.I))
    if not main_content:
        main_content = soup

    lines = main_content.get_text(separator="\n").split("\n")
    poem_lines = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        # 日本語・長い英語・ナビを除外
        if re.search(r'[ぁ-んァ-ヶ一-龠]', s):
            continue
        if re.search(r'^[a-zA-Z\s\.,!?-]{20,}$', s):  # 長すぎる英語行
            continue
        if any(bad in s for bad in ["Google Sites", "Report abuse", "ホーム", "Skyliautie叙事詩"]):
            continue
        if len(s) > 5 and any(c in "áéíóúýäëïöüãõñç'’ʻʼʾ" for c in s):
            poem_lines.append(s)

    if poem_lines:
        return "\n".join(poem_lines)

    return ""  # 何も取れなかったら空文字

def get_poem_title(soup: BeautifulSoup, url: str) -> str:
    title_tag = soup.find("title")
    if title_tag and " - Skyliautie" in title_tag.get_text():
        return title_tag.get_text().split(" - Skyliautie")[0].strip()
    return os.path.basename(url.split("?")[0])

def get_all_poem_links() -> list:
    r = requests.get(LIST_URL, headers=HEADERS)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/shi/lech/" in href and not href.endswith("/shi/lech"):
            full_url = urljoin(BASE_URL, href)
            if "?authuser=0" not in full_url:
                full_url += "?authuser=0"
            title = a.get_text(strip=True) or os.path.basename(href.split("?")[0])
            links.append((title, full_url))
    return links

def main():
    os.makedirs("riparline_corpus", exist_ok=True)
    os.chdir("riparline_corpus")

    links = get_all_poem_links()
    print(f"検出された詩ページ数: {len(links)} 個\n")

    success = 0
    for i, (_, url) in enumerate(links, 1):
        print(f"[{i:02d}/{len(links)}] {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "html.parser")

            title = get_poem_title(soup, url)
            poem = extract_riparline_poem(soup)

            if not poem or len(poem) < 50:
                print("    ⚠️  詩が短すぎるか抽出失敗")
                continue

            safe_title = sanitize_filename(title)
            filename = f"Skyl.X-X（{safe_title}）.txt"
            counter = 1
            while os.path.exists(filename):
                filename = f"Skyl.X-X（{safe_title}_{counter}）.txt"
                counter += 1

            with open(filename, "w", encoding="utf-8") as f:
                f.write(poem + "\n")

            print(f"    ✅ {filename}  ({len(poem.splitlines())}行)")
            success += 1

        except Exception as e:
            print(f"    ❌ エラー: {e}")

    print(f"\n🎉 完了！ {success}/{len(links)} 件保存しました！")
    print("   フォルダ: riparline_corpus")

if __name__ == "__main__":
    main()