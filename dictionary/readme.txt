英辞郎→StarDict辞書変換スクリプト

eiji2sd-text.ps1, eiji2sd-text.pl - StarDict向け。辞書データに通常のテキストを使う
eiji2sd-html.ps1, eiji2sd-html.pl - GoldenDict、OmegaT向け。辞書データはHTML

使い方（PowerShell版）

1. eiji2sd-xxxx.ps1と同じフォルダーに英辞郎のテキストデータ（EIJI-140.TXTなど）を保存する

2. eiji2sd-xxxx.ps1があるフォルダーで、エクスプローラーの上部メニューの
「ファイル」→「Windows PowerShell を開く」からPowerShellのコンソールを起動する

3. コンソールに
PS>Set-ExecutionPolicy Unrestricted
と入力する（ネットから取得したスクリプトは初期設定では実行できないため）

4. コンソールに以下のように入力する（EIJI-XXX.TXTの部分は各自所有のファイル名にしてください）
PS>.\eiji2sd-xxxx.ps1 .\EIJI-XXX.TXT

5. 以下のファイルができるので、StarDict形式辞書に対応するソフトで使用する

stardict.idx
stardict.dict
stardict.ifo

例：EIJIROという名前のフォルダーを作って上記3つのファイルを入れ、
フォルダーごと以下の場所にコピーする。

StarDict："C:\Program Files (x86)\StarDict\dic"
GoldenDict（ポータブル版）：GoldenDictインストール先の"GoldenDict\content"
OmegaT：プロジェクト保存場所の "dictionary" フォルダー

使い方（Perl版）
perlの実行ファイルがインストールされていることが前提になります

1. eiji2sd.pl-xxxxと同じフォルダーに英辞郎のテキストデータ（EIJI-140.TXTなど）を保存する

2. 以下のようにしてスクリプトを実行する
perl eiji2sd-xxxx.pl EIJI-XXX.TXT

3. 以降はPowerShell版と同じ

補足

・PowerShell版とPerl版で作成される辞書のサイズが微妙に違いますが、
内容としては同じです（PowerShell版はいろんな文字をHTMLエスケープするため）

・辞書の読み込みを確認したソフト：StarDict、GoldenDict、OmegaT

・dictzipで辞書を圧縮することができます。
dictzip stardict.dict

・Windows版Dictzip
https://github.com/Tvangeste/dictzip-win32/releases

・英辞郎のフォーマット詳細
http://www.eijiro.jp/spec.htm

・StarDict辞書のフォーマット詳細
http://www.stardict.org/StarDictFileFormat

ライセンス等

スクリプトの利用に制限はありません。
ただし、英辞郎のデータは規約に従って利用するようにお願いします。

改訂履歴
2016-03-07 eiji2sd-text.ps1, eiji2sd-html.ps1
未存在のファイルにResolve-Pathを使うとエラーになるため、Join-Pathに変更した

スクリプト作成者

大和利之 <toshiyuki.yamato@gmail.com>
