import os
import argparse

def extract_replin_lines(directory, order='japanese_first'):
    """
    指定されたディレクトリ内のテキストファイルからリパライン語の行を抽出して、
    新しいファイルを出力する。
    
    Args:
    directory (str): 対象ディレクトリのパス
    order (str): 'japanese_first' または 'replin_first'。ペアの順序を指定。
                 japanese_first: 奇数行 (0-indexed で偶数行が日本語、奇数行がリパライン)
                 replin_first: 偶数行 (0-indexed で偶数行がリパライン、奇数行が日本語)
    """
    if order not in ['japanese_first', 'replin_first']:
        raise ValueError("order must be 'japanese_first' or 'replin_first'")
    
    # ディレクトリ内のすべての.txtファイルを処理
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            input_path = os.path.join(directory, filename)
            output_filename = f"{os.path.splitext(filename)[0]}_extract.txt"
            output_path = os.path.join(directory, output_filename)
            
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # リパライン語の行を抽出
            replin_lines = []
            if order == 'japanese_first':
                # 奇数インデックス (0-based: 1,3,5...)
                replin_lines = [lines[i].strip() for i in range(1, len(lines), 2) if i < len(lines)]
            else:
                # 偶数インデックス (0-based: 0,2,4...)
                replin_lines = [lines[i].strip() for i in range(0, len(lines), 2) if i < len(lines)]
            
            # 出力ファイルに書き込み
            with open(output_path, 'w', encoding='utf-8') as f:
                for line in replin_lines:
                    f.write(line + '\n')
            
            print(f"Processed {filename} -> {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Replin lines from text files in a directory.")
    parser.add_argument("directory", help="Path to the directory containing text files.")
    parser.add_argument("--order", choices=['japanese_first', 'replin_first'], 
                        default='japanese_first', 
                        help="Order of pairs: japanese_first (default) or replin_first.")
    
    args = parser.parse_args()
    extract_replin_lines(args.directory, args.order)