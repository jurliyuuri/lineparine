(function(){
  "use strict";

  // This repo/branch/path triple is where the episode .txt/.html files live.
  // If the repo is ever renamed or moved, update these three lines only.
  var GH_USER = "jurliyuuri";
  var GH_REPO = "lineparine";
  var GH_REF  = "master";
  var DIR_PATH = "translations/translation_texts/dAlenVilalijaLirnasti"; // no leading/trailing slash

  var LIST_API = "https://api.github.com/repos/" + GH_USER + "/" + GH_REPO + "/contents/" + DIR_PATH + "?ref=" + GH_REF;
  var CACHE_KEY = "episodeListCache:" + DIR_PATH;
  var CACHE_TTL_MS = 15 * 60 * 1000; // 15 minutes — eases pressure on the unauthenticated GitHub API rate limit

  var JP_NUMERALS = ["", "一", "ニ", "三", "四", "五", "六", "七", "八", "九", "十",
    "十一","十二","十三","十四","十五","十六","十七","十八","十九","二十",
    "二十一","二十二","二十三","二十四","二十五","二十六","二十七","二十八","二十九","三十"];

  function ordinalLabel(n){
    if(n === 0) return "プロローグ";
    if(n - 1 < JP_NUMERALS.length) return "第" + JP_NUMERALS[n-1] + "話";
    return "第" + (n-1) + "話";
  }

  function stripBom(s){
    return s.charCodeAt(0) === 0xFEFF ? s.slice(1) : s;
  }

  function extractTitle(raw){
    var lines = stripBom(raw).replace(/\r\n?/g, "\n").split("\n");
    var TITLE_MARKER = /^【xakantast/; // tolerates "【xakantasti】", "【xakantast】", "【xakantasti】】" etc.
    for(var i = 0; i < lines.length; i++){
      var line = lines[i].trim();
      if(TITLE_MARKER.test(line)){
        var inline = line.replace(TITLE_MARKER, "").replace(/^[iI】]*/, "").trim();
        if(inline) return inline;
        for(var k = i + 1; k < lines.length; k++){
          var next = lines[k].trim();
          if(next) return next;
        }
        return "";
      }
    }
    return "";
  }

  function readCache(){
    try{
      var raw = sessionStorage.getItem(CACHE_KEY);
      if(!raw) return null;
      var parsed = JSON.parse(raw);
      if(!parsed || (Date.now() - parsed.time) > CACHE_TTL_MS) return null;
      return parsed.results;
    }catch(e){ return null; }
  }

  function writeCache(results){
    try{
      sessionStorage.setItem(CACHE_KEY, JSON.stringify({ time: Date.now(), results: results }));
    }catch(e){ /* ignore quota/availability errors */ }
  }

  document.addEventListener("DOMContentLoaded", function(){
    var container = document.getElementById("episode-list");
    if(!container) return;

    var cached = readCache();
    if(cached){
      render(container, cached);
      return;
    }

    container.innerHTML = '<li class="loading" style="border:none;">話一覧を読み込んでいます…</li>';

    fetch(LIST_API, { headers: { "Accept": "application/vnd.github+json" } })
      .then(function(res){
        if(res.status === 403) throw new Error("rate-limited");
        if(!res.ok) throw new Error("contents API failed: " + res.status);
        return res.json();
      })
      .then(function(items){
        var nums = (items || [])
          .filter(function(it){ return it.type === "file" && /^episode_\d+\.txt$/.test(it.name); })
          .map(function(it){
            var digits = it.name.match(/\d+/)[0];
            return { num: parseInt(digits, 10), pad: digits };
          })
          .sort(function(a, b){ return a.num - b.num; });

        if(nums.length === 0){
          container.innerHTML = '<li class="error" style="border:none;">話が見つかりませんでした。</li>';
          return;
        }

        return Promise.all(nums.map(function(item){
          return fetch("episode_" + item.pad + ".txt")
            .then(function(res){ return res.ok ? res.text() : ""; })
            .then(function(txt){ return { item: item, title: extractTitle(txt) }; })
            .catch(function(){ return { item: item, title: "" }; });
        })).then(function(results){
          writeCache(results);
          render(container, results);
        });
      })
      .catch(function(err){
        if(String(err.message) === "rate-limited"){
          container.innerHTML = '<li class="error" style="border:none;">一覧の取得が混み合っています（GitHub APIの利用制限）。少し時間をおいて再読み込みしてください。各話へのリンクは通常どおりご利用いただけます。</li>';
        } else {
          container.innerHTML = '<li class="error" style="border:none;">一覧の取得に失敗しました。ページを再読み込みするか、しばらく待ってから再度お試しください。</li>';
        }
        console.error(err);
      });
  });

  function render(container, results){
    container.innerHTML = "";
    results.forEach(function(r, idx){
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = "episode_" + r.item.pad + ".html";
      var numSpan = document.createElement("span");
      numSpan.className = "ep-num";
      numSpan.textContent = ordinalLabel(idx);
      var titleSpan = document.createElement("span");
      titleSpan.className = "ep-title";
      titleSpan.textContent = r.title || ("episode_" + r.item.pad);
      a.appendChild(numSpan);
      a.appendChild(titleSpan);
      li.appendChild(a);
      container.appendChild(li);
    });
  }
})();
