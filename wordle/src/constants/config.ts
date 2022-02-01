export const CONFIG = {
  tries: 6, // This changes how many tries you get to finish the wordle
  language: 'Lineparine', // This changes the display name for your language
  wordLength: 5, // This sets how long each word is based on how many characters (as defined in orthography.ts) are in each word
  author: 'Fafs F. Sashimi', // Put your name here so people know who made this Wordle!
  authorWebsite: 'https://w.atwiki.jp/cgwj/pages/42.html', // Put a link to your website or social media here
  wordListSource: 'Lineparine ad japaeovirle cecio levipesta', // Describe the source material for your words here
  wordListSourceLink: 'https://jurliyuuri.com/lineparine/wordle/list.html', // Put a link to the source material for your words here
  //
  // THESE NEXT SETTINGS ARE FOR ADVANCED USERS
  //
  googleAnalytics: '', // You can use this if you use Google Analytics
  shuffle: false, // whether to shuffle the words in the wordlist each time you load the app (note: you will lose the 'word of the day' functionality if this is true)
  normalization: 'NFC', // whether to apply Unicode normalization to words and orthography - options: 'NFC', 'NFD', 'NKFC', 'NKFD', false
}
