/* 離題生活 共用互動：今天聊什麼、文章篩選、分享、電子報 */
(function () {
  function track(name, params) {
    try { if (window.gtag) window.gtag("event", name, params || {}); } catch (e) {}
  }

  /* ---------- 今天聊什麼 ---------- */
  var todayEl = document.getElementById("todayData");
  if (todayEl) {
    var TODAY = JSON.parse(todayEl.textContent);
    var sceneBtns = document.querySelectorAll(".scene-btn");
    var todaySection = document.getElementById("today");
    var siteUrl = todaySection.getAttribute("data-url");
    /* 每個情境各自洗牌，一輪 50 題看完才會重複 */
    var decks = TODAY.prompts.map(function () { return []; });
    var deal = function (s) {
      if (!decks[s].length) {
        var order = TODAY.prompts[s].map(function (_, i) { return i; });
        for (var i = order.length - 1; i > 0; i--) {
          var j = Math.floor(Math.random() * (i + 1)), t = order[i]; order[i] = order[j]; order[j] = t;
        }
        decks[s] = order;
      }
      return decks[s].shift();
    };
    var sceneIdx = 0, promptIdx = 0;
    var showPrompt = function () {
      var item = TODAY.prompts[sceneIdx][promptIdx];
      document.getElementById("promptQ").textContent = item.q;
      document.getElementById("promptP").innerHTML = "";
      var strong = document.createElement("strong");
      strong.textContent = "今日練習：";
      document.getElementById("promptP").appendChild(strong);
      document.getElementById("promptP").appendChild(document.createTextNode(item.p));
      sceneBtns.forEach(function (x) { x.classList.toggle("active", parseInt(x.getAttribute("data-scene"), 10) === sceneIdx); });
      var fbk = document.getElementById("todayFeedback"); if (fbk) fbk.textContent = "";
    };
    var setScene = function (s) { sceneIdx = s; promptIdx = deal(s); showPrompt(); };
    sceneBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        setScene(parseInt(b.getAttribute("data-scene"), 10));
        track("today_scene", { scene: TODAY.scenes[sceneIdx] });
      });
    });
    var shuffle = document.getElementById("shuffleBtn");
    if (shuffle) shuffle.addEventListener("click", function () {
      promptIdx = deal(sceneIdx);
      showPrompt();
      track("today_shuffle", { scene: TODAY.scenes[sceneIdx] });
    });
    /* 分享連結 ?s=情境&p=題號 會直接打開那一題 */
    var qs = new URLSearchParams(location.search);
    var qsS = parseInt(qs.get("s"), 10), qsP = parseInt(qs.get("p"), 10);
    if (TODAY.prompts[qsS] && TODAY.prompts[qsS][qsP]) {
      sceneIdx = qsS; promptIdx = qsP; showPrompt();
      setTimeout(function () { todaySection.scrollIntoView({ behavior: "smooth" }); }, 300);
    } else {
      setScene(0);
    }

    /* ---------- 今天聊什麼：分享 ---------- */
    var promptLink = function (source) {
      return siteUrl + "?s=" + sceneIdx + "&p=" + promptIdx + "&utm_source=" + source + "&utm_medium=share&utm_campaign=today#today";
    };
    var promptText = function () {
      var item = TODAY.prompts[sceneIdx][promptIdx];
      return "【" + TODAY.scenes[sceneIdx] + "】" + item.q + "\n今日練習：" + item.p + "\n——離題生活・今天聊什麼";
    };
    var tfb = function (m) { document.getElementById("todayFeedback").textContent = m; };
    var tcopy = function (text, msg) {
      var done = function () { tfb(msg); };
      var fallback = function () {
        var ta = document.createElement("textarea");
        ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); done(); } catch (e) { tfb("複製失敗，請再試一次。"); }
        document.body.removeChild(ta);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, fallback); else fallback();
    };
    var twin = function (u) { window.open(u, "_blank", "noopener,width=680,height=680"); };
    var tWrap = function (ctx, text, maxW) {
      var lines = [], line = "";
      for (var i = 0; i < text.length; i++) {
        var ch = text.charAt(i);
        if (ctx.measureText(line + ch).width > maxW && line) { lines.push(line); line = ch; } else line += ch;
      }
      if (line) lines.push(line);
      return lines;
    };
    var todayCard = function () {
      var item = TODAY.prompts[sceneIdx][promptIdx];
      var c = document.createElement("canvas"); c.width = 1080; c.height = 1350;
      var x = c.getContext("2d");
      x.fillStyle = "#232220"; x.fillRect(0, 0, 1080, 1350);
      x.strokeStyle = "#3a3935"; x.lineWidth = 2; x.strokeRect(48, 48, 984, 1254);
      x.textAlign = "left";
      x.fillStyle = "#e3b7a9"; x.font = "700 26px 'Noto Sans TC', sans-serif";
      x.fillText("T O D A Y ' S   T O P I C　｜　" + TODAY.scenes[sceneIdx], 110, 170);
      x.font = "600 62px 'Noto Serif TC', serif";
      var qL = tWrap(x, item.q, 860).slice(0, 5);
      x.font = "400 36px 'Noto Sans TC', sans-serif";
      var pL = tWrap(x, item.p, 860).slice(0, 6);
      var blockH = qL.length * 92 + 50 + 62 + pL.length * 58;
      var y = Math.max(300, 230 + (900 - blockH) / 2 + 60);
      x.fillStyle = "#ffffff"; x.font = "600 62px 'Noto Serif TC', serif";
      qL.forEach(function (ln) { x.fillText(ln, 110, y); y += 92; });
      y += 50;
      x.fillStyle = "#e3b7a9"; x.font = "700 32px 'Noto Sans TC', sans-serif";
      x.fillText("今日練習", 110, y); y += 62;
      x.fillStyle = "#cfcabe"; x.font = "400 36px 'Noto Sans TC', sans-serif";
      pL.forEach(function (ln) { x.fillText(ln, 110, y); y += 58; });
      x.fillStyle = "#ece9e2"; x.font = "600 34px 'Noto Serif TC', serif";
      x.fillText("離題生活", 110, 1220);
      x.fillStyle = "#8a867c"; x.font = "500 22px 'Noto Sans TC', sans-serif";
      x.fillText("日子重複的時候，就離題一下", 110, 1262);
      return c;
    };
    document.querySelectorAll("[data-today-share]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var k = btn.getAttribute("data-today-share");
        track("share", { method: k, item_id: "today-" + sceneIdx + "-" + promptIdx, content_type: "today_prompt" });
        if (k === "line") twin("https://social-plugins.line.me/lineit/share?url=" + encodeURIComponent(promptLink("line")) + "&text=" + encodeURIComponent(promptText()));
        else if (k === "facebook") twin("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(promptLink("facebook")) + "&quote=" + encodeURIComponent(promptText()));
        else if (k === "threads") twin("https://www.threads.net/intent/post?text=" + encodeURIComponent(promptText() + "\n" + promptLink("threads")));
        else if (k === "copy") tcopy(promptText() + "\n" + promptLink("copy"), "已複製，可以貼給朋友，或貼在備忘錄留給自己。");
        else if (k === "card") {
          var save = function () {
            var a = document.createElement("a");
            a.download = "liti-today-" + sceneIdx + "-" + promptIdx + ".png";
            a.href = todayCard().toDataURL("image/png");
            document.body.appendChild(a); a.click(); document.body.removeChild(a);
            tfb("圖卡已下載，可以發 IG 限時動態，或存起來當今天的提醒。");
          };
          if (document.fonts && document.fonts.ready) document.fonts.ready.then(save); else save();
        }
      });
    });
  }

  /* ---------- 全部文章：分類篩選與搜尋 ---------- */
  var grid = document.getElementById("articleGrid");
  if (grid && document.querySelector(".chips")) {
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));
    var emptyState = document.getElementById("emptyState");
    var chips = document.querySelectorAll(".chip");
    var currentCat = "全部", keyword = "";
    var apply = function () {
      var shown = 0, kw = keyword.trim();
      cards.forEach(function (c) {
        var ok = (currentCat === "全部" || c.getAttribute("data-cat") === currentCat) &&
          (!kw || c.textContent.indexOf(kw) !== -1);
        c.hidden = !ok;
        if (ok) shown++;
      });
      if (emptyState) emptyState.style.display = shown ? "none" : "block";
    };
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        currentCat = c.getAttribute("data-cat");
        chips.forEach(function (x) { x.classList.toggle("active", x === c); });
        apply();
      });
    });
    var search = document.getElementById("searchInput");
    var searchTimer;
    if (search) search.addEventListener("input", function (e) {
      keyword = e.target.value;
      apply();
      clearTimeout(searchTimer);
      searchTimer = setTimeout(function () { if (keyword.trim()) track("search", { search_term: keyword.trim() }); }, 1200);
    });
  }

  /* ---------- 分享 ---------- */
  var shareBar = document.getElementById("shareBar");
  if (shareBar) {
    var title = shareBar.getAttribute("data-title");
    var hook = shareBar.getAttribute("data-hook");
    var baseUrl = shareBar.getAttribute("data-url");
    var slug = shareBar.getAttribute("data-slug");
    var urlFor = function (source) {
      return baseUrl + "?utm_source=" + source + "&utm_medium=share&utm_campaign=" + encodeURIComponent(slug);
    };
    var shareText = function () { return title + "｜離題生活" + (hook ? " — " + hook : ""); };
    var fb = function (msg) { document.getElementById("shareFeedback").textContent = msg; };
    var copyText = function (text, doneMsg) {
      var done = function () { fb(doneMsg); };
      var fallback = function () {
        var ta = document.createElement("textarea");
        ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); done(); } catch (e) { fb("複製失敗，請再試一次。"); }
        document.body.removeChild(ta);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, fallback);
      else fallback();
    };
    var openWin = function (u) { window.open(u, "_blank", "noopener,width=680,height=680"); };
    var igPanel = document.getElementById("igPanel");
    document.querySelectorAll("[data-share]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var kind = btn.getAttribute("data-share");
        track("share", { method: kind, item_id: slug });
        if (kind !== "instagram") igPanel.hidden = true;
        if (kind === "line") openWin("https://social-plugins.line.me/lineit/share?url=" + encodeURIComponent(urlFor("line")) + "&text=" + encodeURIComponent(shareText()));
        else if (kind === "facebook") openWin("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlFor("facebook")));
        else if (kind === "threads") openWin("https://www.threads.net/intent/post?text=" + encodeURIComponent(shareText() + " " + urlFor("threads")));
        else if (kind === "instagram") { igPanel.hidden = !igPanel.hidden; fb(igPanel.hidden ? "" : "選「下載分享圖卡」就能把這篇帶去 Instagram。"); }
        else if (kind === "copy") copyText(shareText() + "\n" + urlFor("copy"), "分享文字和連結已複製，去貼給想分享的人吧。");
      });
    });
    document.getElementById("igCopyBtn").addEventListener("click", function () {
      copyText(shareText() + "\n" + urlFor("instagram"), "分享文字已複製，可以貼到 Instagram 貼文或訊息裡。");
    });
    var wrapLines = function (ctx, text, maxWidth) {
      var lines = [], line = "";
      for (var i = 0; i < text.length; i++) {
        var ch = text.charAt(i);
        if (ctx.measureText(line + ch).width > maxWidth && line) { lines.push(line); line = ch; } else line += ch;
      }
      if (line) lines.push(line);
      return lines;
    };
    document.getElementById("downloadCardBtn").addEventListener("click", function () {
      track("share_card_download", { item_id: slug });
      var canvas = document.createElement("canvas");
      canvas.width = 1080; canvas.height = 1080;
      var ctx = canvas.getContext("2d");
      ctx.fillStyle = "#f2efe9"; ctx.fillRect(0, 0, 1080, 1080);
      ctx.strokeStyle = "#e9e4da"; ctx.lineWidth = 2; ctx.strokeRect(48, 48, 984, 984);
      ctx.textAlign = "center";
      ctx.fillStyle = "#8b5548"; ctx.font = "700 30px 'Noto Sans TC', sans-serif";
      ctx.fillText("離 題 生 活", 540, 170);
      ctx.font = "500 20px 'Noto Sans TC', sans-serif"; ctx.fillStyle = "#8a867c";
      ctx.fillText("I N D E P E N D E N T   L I F E   J O U R N A L", 540, 214);
      ctx.fillStyle = "#26241f"; ctx.font = "600 58px 'Noto Serif TC', serif";
      var tl = wrapLines(ctx, title, 820).slice(0, 4);
      var y = 420 - (tl.length - 1) * 44;
      tl.forEach(function (ln) { ctx.fillText(ln, 540, y); y += 88; });
      if (hook) {
        ctx.fillStyle = "#8b5548"; ctx.font = "500 36px 'Noto Serif TC', serif";
        var hy = y + 56;
        wrapLines(ctx, hook, 800).slice(0, 3).forEach(function (ln) { ctx.fillText(ln, 540, hy); hy += 56; });
      }
      ctx.fillStyle = "#8a867c"; ctx.font = "500 24px 'Noto Serif TC', serif";
      ctx.fillText("日子重複的時候，就離題一下", 540, 950);
      var save = function () {
        var a = document.createElement("a");
        a.download = "liti-life-" + slug + ".png";
        a.href = canvas.toDataURL("image/png");
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        fb("分享圖卡已下載，打開 Instagram 就能貼上去了。");
      };
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(save); else save();
    });
  }

  /* ---------- 電子報 ---------- */
  var form = document.getElementById("subscribeForm");
  if (form) {
    var input = document.getElementById("subscribeEmail");
    var msg = document.getElementById("subscribeMsg");
    var idle = msg.textContent;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(input.value.trim())) {
        msg.textContent = "請輸入正確的 e-mail 格式，例如 name@example.com。";
        msg.className = "subscribe-msg is-error"; input.focus(); return;
      }
      track("subscribe_attempt");
      var btn = form.querySelector("button");
      btn.disabled = true;
      msg.textContent = "寄送中……";
      msg.className = "subscribe-msg";
      var xhr = new XMLHttpRequest();
      xhr.open("POST", form.getAttribute("data-endpoint"), true);
      xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
      xhr.onreadystatechange = function () {
        if (xhr.readyState !== 4) return;
        btn.disabled = false;
        if (xhr.status >= 200 && xhr.status < 300) {
          track("generate_lead", { method: "newsletter" });
          msg.textContent = "還差一步：確認信已寄到你的信箱，點信裡的連結就完成訂閱了。沒看到的話，記得看一下垃圾郵件匣。";
          msg.className = "subscribe-msg is-ok";
          input.value = "";
        } else {
          msg.textContent = "現在好像塞車了，請稍後再試一次。";
          msg.className = "subscribe-msg is-error";
        }
      };
      xhr.send("email=" + encodeURIComponent(input.value.trim()));
    });
    input.addEventListener("input", function () {
      if (msg.className.indexOf("is-error") !== -1) { msg.textContent = idle; msg.className = "subscribe-msg"; }
    });
  }

  /* ---------- 追蹤：外連社群、閱讀完成 ---------- */
  document.querySelectorAll('a[href^="http"]').forEach(function (a) {
    if (a.hostname !== location.hostname) a.addEventListener("click", function () {
      track("outbound_click", { link_domain: a.hostname, link_url: a.href });
    });
  });
  var articleEnd = document.getElementById("articleEnd");
  if (articleEnd && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (ents) {
      if (ents[0].isIntersecting) { track("article_read_complete", { item_id: articleEnd.getAttribute("data-slug") }); io.disconnect(); }
    });
    io.observe(articleEnd);
  }
})();

