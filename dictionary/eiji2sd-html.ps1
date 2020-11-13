Add-Type -AssemblyName System.Web

function Html-Encode {
    param( [string]$string )
    return [System.Web.HttpUtility]::HtmlEncode($string)
}

# 整数をネットワークバイトオーダーに変換し、そのバイト配列を返す
# ものすごく遅い
<#
function ConvertTo-BigEndian {
    param( [uint32]$value )
    [byte[]]$bytes = [BitConverter]::GetBytes($value)
    if ( [BitConverter]::IsLittleEndian ) { [Array]::Reverse($bytes) }
    return $bytes
}
#>

$doArrayReverse = ""

if ( [BitConverter]::IsLittleEndian ) {
    $doArrayReverse = 'System.Array.Reverse(bytes1); System.Array.Reverse(bytes2);'
}

# PowerShellだと遅いのでこちらを使う
$code = @"
public class IdxByteConverter {
    public static byte[] Convert(uint value1, uint value2) {
        byte[] bytes1 = System.BitConverter.GetBytes(value1);
        byte[] bytes2 = System.BitConverter.GetBytes(value2);
        $doArrayReverse
        byte[] retBytes = new byte[bytes1.Length + bytes2.Length];
        bytes1.CopyTo(retBytes, 0);
        bytes2.CopyTo(retBytes, bytes1.Length);
        return retBytes;
    }
}
"@

Add-Type -Language CSharp -TypeDefinition $code

$txtFile = (Resolve-Path $args[0]).Path
$reader = New-Object IO.StreamReader( $txtFile, [Text.Encoding]::GetEncoding("shift_jis"), $false )
$dataHash = New-Object "Collections.Generic.Dictionary[String, Collections.Hashtable]" -ArgumentList @([int]3000000)
$wordList = New-Object 'Collections.Generic.List[String]' -ArgumentList @([int]3000000)
$wordCount1 = 0

$idxFile  = Join-Path (pwd) stardict.idx
$dictFile = Join-Path (pwd) stardict.dict
$ifoFile  = Join-Path (pwd) stardict.ifo

try { 

    while (-not $reader.EndOfStream) {

        $line = $reader.ReadLine()
        $wordContent = @( $line -split " : ", 2 )
        $word = $wordContent[0] -replace "^■", ""
        $content = $wordContent[1]

        $part = $null

        if ($word -match "\s*{(.+?)}\s*") {
            $part = ( $Matches[1] -replace "^\d+\-", "" ) -replace "\-\d+$", ""
            if ($part -match "^\d+$") {
                $part = $null
            }
            $word = $word -replace "\s*{.+?}\s*", ""
        }

        if ($word.Length -eq 1) { continue }
        if ( [Text.Encoding]::UTF8.GetByteCount($word) -gt 255) { continue }

        $meaningExtra = @( $content -split "(?=◆|■・)" )
        $meaning = $meaningExtra[0] -replace "｛.+?｝", ""
        $meaningExtra[0] = $null

        $note = @()
        $example = @()

        foreach ($text in $meaningExtra) {
            if ($text -match "^◆") {
                $note += ($text -replace "^◆", "")
            }
            elseif ($text -match "^■・") {
                $example += ($text -replace "^■・", "")
            }
        }

        $data = @{
            part = $part
            meaning = $meaning
            # note = $note
            # example = $example
            extra = $note + $example
            next = @()
        }

        if ( $dataHash.ContainsKey($word)  ) {
            $dataHash[$word]["next"] += $data
        }
        else {
            $dataHash.Add($word, $data)
            $wordList.Add($word)
            $wordCount1++
        }

        if ( ($wordCount1 % 5000) -eq 0 ) {
            Write-Progress -Activity "データを読込み中" -Status $word
        }
    }
}
finally {
    $reader.Close()
}

$wordCount2 = 0
[uint32]$offset = 0

$idxWriter  = [IO.File]::Create($idxFile)
$dictWriter = [IO.File]::Create($dictFile)

try {

    [Text.StringBuilder]$buffer = New-Object Text.StringBuilder(1024)
 
    Write-Progress -Activity "項目をソート中"
    [void]$wordList.Sort([StringComparer]::OrdinalIgnoreCase) # バイト比較でソートする

    foreach ($word in $wordList) {

        $data = $dataHash[$word]
        $wordEscaped = (Html-Encode $word)
        $part = ""
        $extra = ""
        $currentPart = $null

        if ( $data["part"] -ne $null ) {
            $part = "【" + (Html-Encode $data["part"]) + "】"
            $currentPart = $data["part"]
        }

        if ( $data["extra"].Length -ne 0 ) {
            $li = $data["extra"] | foreach { "<li>" + (Html-Encode $_) + "</li>" }
            $extra = '<ul style="list-style-type: none; margin-top: 0; margin-bottom: 0;">' + ($li -join "") + '</ul>'
        }

        [void]$buffer.AppendFormat("<dl><dt>{0}<dfn>{1}</dfn></dt><dd>{2}{3}</dd>", $part, $wordEscaped, ( Html-Encode $data["meaning"] ), $extra )

        foreach ($next in $data["next"]) {

            $part = ""
            $dt = ""
            $extra = ""

            if ( $currentPart -ne $next["part"] ) {
                if ($next["part"] -ne $null) {
                    $part = "【" + (Html-Encode $next["part"]) + "】"
                }
                $dt = "<dt>{0}<dfn>{1}</dfn></dt>" -f $part, $wordEscaped
                $currentPart = $next["part"]
            }

            if ( $next["extra"].Length -ne 0 ) {
                $li = $next["extra"] | foreach { "<li>" + (Html-Encode $_) + "</li>" }
                $extra = '<ul style="list-style-type: none; margin-top: 0; margin-bottom: 0;">' + ($li -join "") + '</ul>'
            }
            [void]$buffer.AppendFormat("{0}<dd>{1}{2}</dd>", $dt, ( Html-Encode $next["meaning"] ), $extra )
        }

        [void]$buffer.Append("</dl>")

        $wordBytes = [Text.Encoding]::UTF8.GetBytes($word + "`0") # 末尾にヌル文字
        $textBytes = [Text.Encoding]::UTF8.GetBytes( $buffer.ToString() )
        [void]$buffer.Clear()
        $idxBytes = $wordBytes + [IdxByteConverter]::Convert($offset, $textBytes.Length)

        [void]$idxWriter.Write([byte[]]$idxBytes, 0, $idxBytes.Length)
        [void]$dictWriter.Write([byte[]]$textBytes, 0, $textBytes.Length)

        $offset += $textBytes.Length
        $wordCount2++

        if ( ($wordCount2 % 5000) -eq 0 ) {
            Write-Progress -Activity "データを書き込み中" -Status $word -PercentComplete ($wordCount2 / $wordCount1 * 100)
        }
    }

}
finally {
    $idxWriter.Close()
    $dictWriter.Close()
}

$idxSize = (Get-Item -LiteralPath $idxFile).Length

$ifoContent = @"
StarDict's dict ifo file
version=2.4.2
bookname=英辞郎
wordcount=$wordCount1
idxfilesize=$idxSize
sametypesequence=h

"@

$ifoContent = ($ifoContent -replace "`r`n", "`n") # StarDictは改行がLFでないと認識しない

[IO.File]::WriteAllBytes( $ifoFile, [Text.Encoding]::UTF8.GetBytes($ifoContent) )
Write-Progress -Activity "辞書を書き込み中" -Status "完了" -Completed
