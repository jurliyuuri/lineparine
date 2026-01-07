import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://sites.google.com/site/skyliautie/"
LIST_URL = "https://sites.google.com/site/skyliautie/shi/lech"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

def sanitize_filename(title: str) -> str:
    title = title.strip().lower()
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'[^\w\-]', '', title)
    return title if title else "untitled"

def extract_riparline_poem(soup: BeautifulSoup) -> str:
    """2025年現在のGoogle Sites構造に完全対応した抽出関数"""
    
    # 方法1: <pre>タグがあれば即採用（古いページ用）
    pre = soup.find("pre")
    if pre:
        text = pre.get_text(separator="\n").strip()
        if "á" in text or "é" in text or "'" in text:
            return text

    # 方法2: 等幅フォント（courier/monospace）の要素をすべて集めて再構築
    poem_parts = []
    for tag in soup.find_all(style=re.compile(r"courier|monospace|Lucida Console", re.I)):
        text = tag.get_text(separator="\n")
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        poem_parts.extend(lines)
    
    if poem_parts:
        return "\n".join(poem_parts)

    # 方法3: アクセント文字・アポストロフィを含む行を全ページから徹底的に集める（最終兵器）
    full_text = soup.get_text(separator="\n")
    lines = []
    for line in full_text.split("\n"):
        s = line.strip()
        if not s:
            continue
        # リパライン語の特徴でフィルタ（アクセント or アポストロフィがあって、日本語なし、英語長文なし）
        if re.search(r"[áéíóúýäëïöüãõñç'’ʻʼʾ]", s) and \
           not re.search(r"[ぁ-んァ-ヶ一-龠]", s) and \
           len(s) < 120 and \
           not s.isascii():
            lines.append(s)
    
    return "\n".join(lines) if lines else ""

def get_poem_title(soup: BeautifulSoup, url: str) -> str:
    if soup.title and " - Skyliautie" in soup.title.string:
        return soup.title.string.split(" - Skyliautie")[0].strip()
    return os.path.basename(url.split("?")[0])

def get_all_poem_links() -> list:
    r = requests.get(LIST_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")
    
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/shi/lech/" in href and href.count("/") >= 5:  # 個別詩ページの深さ
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
    print(f"検出された詩ページ: {len(links)}個\n")

    success = 0
    for i, (_, url) in enumerate(links, 1):
        print(f"[{i:02d}/{len(links)}] {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "html.parser")
            
            title = get_poem_title(soup, url)
            poem = extract_riparline_poem(soup)
            
            if len(poem) < 60:  # さすがに短すぎたら失敗扱い（実質これで漏れなし）
                print("    ⚠️  抽出失敗または短すぎる")
                continue
                
            safe_title = sanitize_filename(title)
            filename = f"Skyl.X-X（{safe_title}）.txt"
            counter = 1
            while os.path.exists(filename):
                filename = f"Skyl.X-X（{safe_title}_{counter}）.txt"
                counter += 1
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(poem + "\n")
            
            print(f"    ✅ 保存: {filename}  ({len(poem.splitlines())}行)")
            success += 1
            
        except Exception as e:
            print(f"    ❌ エラー: {e}")
    
    print(f"\n🎉 完了！ {success}/{len(links)} 件を riparline_corpus に保存しました！")

if __name__ == "__main__":
    main()