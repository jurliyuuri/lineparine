(function(){
  "use strict";

  // This repo/branch/path triple is where the episode .txt/.html files live.
  // If the repo is ever renamed or moved, update these three lines only.
  var GH_USER = "jurliyuuri";
  var GH_REPO = "lineparine";
  var GH_REF  = "master";
  var DIR_PATH = "translations/translation_texts/dAlenVilalijaLirnasti"; // no leading/trailing slash

  var LIST_API = "https://data.jsdelivr.com/v1/packages/gh/" + GH_USER + "/" + GH_REPO + "@" + GH_REF + "?structure=flat";

  var JP_NUMERALS = ["", "一", "ニ", "三", "四", "五", "六", "七", "八", "九", "十",
    "十一","十二","十三","十四","十五","十六","十七","十八","十九","二十",
    "二十一","二十二","二十三","二十四","二十五","二十六","二十七","二十八","二十九","三十"];

  function ordinalLabel(n){
    if(n === 0) return "プロローグ";
    if(n - 1 < JP_NUMERALS.length) return "第" + JP_NUMERALS[n-1] + "話";
    return "第" + (n-1) + "話";
  }

  document.addEventListener("DOMContentLoaded", function(){
    var container = document.getElementById("episode-list");
    if(!container) return;

    container.innerHTML = '<li class="loading" style="border:none;">話一覧を読み込んでいます…</li>';

    fetch(LIST_API)
      .then(function(res){
        if(!res.ok) throw new Error("jsDelivr list failed: " + res.status);
        return res.json();
      })
      .then(function(data){
        var prefix = "/" + DIR_PATH + "/";
        var files = (data.files || [])
          .map(function(f){ return f.name || f.path || ""; })
          .filter(function(name){ return name.indexOf(prefix) === 0; })
          .map(function(name){ return name.slice(prefix.length); })
          .filter(function(name){ return /^episode_\d+\.txt$/.test(name); });

        var nums = files.map(function(name){
          return { num: parseInt(name.match(/\d+/)[0], 10), pad: name.match(/\d+/)[0] };
        }).sort(function(a,b){ return a.num - b.num; });

        if(nums.length === 0){
          container.innerHTML = '<li class="error" style="border:none;">話が見つかりませんでした。</li>';
          return;
        }

        return Promise.all(nums.map(function(item){
          return fetch(DIR_PATH + "/episode_" + item.pad + ".txt")
            .then(function(res){ return res.ok ? res.text() : ""; })
            .then(function(txt){ return { item: item, title: extractTitle(txt) }; })
            .catch(function(){ return { item: item, title: "" }; });
        })).then(function(results){
          container.innerHTML = "";
          results.forEach(function(r, idx){
            var li = document.createElement("li");
            var a = document.createElement("a");
            a.href = DIR_PATH + "/episode_" + r.item.pad + ".html";
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
        });
      })
      .catch(function(err){
        container.innerHTML = '<li class="error" style="border:none;">一覧の取得に失敗しました。ページを再読み込みするか、しばらく待ってから再度お試しください。</li>';
        console.error(err);
      });
  });

  function extractTitle(raw){
    var lines = raw.replace(/\r\n?/g, "\n").split("\n");
    for(var i = 0; i < lines.length; i++){
      if(lines[i].trim() === "【xakantasti】") return (lines[i+1] || "").trim();
    }
    return "";
  }
})();
