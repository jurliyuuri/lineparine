// update-list.js  ← これをフォルダに保存
const fs = require('fs');
const path = require('path');

const files = fs.readdirSync('.')
    .filter(file => path.extname(file).toLowerCase() === '.txt')
    .map(file => ({ name: file }));

fs.writeFileSync('files.json', JSON.stringify(files, null, 2));
console.log(`✅ files.json を更新しました！（${files.length}個の.txtファイル）`);