import re
import sys
from pathlib import Path

def is_lineparine(text):
    """
    テキストがリパライン語かどうかを判定する
    リパライン語の特徴：アルファベット、アポストロフィ、ピリオド、感嘆符などを含む
    """
    # 空行や空白のみの行は除外
    if not text.strip():
        return False
    
    # 日本語文字（ひらがな、カタカナ、漢字）が含まれていたら日本語と判定
    if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text):
        return False
    
    # アルファベットが含まれていればリパライン語の可能性が高い
    if re.search(r'[a-zA-Z]', text):
        return True
    
    return False

def extract_lineparine(input_file):
    """
    入力ファイルからリパライン語の行を抽出する
    """
    try:
        # 入力ファイルを読み込む
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # リパライン語の行を抽出
        lineparine_lines = []
        for line in lines:
            if is_lineparine(line):
                lineparine_lines.append(line)
        
        # 出力ファイル名を生成
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_extract{input_path.suffix}"
        
        # 抽出結果を出力
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lineparine_lines)
        
        print(f"抽出完了: {len(lineparine_lines)}行のリパライン語を抽出しました")
        print(f"出力ファイル: {output_file}")
        
        return True
        
    except FileNotFoundError:
        print(f"エラー: ファイル '{input_file}' が見つかりません")
        return False
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("使用方法: python script.py <入力ファイル>")
        print("例: python script.py input.txt")
        return
    
    input_file = sys.argv[1]
    extract_lineparine(input_file)

if __name__ == "__main__":
    main()