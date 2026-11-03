/* 離題生活 共用互動：今天聊什麼、文章篩選、分享、電子報 */
(function () {
  function track(name, params) {
    try { if (window.gtag) window.gtag("event", name, params || {}); } catch (e) {}
  }

  /* ---------- 今天聊什麼 ---------- */
  var todayEl = document.getElementById("todayData");
  if (todayEl) {
    var TODAY = JSON.parse(todayEl.textContent);
    var sceneIdx = 0, promptIdx = 0;
    var sceneBtns = document.querySelectorAll(".scene-btn");
    var showPrompt = function () {
      var list = TODAY.prompts[sceneIdx];
      var item = list[promptIdx % list.length];
      document.getElementById("promptQ").textContent = item.q;
      document.getElementById("promptP").innerHTML = item.p;
    };
    sceneBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        sceneBtns.forEach(function (x) { x.classList.remove("active"); });
        b.classList.add("active");
        sceneIdx = parseInt(b.getAttribute("data-scene"), 10);
        promptIdx = 0;
        showPrompt();
        track("today_scene", { scene: TODAY.scenes[sceneIdx] });
      });
    });
    var shuffle = document.getElementById("shuffleBtn");
    if (shuffle) shuffle.addEventListener("click", function () {
      promptIdx = (promptIdx + 1) % TODAY.prompts[sceneIdx].length;
      showPrompt();
      track("today_shuffle", { scene: TODAY.scenes[sceneIdx] });
    });
    showPrompt();
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
