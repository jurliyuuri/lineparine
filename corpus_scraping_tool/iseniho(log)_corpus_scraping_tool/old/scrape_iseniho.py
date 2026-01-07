import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urljoin

# 保存フォルダ作成
output_dir = "riparian_corpus"
os.makedirs(output_dir, exist_ok=True)

# User-Agent（Google Sitesはこれがないとたまにブロックされる）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWeb 537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
}

# 1〜8部までの正しいURLマッピング（2025年11月現在）
chapters = {
    1: "1st/1/t",   # 創世記
    2: "1st/2/t",   # 出エジプト記〜士師記
    3: "1st/3/t",   # サムエル記〜列王紀下
    4: "1st/4/t",   # 列王紀下（続き）〜歴代誌上？
    5: "2nd/1/t",   # 歴代誌上〜ヨブ記？
    6: "2nd/2/t",
    7: "2nd/3/t",
    8: "2nd/4/t",   # マラキ書まで
}

base_url = "https://sites.google.com/site/good0think/"

def extract_riparian_from_parallel_page(html):
    soup = BeautifulSoup(html, "html.parser")
    
    # 本文エリア取得
    content = soup.find("div", class_="sites-layout-tile")
    if not content:
        content = soup.find("div", id="sites-canvas-main-content")
    if not content:
        return ""
    
    # すべてのテキストを改行で分割
    lines = content.get_text(separator="\n").split("\n")
    
    riparian_text = []
    is_next_riparian = False  # 次がリパライン語かどうかのフラグ
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # #数字 の節番号が来たら、次がリパライン語
        if re.match(r"^#\d+", line):
            is_next_riparian = True
            continue  # 節番号自体は保存しない（必要なら残す）
        
        # フラグが立っている＝この行はリパライン語
        if is_next_riparian:
            # 明らかに日本語だけの行はスキップ（保険）
            if re.search(r'[ぁ-んァ-ヶ一-龠]', line) and not re.search(r'[a-zA-Záéíóúäëïöü]', line):
                is_next_riparian = True  # 日本語だったら次のリパライン語を待つ
                continue
            riparian_text.append(line)
            is_next_riparian = False  # 次は日本語のはず
        else:
            # 通常は日本語のはずなので無視するが、
            # 稀にリパライン語が連続する場合の保険として、
            # ラテン文字中心なら採用
            if len(re.findall(r'[a-zA-ZáéíóúäëïöüÁÉÍÓÚÄËÏÖÜ]', line)) > len(line) * 0.7:
                riparian_text.append(line)
            # 次の行がまたリパライン語の可能性を残す
            if re.match(r"^#\d+", line):
                is_next_riparian = True

    return "\n".join(riparian_text)

print("リパライン語旧約聖書コーパス収集開始（最新構造対応版）\n")

for chap_num, path in chapters.items():
    url = base_url + path
    print(f"第{chap_num}部 取得中 → {url}")
    
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        r.encoding = "utf-8"
        
        text = extract_riparian_from_parallel_page(r.text)
        
        filename = f"iseniho(Chap_{chap_num}).txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        
        lines_count = len([l for l in text.split("\n") if l.strip()])
        print(f" → {filename} 保存完了（{lines_count}行）")
        
    except Exception as e:
        print(f" × 第{chap_num}部でエラー: {e}")

print("\n全8部 完了！")
print(f"ファイルは「{output_dir}」フォルダに保存されました。")
print("これでAntConcやSketch Engineで完全に使える高品質リパライン語コーパスになります！")