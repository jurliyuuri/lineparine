# scrape_skyliautie_fixed.py
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
    """
    2025年現在のSkyliautie詩ページから、リパライン語の詩部分だけを正確に抽出
    """
    # 方法1: <pre>タグがあれば最優先（古いページ用）
    pre = soup.find("pre")
    if pre and pre.get_text(strip=True):
        return pre_text = pre.get_text(separator="\n")
        if any(c in "áéíóúäëïöüãõñç'’" for c in pre_text):
            return pre_text.strip()

    # 方法2: Courier New などの等幅フォントで書かれたブロックを探す（これが現在主流）
    candidates = []
    for elem in soup.find_all(["div", "span", "p"], style=True):
        style = elem.get("style", "")
        if "courier" in style.lower() or "monospace" in style.lower() or "font-family:'courier new'" in style.lower():
            text = elem.get_text(separator="\n")
            if len(text) > 50:  # 詩はそれなりに長い
                candidates.append(text)

    # 方法3: class名に "sites-canvas-main-content" 内の長いテキストブロックなど
    if not candidates:
        main = soup.find("div", class_=re.compile(r"sites-canvas-main-content|main-content", re.I))
        if main:
            text = main.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            # リパライン語っぽい行を優先採取
            rip_lines = [ln for ln in lines if re.search(r"[áéíóúýäëïöüãõñç']", ln) and not re.search(r'[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\uFF00-\uFFEF]', ln)]
            if rip_lines:
                # 連続しているブロックを探す
                blocks = []
                curr = []
                for line in lines:
                    if re.search(r"[áéíóúýäëïöüãõñç']", line) and len(line) > 5:
                        curr.append(line)
                    elif curr:
                        blocks.append("\n".join(curr))
                        curr = []
                if curr:
                    blocks.append("\n".join(curr))
                if blocks:
                    # 一番長いブロックが長いものを採用
                    return max(blocks, key=len).strip()

    # 候補があれば一番長いものを返す
    if candidates:
        return max(candidates, key=len).strip()

    # 最終手段：全テキストから日本語・英語を除外して残った部分
    full_text = soup.get_text(separator="\n")
    lines = []
    for line in full_text.splitlines():
        line = line.strip()
        if not line:
            continue
        # 日本語・長い英語・ナビゲーションを除外
        if re.search(r'[ぁ-んァ-ヶ一-龠]', line):
            continue
        if re.search(r'^[a-zA-Z\s]{15,}$', line):  # 長すぎる英語行
            continue
        if any(nav in line for nav in ["Google Sites", "Report abuse", "Skyliautie", "ホーム"]):
            continue
        lines.append(line)

    return "\n".join(lines).strip() if lines else ""

def get_poem_title(soup: BeautifulSoup, url: str) -> str:
    title_tag = soup.find("title")
    if title_tag and " - Skyliautie" in title_tag.get_text():
        return title_tag.get_text().split(" - Skyliautie")[0].strip()
    # フォールバック：URLの最後
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
            title = a.get_text(strip=True) or os.path.basename(href)
            links.append((title, full_url))
    return links

def main():
    os.makedirs("riparline_corpus", exist_ok=True)
    os.chdir("riparline_corpus")

    links = get_all_poem_links()
    print(f"検出された詩ページ数: {len(links)} 個")

    success = 0
    for i, (_, url) in enumerate(links, 1):
        print(f"[{i:02d}/{len(links)}] 取得中 → {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "html.parser")

            title = get_poem_title(soup, url)
            poem = extract_riparline_poem(soup)

            if not poem or len(poem) < 30:
                print("    ⚠️  詩が抽出できませんでした（短すぎるか空）")
                continue

            filename_base = f"Skyl.X-X（{sanitize_filename(title)}）.txt"
            filename = filename_base
            counter = 1
            while os.path.exists(filename):
                filename = f"Skyl.X-X（{sanitize_filename(title)}_{counter}）.txt"
                counter += 1

            with open(filename, "w", encoding="utf-8") as f:
                f.write(poem + "\n")

            print(f"    ✅ 保存完了 → {filename} ({len(poem.splitlines())}行)")
            success += 1

        except Exception as e:
            print(f"    ❌ エラー: {e}")

    print(f"\n🎉 完了！ {success}/{len(links)} 件の詩を保存しました。")
    print("   フォルダ: riparline_corpus")

if __name__ == "__main__":
    main()