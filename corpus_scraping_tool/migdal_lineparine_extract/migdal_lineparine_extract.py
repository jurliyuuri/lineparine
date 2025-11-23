import sys
import re
import os

def extract_and_process_sections(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 正規表現でタグ間の内容を抽出（複数マッチ、DOTALLで改行を含む）
        pattern = r'\{% ln x-v3-jrlrflll %\}(.*?)\{% endln %\}'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if not matches:
            print("指定されたタグが見つかりませんでした。")
            return
        
        # Markdownリンクの置き換えパターン: [text](url) → text
        link_pattern = r'\[([^\]]*)\]\([^)]*\)'
        
        # 出力ファイルのパスを作成（ファイル名にシングルクォート'が含まれる場合もそのまま使用）
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        dir_path = os.path.dirname(file_path) or '.'
        output_file = os.path.join(dir_path, f"{base_name}_extract.txt")
        
        with open(output_file, 'w', encoding='utf-8') as out_file:
            for match in matches:
                processed = re.sub(link_pattern, r'\1', match.strip())
                # 空行を完全に詰める（1つ以上の連続改行を単一の改行に統一し、空行を除去）
                processed = re.sub(r'\n+', '\n', processed)
                out_file.write(processed + '\n\n')  # セクション間の改行区切り
        
        print(f"抽出および処理が完了しました。出力ファイル: {output_file}")
    
    except FileNotFoundError:
        print(f"ファイル '{file_path}' が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用法: python script.py <テキストファイルのパス>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    extract_and_process_sections(file_path)