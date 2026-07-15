(function(){
  "use strict";

  var DICT_BASE = "https://jurliyuuri.com/lineparine/dictionary/#w/";
  var SERIES_TITLE = "D'alen.vilaija, lirnasti";

  // ---------- 1. work out which episode this page is ----------
  var m = location.pathname.match(/episode_(\d+)\.html?$/i);
  if(!m){
    renderFatal("このページのファイル名から話数を判別できませんでした（episode_XXXX.html という名前である必要があります）。");
    return;
  }
  var epStr = m[1];              // e.g. "0016", keeps original zero-padding
  var epNum = parseInt(epStr, 10);
  var txtFile = "episode_" + epStr + ".txt";

  // ---------- 2. page shell ----------
  document.body.innerHTML =
    '<header class="chrome">' +
      '<a class="back" href="index.html">&larr; トップに戻る</a>' +
      '<label class="font-switch">' +
        '<span>cirlxarli liparxeで表示</span>' +
        '<input type="checkbox" id="fontToggle" class="hidden-checkbox" checked>' +
        '<span class="switch-track"></span>' +
      '</label>' +
    '</header>' +
    '<div class="page"><div class="leaf" id="leaf">' +
      '<p class="loading" id="loading">読み込んでいます…</p>' +
    '</div></div>' +
    '<div id="glossToast" role="status" aria-live="polite"></div>';

  fetch(txtFile)
    .then(function(res){
      if(!res.ok) throw new Error("txt not found: " + res.status);
      return res.text();
    })
    .then(function(raw){ renderEpisode(raw); })
    .catch(function(err){
      renderFatal("本文ファイル（" + txtFile + "）の読み込みに失敗しました。同じディレクトリにファイルが存在するか確認してください。");
      console.error(err);
    });

  function renderFatal(msg){
    var leaf = document.getElementById("leaf") || document.body;
    leaf.innerHTML = '<p class="error">' + escapeHtml(msg) + "</p>";
  }

  // ---------- 3. parse the .txt into title + paragraph blocks ----------
  function parseEpisode(raw){
    var lines = raw.replace(/\r\n?/g, "\n").split("\n");

    var title = "";
    for(var i = 0; i < lines.length; i++){
      if(lines[i].trim() === "【xakantasti】"){
        title = (lines[i+1] || "").trim();
        break;
      }
    }

    var bodyStart = -1;
    for(var j = 0; j < lines.length; j++){
      if(/^【dirxel/.test(lines[j].trim())){
        bodyStart = j + 1;
        break;
      }
    }
    var bodyLines = bodyStart >= 0 ? lines.slice(bodyStart) : lines;
    var bodyText = bodyLines.join("\n").trim();
    var blocks = bodyText.split(/\n\s*\n+/).map(function(b){ return b.trim(); }).filter(Boolean);

    return { title: title, blocks: blocks };
  }

  function classifyBlock(block){
    var first = block.split("\n")[0];
    if(first.charAt(0) === '"') return "dialogue";
    if(first.charAt(0) === "(") return "thought";
    return "narration";
  }

  // ---------- 4. render ----------
  function renderEpisode(raw){
    var parsed = parseEpisode(raw);
    document.title = SERIES_TITLE + (parsed.title ? " ―" + parsed.title + "―" : "");

    var leaf = document.getElementById("leaf");
    leaf.innerHTML = "";

    var eyebrow = document.createElement("p");
    eyebrow.className = "eyebrow";
    eyebrow.textContent = SERIES_TITLE;
    leaf.appendChild(eyebrow);

    var h2 = document.createElement("h2");
    h2.className = "chapter fy";
    h2.id = "chapterTitle";
    h2.textContent = parsed.title || ("episode_" + epStr);
    leaf.appendChild(h2);

    leaf.appendChild(hr());

    var hint = document.createElement("p");
    hint.className = "hint";
    hint.innerHTML = "<b>単語をクリック</b>すると、理語辞書の該当エントリを新しいタブで直接開きます。";
    leaf.appendChild(hint);

    var story = document.createElement("div");
    story.className = "story fy";
    story.id = "story";

    parsed.blocks.forEach(function(block){
      var p = document.createElement("p");
      p.className = classifyBlock(block);
      var blockLines = block.split("\n");
      blockLines.forEach(function(line, idx){
        p.appendChild(document.createTextNode(line));
        if(idx < blockLines.length - 1) p.appendChild(document.createElement("br"));
      });
      story.appendChild(p);
    });

    leaf.appendChild(story);
    leaf.appendChild(hrBottom());
    leaf.appendChild(buildNav());

    var backP = document.createElement("p");
    backP.style.textAlign = "center";
    var backA = document.createElement("a");
    backA.className = "back";
    backA.href = "index.html";
    backA.style.fontFamily = "'Zen Kaku Gothic New', sans-serif";
    backA.textContent = "← トップに戻る";
    backP.appendChild(backA);
    leaf.appendChild(backP);

    // gloss-link every word, then wire up the font toggle
    wrapContainer(story);
    wrapContainer(h2);

    var checkbox = document.getElementById("fontToggle");
    function applyFont(useConlangFont){
      leaf.classList.toggle("latin-off", !useConlangFont);
      document.querySelectorAll(".w").forEach(function(el){
        el.textContent = useConlangFont ? transformForFont(el.dataset.word) : el.dataset.word;
      });
    }
    checkbox.addEventListener("change", function(){ applyFont(checkbox.checked); });
    applyFont(checkbox.checked);

    checkPrevNextExistence();
  }

  function hr(){ var el = document.createElement("hr"); el.className = "rule"; return el; }
  function hrBottom(){ var el = document.createElement("hr"); el.className = "rule bottom"; return el; }

  function buildNav(){
    var nav = document.createElement("div");
    nav.className = "episode-nav";
    nav.id = "episodeNav";

    var pad = epStr.length;
    var prevNum = epNum - 1;
    var nextNum = epNum + 1;

    var prevA = document.createElement("a");
    prevA.id = "prevLink";
    prevA.style.visibility = "hidden";
    if(prevNum >= 0){
      prevA.href = "episode_" + String(prevNum).padStart(pad, "0") + ".html";
      prevA.textContent = "← 前の話";
    }

    var spacer = document.createElement("span");
    spacer.className = "spacer";

    var nextA = document.createElement("a");
    nextA.id = "nextLink";
    nextA.style.visibility = "hidden";
    nextA.href = "episode_" + String(nextNum).padStart(pad, "0") + ".html";
    nextA.textContent = "次の話 →";

    nav.appendChild(prevA);
    nav.appendChild(spacer);
    nav.appendChild(nextA);
    return nav;
  }

  // show prev/next links only if the sibling file actually exists
  function checkPrevNextExistence(){
    ["prevLink", "nextLink"].forEach(function(id){
      var a = document.getElementById(id);
      if(!a || !a.href) return;
      fetch(a.href.replace(".html", ".txt"), { method: "HEAD" })
        .then(function(res){ if(res.ok) a.style.visibility = "visible"; })
        .catch(function(){ /* leave hidden */ });
    });
  }

  // ---------- 5. word wrapping for dictionary gloss links ----------
  var WORD_RE = /[A-Za-z0-9]+(?:'[A-Za-z0-9]+)*/g;

  function wrapTextNode(node){
    var text = node.nodeValue;
    if(!WORD_RE.test(text)) return;
    WORD_RE.lastIndex = 0;
    var frag = document.createDocumentFragment();
    var lastIndex = 0, mm;
    while((mm = WORD_RE.exec(text))){
      if(mm.index > lastIndex) frag.appendChild(document.createTextNode(text.slice(lastIndex, mm.index)));
      var a = document.createElement("a");
      a.className = "w";
      a.textContent = mm[0];
      a.href = DICT_BASE + encodeURIComponent(mm[0]);
      a.target = "_blank";
      a.rel = "noopener";
      a.dataset.word = mm[0];
      frag.appendChild(a);
      lastIndex = WORD_RE.lastIndex;
    }
    if(lastIndex < text.length) frag.appendChild(document.createTextNode(text.slice(lastIndex)));
    node.parentNode.replaceChild(frag, node);
  }

  function wrapContainer(root){
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var nodes = [];
    var n;
    while((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(wrapTextNode);
  }

  // ---------- 6. dz/fh/vh -> X/F/V transcription for the web font ----------
  // Any stray capital X/F/V already in the source is lowercased first so that,
  // after transcription, a capital X/F/V *only* ever means an original dz/fh/vh.
  function transformForFont(word){
    return word
      .replace(/[XFV]/g, function(c){ return c.toLowerCase(); })
      .replace(/dz/gi, "X")
      .replace(/fh/gi, "F")
      .replace(/vh/gi, "V");
  }

  // ---------- 7. gloss toast ----------
  document.addEventListener("click", function(e){
    var el = e.target.closest && e.target.closest("a.w");
    if(!el) return;
    var toast = document.getElementById("glossToast");
    if(!toast) return;
    toast.innerHTML = "<div><b>「" + escapeHtml(el.dataset.word) + "」</b>を辞書で検索しました</div>" +
      '<div class="sub">新しいタブで辞書エントリを開きました。</div>';
    toast.classList.add("show");
    clearTimeout(toast._hideTimer);
    toast._hideTimer = setTimeout(function(){ toast.classList.remove("show"); }, 3200);
  });

  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, function(c){
      return { "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c];
    });
  }
})();
