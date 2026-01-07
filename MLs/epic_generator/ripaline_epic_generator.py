import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os
import re

# GPU設定の確認
print("GPUの使用可能性:", "利用可能" if tf.config.list_physical_devices('GPU') else "利用不可")

class RipalineEpicGenerator:
    def __init__(self, corpus_file='lerne.1-1-1.txt'):
        self.corpus_file = corpus_file
        self.tokenizer = None
        self.model = None
        self.max_sequence_len = None
        self.total_words = None
        
    def count_syllables(self, word):
        """音節数をカウント（母音ベース）"""
        # リパライン語の母音パターン
        vowels = 'aeiouáéíóúâêîôû'
        # 特殊文字を除去
        clean_word = re.sub(r'[^a-záéíóúâêîôû]', '', word.lower())
        return sum(1 for char in clean_word if char in vowels)
    
    def load_and_preprocess_corpus(self):
        """コーパスを読み込んで前処理"""
        print("コーパスを読み込み中...")
        with open(self.corpus_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 引用符を標準化
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # 行ごとに分割
        lines = [line.strip().strip('"') for line in text.split('\n') if line.strip()]
        
        # 空行や短すぎる行を除外
        lines = [line for line in lines if len(line.split()) >= 5]
        
        print(f"総行数: {len(lines)}")
        
        # 12音節の行をフィルタリング（±1音節の誤差を許容）
        filtered_lines = []
        for line in lines:
            words = line.split()
            total_syllables = sum(self.count_syllables(w) for w in words)
            if 11 <= total_syllables <= 13:
                filtered_lines.append(line)
        
        print(f"12音節の行数: {len(filtered_lines)}")
        
        # フィルタリング後の行が少なすぎる場合は全行を使用
        if len(filtered_lines) < 100:
            print("警告: 12音節の行が少ないため、全ての行を使用します")
            return lines
        
        return filtered_lines
    
    def create_sequences(self, lines, seq_length=15):
        """訓練用のシーケンスデータを作成"""
        print("シーケンスデータを作成中...")
        
        # トークナイザーの作成
        self.tokenizer = Tokenizer()
        self.tokenizer.fit_on_texts(lines)
        self.total_words = len(self.tokenizer.word_index) + 1
        
        print(f"語彙数: {self.total_words}")
        
        # 入力シーケンスを作成
        input_sequences = []
        for line in lines:
            token_list = self.tokenizer.texts_to_sequences([line])[0]
            # N-gramシーケンスを生成
            for i in range(1, len(token_list)):
                n_gram_sequence = token_list[:i+1]
                input_sequences.append(n_gram_sequence)
        
        # パディング
        self.max_sequence_len = max([len(seq) for seq in input_sequences])
        input_sequences = pad_sequences(input_sequences, 
                                        maxlen=self.max_sequence_len, 
                                        padding='pre')
        
        # X（入力）とy（出力）に分割
        X = input_sequences[:, :-1]
        y = input_sequences[:, -1]
        
        # yをone-hot化
        y = tf.keras.utils.to_categorical(y, num_classes=self.total_words)
        
        print(f"訓練サンプル数: {len(X)}")
        print(f"最大シーケンス長: {self.max_sequence_len}")
        
        return X, y
    
    def build_model(self, embedding_dim=128, lstm_units=256):
        """LSTMモデルを構築"""
        print("モデルを構築中...")
        
        model = Sequential()
        
        # 埋め込み層
        model.add(Embedding(self.total_words, 
                           embedding_dim, 
                           input_length=self.max_sequence_len-1))
        
        # 双方向LSTM層（より文脈を理解）
        model.add(Bidirectional(LSTM(lstm_units, return_sequences=True)))
        model.add(Dropout(0.3))
        
        model.add(LSTM(lstm_units // 2))
        model.add(Dropout(0.3))
        
        # 出力層
        model.add(Dense(self.total_words, activation='softmax'))
        
        # コンパイル
        model.compile(loss='categorical_crossentropy',
                     optimizer='adam',
                     metrics=['accuracy'])
        
        model.summary()
        
        return model
    
    def train(self, epochs=100, batch_size=128, save_path='ripaline_epic_model.h5'):
        """モデルを訓練"""
        # データ準備
        lines = self.load_and_preprocess_corpus()
        X, y = self.create_sequences(lines)
        
        # モデル構築
        self.model = self.build_model()
        
        # メタ情報を保存
        metadata_path = save_path.replace('.h5', '_metadata.txt')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write(f"max_sequence_len={self.max_sequence_len}\n")
            f.write(f"total_words={self.total_words}\n")
        
        # コールバック設定
        checkpoint = ModelCheckpoint(save_path, 
                                    monitor='loss', 
                                    verbose=1, 
                                    save_best_only=True, 
                                    mode='min')
        
        early_stop = EarlyStopping(monitor='loss', 
                                   patience=10, 
                                   verbose=1)
        
        # 訓練開始
        print("\n訓練を開始します...")
        history = self.model.fit(X, y, 
                               epochs=epochs,
                               batch_size=batch_size,
                               callbacks=[checkpoint, early_stop],
                               verbose=1)
        
        print(f"\n訓練完了！モデルを {save_path} に保存しました。")
        print(f"メタ情報を {metadata_path} に保存しました。")
        
        return history
    
    def load_trained_model(self, model_path='ripaline_epic_model.h5'):
        """訓練済みモデルをロード"""
        if os.path.exists(model_path):
            print(f"モデルを {model_path} から読み込み中...")
            self.model = load_model(model_path)
            
            # モデルからmax_sequence_lenを取得
            self.max_sequence_len = self.model.input_shape[1] + 1
            print(f"モデルの読み込み完了！(シーケンス長: {self.max_sequence_len})")
            return True
        else:
            print(f"エラー: {model_path} が見つかりません")
            return False
    
    def predict_next_word(self, seed_text, temperature=1.0):
        """次の単語を予測"""
        token_list = self.tokenizer.texts_to_sequences([seed_text])[0]
        token_list = pad_sequences([token_list], 
                                   maxlen=self.max_sequence_len-1, 
                                   padding='pre')
        
        # 予測
        predictions = self.model.predict(token_list, verbose=0)[0]
        
        # Temperature samplingで多様性を制御
        predictions = np.asarray(predictions).astype('float64')
        predictions = np.log(predictions + 1e-7) / temperature
        exp_preds = np.exp(predictions)
        predictions = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, predictions, 1)
        predicted_index = np.argmax(probas)
        
        # トークンを単語に変換
        for word, index in self.tokenizer.word_index.items():
            if index == predicted_index:
                return word
        
        return ""
    
    def generate_line(self, seed_text, max_words=20, temperature=0.8, 
                     target_syllables=12):
        """1行を生成（12音節を目指す）"""
        current_text = seed_text
        words_generated = 0
        current_syllables = sum(self.count_syllables(w) for w in seed_text.split())
        
        while words_generated < max_words:
            next_word = self.predict_next_word(current_text, temperature)
            
            if not next_word:
                break
            
            # 音節数をチェック
            next_syllables = self.count_syllables(next_word)
            potential_syllables = current_syllables + next_syllables
            
            # 12音節に近づいたら終了
            if potential_syllables >= 11 and potential_syllables <= 13:
                current_text += " " + next_word
                break
            elif potential_syllables > 13:
                # 音節オーバーなら終了
                break
            
            current_text += " " + next_word
            current_syllables = potential_syllables
            words_generated += 1
        
        return current_text
    
    def generate_epic_poem(self, num_stanzas=4, lines_per_stanza=4, 
                          temperature=0.8, seed_words=None):
        """叙事詩を生成"""
        if seed_words is None:
            # コーパスから頻出する開始語を使用
            seed_words = ["la", "si", "berxa", "mal", "fal", "ci", "pa", "me"]
        
        poem_stanzas = []
        
        for stanza_num in range(num_stanzas):
            print(f"\n連 {stanza_num + 1} を生成中...")
            stanza_lines = []
            
            for line_num in range(lines_per_stanza):
                # ランダムに開始語を選択
                seed = np.random.choice(seed_words)
                
                # 行を生成
                line = self.generate_line(seed, temperature=temperature)
                
                # 音節数を確認
                syllables = sum(self.count_syllables(w) for w in line.split())
                print(f"  行 {line_num + 1} ({syllables}音節): {line}")
                
                stanza_lines.append(line)
            
            poem_stanzas.append(stanza_lines)
        
        return poem_stanzas
    
    def format_poem(self, stanzas):
        """詩を整形して出力"""
        formatted = []
        for i, stanza in enumerate(stanzas):
            formatted.append(f"=== 第{i+1}連 ===")
            for j, line in enumerate(stanza):
                syllables = sum(self.count_syllables(w) for w in line.split())
                formatted.append(f'"{line}" ({syllables}音節)')
            formatted.append("")
        
        return '\n'.join(formatted)


# ========== メイン実行部分 ==========

if __name__ == "__main__":
    # ジェネレーターのインスタンス化
    generator = RipalineEpicGenerator('lerne.1-1-1.txt')
    
    # モードを選択
    print("=" * 50)
    print("リパライン語叙事詩ジェネレーター")
    print("=" * 50)
    print("\n1. 新規訓練")
    print("2. 既存モデルで生成")
    
    mode = input("\nモードを選択 (1 or 2): ").strip()
    
    if mode == "1":
        # 新規訓練
        print("\n=== 訓練モード ===")
        epochs = int(input("エポック数 (推奨: 100): ") or "100")
        
        # 訓練実行
        generator.train(epochs=epochs, batch_size=128)
        
        # 訓練後に生成するか確認
        gen_now = input("\n今すぐ詩を生成しますか？ (y/n): ").strip().lower()
        if gen_now != 'y':
            print("訓練完了。終了します。")
            exit()
    
    elif mode == "2":
        # 既存モデルをロード
        print("\n=== 生成モード ===")
        model_path = input("モデルファイルパス (Enter=ripaline_epic_model.h5): ").strip()
        if not model_path:
            model_path = 'ripaline_epic_model.h5'
        
        # モデルをロード
        if not generator.load_trained_model(model_path):
            print("エラー: モデルの読み込みに失敗しました")
            exit()
        
        # メタ情報を読み込み
        metadata_path = model_path.replace('.h5', '_metadata.txt')
        if os.path.exists(metadata_path):
            print(f"メタ情報を {metadata_path} から読み込み中...")
            with open(metadata_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('max_sequence_len='):
                        generator.max_sequence_len = int(line.split('=')[1].strip())
                    elif line.startswith('total_words='):
                        generator.total_words = int(line.split('=')[1].strip())
            print(f"max_sequence_len: {generator.max_sequence_len}")
            print(f"total_words: {generator.total_words}")
        
        # トークナイザーの再構築（訓練時と同じデータで）
        lines = generator.load_and_preprocess_corpus()
        generator.tokenizer = Tokenizer()
        generator.tokenizer.fit_on_texts(lines)
        
        # total_wordsが一致するか確認
        expected_words = len(generator.tokenizer.word_index) + 1
        if generator.total_words and generator.total_words != expected_words:
            print(f"警告: 語彙数が異なります (メタ: {generator.total_words}, 実際: {expected_words})")
        generator.total_words = expected_words
    
    else:
        print("無効な選択です")
        exit()
    
    # 詩の生成
    print("\n" + "=" * 50)
    print("叙事詩を生成します")
    print("=" * 50)
    
    num_stanzas = int(input("\n連の数 (推奨: 3-5): ") or "4")
    temperature = float(input("創造性 (0.5=保守的, 1.0=バランス, 1.5=創造的): ") or "0.8")
    
    # 生成実行
    print("\n生成中...\n")
    stanzas = generator.generate_epic_poem(num_stanzas=num_stanzas, 
                                           temperature=temperature)
    
    # 結果を表示
    print("\n" + "=" * 50)
    print("生成された叙事詩")
    print("=" * 50 + "\n")
    print(generator.format_poem(stanzas))
    
    # ファイルに保存
    output_file = f"generated_epic_{np.random.randint(1000, 9999)}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(generator.format_poem(stanzas))
    
    print(f"\n詩を {output_file} に保存しました！")