/* ---------- 離友內心戲投稿 ---------- */
(function () {
  var f = document.getElementById("submitForm");
  if (!f) return;
  var msg = document.getElementById("submitMsg");
  f.addEventListener("submit", function (e) {
    e.preventDefault();
    var v = function (n) { var el = f.elements[n]; return el ? (el.value || "").trim() : ""; };
    var scene = (f.querySelector('input[name="scene"]:checked') || {}).value || "";
    if (!v("story") && !v("thought")) { msg.textContent = "至少寫一下場景，或你心裡演的那句。"; msg.className = "submit-msg is-error"; return; }
    if (!f.elements.agree.checked) { msg.textContent = "請勾選同意改寫並匿名刊登，我們才能使用這段內心戲。"; msg.className = "submit-msg is-error"; return; }
    var body = "【發生在哪裡】" + scene + "\n\n【那個場景】\n" + v("story") + "\n\n【我嘴上說的】\n" + v("said") +
      "\n\n【我心裡演的】\n" + v("thought") + "\n\n【刊出暱稱】" + (v("nick") || "（不署名）") + "\n\n我同意離題生活改寫並匿名刊登這段內容。";
    try { if (window.gtag) window.gtag("event", "submit_story", { scene: scene }); } catch (err) {}
    location.href = "mailto:" + f.getAttribute("data-email") + "?subject=" + encodeURIComponent("離友內心戲投稿｜" + scene) + "&body=" + encodeURIComponent(body);
    msg.textContent = "已經幫你打開電子郵件，按下寄出就完成了。謝謝你的內心戲！";
    msg.className = "submit-msg";
  });
})();
