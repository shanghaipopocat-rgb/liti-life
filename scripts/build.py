#!/usr/bin/env python3
"""離題生活 網站產生器

用法：python3 scripts/build.py
讀取 content/ 裡的 site.json、articles.json、today.json，
產生首頁、分類頁、文章頁、關於頁、404、sitemap.xml。

新增文章：在 content/articles.json 加一筆，圖片放 images/<名稱>.webp 與 .jpg，再跑一次本程式。
"""
import json, html, os, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "content"
SITE = json.loads((C / "site.json").read_text(encoding="utf-8"))
ARTS = json.loads((C / "articles.json").read_text(encoding="utf-8"))
TODAY = json.loads((C / "today.json").read_text(encoding="utf-8"))
ARTS.sort(key=lambda a: a.get("date", ""), reverse=True)
CATS = {c["name"]: c for c in SITE["categories"]}
BASE = SITE["baseUrl"].rstrip("/")
WEEK = "一二三四五六日"

e = html.escape
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 12h16m-6-6 6 6-6 6"/></svg>'
ICONS = {
    "facebook": '<path d="M15 4h-2.5A3.5 3.5 0 0 0 9 7.5V10H6.5v3H9v7h3.2v-7h2.6l.7-3h-3.3V7.8c0-.5.4-.8.9-.8H15V4Z"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="4.5"/><circle cx="12" cy="12" r="3.8"/><circle cx="17.2" cy="6.8" r="0.6" fill="currentColor"/>',
    "threads": '<circle cx="12" cy="12" r="3.2"/><path d="M12 3.5c2.8 1 4.2 3.4 4 6.6-.1 3.4-1.8 5.4-4.2 5.4-2 0-3.3-1.3-3.3-3.2 0-2 1.5-3.4 3.7-3.4 1.5 0 2.7.7 3.3 1.8M17.5 5.6c1.9 1.9 3 4.3 3 6.9 0 4.7-3.4 7.5-8.5 7.5-4.9 0-8.5-3.6-8.5-8s3.6-8 8.5-8c2 0 3.8.6 5.2 1.7"/>',
    "line": '<path d="M21 11.5c0 4.7-4 8.5-9 8.5-1 0-2-.2-2.9-.5L4 21l1.6-3.9C4.6 15.6 3 13.7 3 11.5 3 6.8 7 3 12 3s9 3.8 9 8.5Z"/>',
    "copy": '<path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7L12.7 18.3"/>',
}
def icon(k): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">{ICONS[k]}</svg>'

def cat_url(r, cat): return f'{r}columns/{CATS[cat]["slug"]}/'
def art_url(r, a): return f'{r}articles/{a["id"]}/'

def fmt_date(d):
    import datetime
    dt = datetime.date.fromisoformat(d)
    return f"{dt.year} 年 {dt.month} 月 {dt.day} 日"

def picture(r, a, cls="", lazy=True, alt=None):
    alt = e(alt if alt is not None else a.get("imgAlt", ""))
    load = ' loading="lazy"' if lazy else ""
    return (f'<picture><source srcset="{r}images/{a["img"]}.webp" type="image/webp" />'
            f'<img src="{r}images/{a["img"]}.jpg" alt="{alt}"{load} decoding="async" class="{cls}" /></picture>')

def cover(r, a):
    if a.get("img"):
        kind = f'<span class="img-kind">{e(a["kind"])}</span>' if a.get("kind") else ""
        return f'<div class="cover">{picture(r, a)}{kind}</div>'
    return (f'<div class="cover"><div class="cover-typo"><span class="small">{e(a.get("typoSmall",""))}</span>'
            f'<span class="big">{e(a.get("typo",""))}</span></div></div>')

def card(r, a):
    return (f'<a class="card" href="{art_url(r,a)}" data-cat="{e(a["cat"])}">{cover(r,a)}'
            f'<span class="cat-label">{e(a["cat"])}</span><h3>{e(a["title"])}</h3>'
            f'<p>{e(a["excerpt"])}</p><div class="hook">{e(a.get("hook",""))}</div></a>')

def head(r, title, desc, url, image=None, og_type="website"):
    image = image or f"{BASE}/images/featured-work.jpg"
    ga = SITE["gaId"]
    return f'''<!doctype html>
<html lang="zh-Hant">
  <head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga}');
    </script>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="color-scheme" content="light" />
    <title>{e(title)}</title>
    <meta name="description" content="{e(desc)}" />
    <link rel="canonical" href="{url}" />
    <meta property="og:site_name" content="{SITE["name"]}" />
    <meta property="og:type" content="{og_type}" />
    <meta property="og:title" content="{e(title)}" />
    <meta property="og:description" content="{e(desc)}" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{image}" />
    <meta property="og:locale" content="zh_TW" />
    <meta name="twitter:card" content="summary_large_image" />
    <link rel="icon" type="image/png" href="{r}images/mascot.png" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@500;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="{r}assets/style.css" />
  </head>
  <body>'''

def masthead(r, compact):
    if compact:
        return f'''
    <header class="wrap">
      <div class="masthead compact">
        <a href="{r}" aria-label="回到離題生活首頁">
          <figure class="masthead-visual">{picture(r, {"img":"mascot"}, lazy=False, alt="離題生活小人：提著公事包跑過一條線，從西裝換成休閒服")}</figure>
          <div class="masthead-lockup"><div class="masthead-text">
            <div class="site-name">{SITE["name"]}</div>
            <div class="slogan">{SITE["slogan"]}</div>
          </div></div>
        </a>
      </div>
    </header>'''
    return f'''
    <header class="wrap">
      <div class="topstrip">
        <span id="todayDate"></span>
        <span class="en">{SITE["nameEn"]}</span>
        <span>{SITE["tagline"]}</span>
      </div>
      <div class="masthead">
        <figure class="masthead-visual">{picture(r, {"img":"mascot"}, lazy=False, alt="離題生活小人：提著公事包跑過一條線，從西裝換成休閒服")}</figure>
        <div class="masthead-lockup"><div class="masthead-text">
          <h1>{SITE["name"]}</h1>
          <div class="journal-en">{SITE["nameEn"]}</div>
          <div class="slogan">{SITE["slogan"]}</div>
        </div></div>
      </div>
    </header>
    <script>(function(){{var d=new Date(),w="{WEEK}";document.getElementById("todayDate").textContent=d.getFullYear()+" 年 "+(d.getMonth()+1)+" 月 "+d.getDate()+" 日　星期"+w[(d.getDay()+6)%7];}})();</script>'''

def nav(r, current=""):
    items = [(c["name"], cat_url(r, c["name"]), "") for c in SITE["categories"]]
    items += [("全部文章", f"{r}articles/", ""), ("今天聊什麼", f"{r}#today", "accent-link"), ("離友內心戲", f"{r}submit/", ""), ("關於離題", f"{r}about/", "")]
    links = "".join(
        f'<a href="{u}"{" class=%s" % chr(34)+cls+chr(34) if cls else ""}{" aria-current=%spage%s" % (chr(34),chr(34)) if name==current else ""}>{name}</a>'
        for name, u, cls in items)
    return f'\n    <nav class="mainnav" aria-label="主選單"><div class="wrap">{links}</div></nav>'

def author_note(r):
    a = SITE.get("author")
    if not a: return ""
    lines = "".join(f"<p>{e(x)}</p>" for x in a["lines"])
    return f'''
    <section class="author-note wrap" aria-label="關於寫的人">
      <div class="author-inner">
        {picture(r, {"img":"mascot"}, alt="黎題")}
        <div class="author-text">
          <span class="tag-en">FROM THE WRITER</span>
          {lines}
          <div class="author-sign">—— {e(a["name"])}　<a href="{r}submit/">寫給我 →</a></div>
        </div>
      </div>
    </section>'''

def subscribe():
    return f'''
    <section class="subscribe wrap" id="subscribe" aria-label="電子報訂閱">
      <div class="subscribe-inner">
        <span class="tag-en">NEWSLETTER</span>
        <h2>把離題，寄到你的信箱</h2>
        <p class="intro">{SITE["newsletterIntro"]}</p>
        <form class="subscribe-form" id="subscribeForm" data-endpoint="{SITE["newsletterEndpoint"]}" novalidate>
          <input type="email" id="subscribeEmail" name="email" placeholder="輸入你的 e-mail" aria-label="電子信箱" autocomplete="email" inputmode="email" />
          <button type="submit">訂閱</button>
        </form>
        <p class="subscribe-msg" id="subscribeMsg" role="status" aria-live="polite">只寄離題生活的文章，不寄廣告，隨時可以取消。</p>
      </div>
    </section>'''

def footer(r):
    soc = "".join(f'<a href="{s["url"]}" target="_blank" rel="noopener noreferrer">{icon(s["key"])}<span>{s["label"]}</span></a>' for s in SITE["social"])
    fnav = "".join(f'<a href="{cat_url(r,c["name"])}">{c["name"]}</a>' for c in SITE["categories"])
    return f'''
    <footer>
      <div class="wrap">
        <div class="foot-layout">
          {picture(r, {"img":"mascot"}, alt="")}
          <div class="foot-content">
            <div class="foot-name">{SITE["name"]}</div>
            <div class="foot-en">{SITE["nameEn"]}</div>
            <div class="foot-slogan">{SITE["slogan"]}</div>
            <div class="foot-nav">{fnav}<a href="{r}articles/">全部文章</a><a href="{r}about/">關於離題</a><a href="{r}#subscribe">訂閱電子報</a></div>
            <div class="foot-social" aria-label="離題生活社群媒體">
              <div class="foot-social-head"><span class="foot-social-label">離題生活社群媒體</span><span class="foot-social-en">FOLLOW US</span></div>
              <p class="foot-social-intro">在社群上繼續離題，追蹤最新文章與日常碎念。</p>
              <div class="foot-social-links">{soc}</div>
            </div>
          </div>
        </div>
        <div class="copy">© 2026 {SITE["name"]} {SITE["nameEn"]}</div>
      </div>
    </footer>'''

def tail(r, extra=""):
    return f'{extra}\n    <script src="{r}assets/site.js" defer></script>\n  </body>\n</html>\n'

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def body_html(a):
    out = []
    for b in a["body"]:
        if isinstance(b, str): out.append(f"<p>{e(b)}</p>")
        elif "quote" in b: out.append(f'<blockquote class="epigraph"><p>「{e(b["quote"])}」</p><cite>—— {e(b["cite"])}</cite></blockquote>')
        elif "heading" in b: out.append(f'<h2 class="subhead">{e(b["heading"])}</h2>')
        elif "tagline" in b: out.append(f'<p class="tagline">{e(b["tagline"])}</p>')
        elif "practiceCards" in b:
            cs = "".join(
                f'<article class="practice-card"><div class="practice-card-top"><span class="practice-card-kicker">{e(b.get("kicker","辦公室界線版"))}</span>'
                f'<span class="practice-card-num">{e(c["num"])}</span></div><h4>{e(c["title"])}{"" if (c["title"].startswith("「") and c["title"].endswith("」")) else "："}</h4><p>{e(c["text"])}</p>'
                f'<div class="practice-card-foot"><span>離題生活</span><span>INDEPENDENT LIFE JOURNAL</span></div></article>'
                for c in b["practiceCards"])
            out.append(f'<div class="practice-cards">{cs}</div>')
    return "\n          ".join(out)

def share_bar(a, url):
    btns = "".join(f'<button class="share-btn" type="button" data-share="{k}">{icon(k)}{lbl}</button>'
                   for k, lbl in [("line","LINE"),("facebook","Facebook"),("threads","Threads"),("instagram","Instagram"),("copy","複製分享文字")])
    return f'''
        <div class="share-bar" id="shareBar" data-title="{e(a["title"])}" data-hook="{e(a.get("hook",""))}" data-url="{url}" data-slug="{a["id"]}">
          <div class="share-head"><span class="share-label">分享這篇</span><span class="share-en">SHARE</span></div>
          <div class="share-row">{btns}</div>
          <div class="ig-panel" id="igPanel" hidden>
            <p>Instagram 不能直接分享網頁連結。可以下載這篇的分享圖卡，貼到貼文或限時動態；也可以複製分享文字，貼到貼文或訊息裡。</p>
            <div class="ig-actions">
              <button class="share-btn solid" type="button" id="downloadCardBtn">下載分享圖卡</button>
              <button class="share-btn" type="button" id="igCopyBtn">複製分享文字</button>
            </div>
          </div>
          <p class="share-feedback" id="shareFeedback" role="status" aria-live="polite"></p>
        </div>'''

# ---------------- pages ----------------
def build_home():
    r = "./"
    feat = next((a for a in ARTS if a.get("featured")), ARTS[0])
    wide = next((a for a in ARTS if a.get("wide") and a is not feat), None)
    latest = [a for a in ARTS if a is not feat and a is not wide][:6]
    today_btns = "".join(f'<button class="today-share-btn" type="button" data-today-share="{k}" aria-label="{lbl}" title="{lbl}">{icon(ic)}<span>{lbl}</span></button>'
        for k, ic, lbl in [("line","line","LINE"),("facebook","facebook","Facebook"),("threads","threads","Threads"),("card","instagram","下載圖卡"),("copy","copy","複製")])
    scenes = "".join(f'<button class="scene-btn{" active" if i==0 else ""}" data-scene="{i}">{e(s)}</button>' for i, s in enumerate(TODAY["scenes"]))
    cats = "".join(f'''
        <div class="cat-item">
          <div class="num">{c["num"]}<span class="role">{c["role"]}</span></div>
          <h3>{c["name"]}</h3>
          <p>{c["desc"]}</p>
          <a class="more" href="{cat_url(r,c["name"])}">看這個分類 {ARROW}</a>
        </div>''' for c in SITE["categories"])
    wide_html = ""
    if wide:
        wide_html = f'''
        <a class="wide-card" href="{art_url(r,wide)}">
          {cover(r, wide)}
          <div class="text"><span class="cat-label">{e(wide["cat"])}</span><h3>{e(wide["title"])}</h3><p>{e(wide["excerpt"])}</p><div class="hook">{e(wide.get("hook",""))}</div></div>
        </a>'''
    page = head(r, f'{SITE["name"]}｜{SITE["slogan"]}', SITE["description"], f"{BASE}/") + masthead(r, False) + nav(r) + f'''
    <main class="wrap">
      <section class="statement">
        <p class="lead">{SITE["statementLead"]}</p>
        <p class="sub">{SITE["statementSub"]}</p>
      </section>

      <section class="featured" aria-label="本期精選">
        <div class="section-tag"><span class="tag-en">FEATURED</span><span class="tag-zh">本期精選</span></div>
        <div class="featured-grid">
          <figure>
            <div class="fig-media">{picture(r, feat, lazy=False)}<span class="img-kind">{e(feat.get("kind",""))}</span></div>
            <figcaption>{e(feat.get("caption",""))}</figcaption>
          </figure>
          <div>
            <span class="cat-label">{e(feat["cat"])}</span>
            <h2>{e(feat["title"])}</h2>
            <p>{e(feat["excerpt"])}</p>
            <div class="hook">{e(feat.get("hook",""))}</div>
            <a class="read-btn" href="{art_url(r,feat)}">開始閱讀 {ARROW}</a>
          </div>
        </div>
      </section>

      <section id="latest" aria-label="最新文章">
        <div class="section-tag" style="margin-top:72px;"><span class="tag-en">LATEST</span><span class="tag-zh">最新文章</span></div>
        <div class="grid">{"".join(card(r,a) for a in latest)}</div>
        {wide_html}
        <div class="see-all"><a href="{r}articles/">看全部文章</a></div>
      </section>
    </main>

    <section class="today" id="today" aria-label="今天聊什麼" data-url="{BASE}/">
      <div class="wrap">
        <span class="tag-en">TODAY'S TOPIC</span>
        <h2>今天聊什麼</h2>
        <p class="intro">日子一樣的時候，先離題三分鐘。<span class="intro-more">選一個你現在的狀態，每個狀態有 50 題，沒有測驗結果，也沒有建議清單，只有一個問題，和一個小小的出口。</span></p>
        <div class="scene-row" role="group" aria-label="選擇現在的狀態">{scenes}</div>
        <div class="prompt-card">
          <p class="q" id="promptQ"></p>
          <p class="practice" id="promptP"></p>
          <button class="shuffle-btn" id="shuffleBtn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M16 3h5v5M4 20 21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/></svg>換一題</button>
          <div class="today-share">
            <span class="today-share-label">分享這一題，給朋友或給自己</span>
            <div class="today-share-row">{today_btns}</div>
            <p class="today-feedback" id="todayFeedback" role="status" aria-live="polite"></p>
          </div>
        </div>
      </div>
    </section>
    <script type="application/json" id="todayData">{json.dumps(TODAY, ensure_ascii=False)}</script>

    <section class="categories wrap" id="columns" aria-label="三大分類">
      <div class="section-tag"><span class="tag-en">COLUMNS</span><span class="tag-zh">看見、點破，然後離題一下</span></div>
      <div class="cat-grid">{cats}</div>
    </section>
''' + author_note(r) + subscribe() + footer(r) + tail(r)
    write("index.html", page)

def build_all_articles():
    r = "../"
    chips = '<button class="chip active" data-cat="全部">全部</button>' + "".join(
        f'<button class="chip" data-cat="{c["name"]}">{c["name"]}</button>' for c in SITE["categories"])
    page = head(r, f'全部文章｜{SITE["name"]}', "離題生活全部文章：生活異思、荒謬觀察、人生練習。", f"{BASE}/articles/") + masthead(r, True) + nav(r, "全部文章") + f'''
    <main class="wrap">
      <div class="crumb"><a href="{r}">首頁</a>　/　全部文章</div>
      <div class="cat-hero"><span class="role">ALL STORIES</span><h1>全部文章</h1><p>每一篇，都是一次小小的離題。</p></div>
      <div class="toolbar" style="margin-top:20px;">
        <div class="chips" role="group" aria-label="分類篩選">{chips}</div>
        <label class="searchbox"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8"/></svg>
          <input type="search" id="searchInput" placeholder="搜尋文章關鍵字" aria-label="搜尋文章" /></label>
      </div>
      <div class="grid" id="articleGrid">{"".join(card(r,a) for a in ARTS)}</div>
      <div class="empty-state" id="emptyState"><div class="big">這一題，還沒有人寫</div><p>換個關鍵字，或回到全部分類看看。也歡迎<a href="{r}submit/" style="color:var(--accent)">投稿你的內心戲</a>。</p></div>
      <div style="height:70px"></div>
    </main>''' + footer(r) + tail(r)
    write("articles/index.html", page)

def build_categories():
    r = "../../"
    for c in SITE["categories"]:
        items = [a for a in ARTS if a["cat"] == c["name"]]
        grid = "".join(card(r, a) for a in items) if items else \
            f'<div class="empty-state" style="display:block"><div class="big">這一題，還在醞釀</div><p>新文章很快就來。</p></div>'
        page = head(r, f'{c["name"]}｜{SITE["name"]}', c["desc"], f'{BASE}/columns/{c["slug"]}/') + masthead(r, True) + nav(r, c["name"]) + f'''
    <main class="wrap">
      <div class="crumb"><a href="{r}">首頁</a>　/　{c["name"]}</div>
      <div class="cat-hero">
        <div class="num">{c["num"]}　<span class="role">{c["en"]} · {c["role"]}</span></div>
        <h1>{c["name"]}</h1>
        <p>{c["desc"]}</p>
      </div>
      <div class="grid">{grid}</div>
      <div style="height:70px"></div>
    </main>''' + subscribe() + footer(r) + tail(r)
        write(f'columns/{c["slug"]}/index.html', page)

def build_article_pages():
    r = "../../"
    for a in ARTS:
        url = f'{BASE}/articles/{a["id"]}/'
        img = f'{BASE}/images/{a["img"]}.jpg' if a.get("img") else None
        if a.get("img"):
            cap = f'<figcaption>{e(a["caption"])}</figcaption>' if a.get("caption") else ""
            hero = f'<figure class="hero-img">{picture(r, a, lazy=False)}{cap}</figure>'
        else:
            hero = f'<div class="cover-typo hero-typo"><span class="small">{e(a.get("typoSmall",""))}</span><span class="big">{e(a.get("typo",""))}</span></div>'
        related = [x for x in ARTS if x["cat"] == a["cat"] and x is not a][:3]
        related += [x for x in ARTS if x is not a and x not in related][: 3 - len(related)]
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["excerpt"],
              "datePublished": a.get("date"), "inLanguage": "zh-Hant", "mainEntityOfPage": url,
              "publisher": {"@type": "Organization", "name": SITE["name"]}}
        if img: ld["image"] = img
        page = head(r, f'{a["title"]}｜{SITE["name"]}', a["excerpt"], url, img, "article") + masthead(r, True) + nav(r, a["cat"]) + f'''
    <main class="wrap">
      <div class="crumb"><a href="{r}">首頁</a>　/　<a href="{cat_url(r,a["cat"])}">{e(a["cat"])}</a></div>
      <article class="article">
        <a class="cat-label" href="{cat_url(r,a["cat"])}">{e(a["cat"])}</a>
        <h1>{e(a["title"])}</h1>
        <div class="hook">{e(a.get("hook",""))}</div>
        <div class="meta">{fmt_date(a["date"]) if a.get("date") else ""}</div>
        {hero}
        <div class="body">
          {body_html(a)}
        </div>
        <div id="articleEnd" data-slug="{a["id"]}"></div>
        {share_bar(a, url)}
      </article>
      <section class="related" aria-label="延伸閱讀">
        <div class="section-tag"><span class="tag-en">MORE</span><span class="tag-zh">再離題一下</span></div>
        <div class="grid">{"".join(card(r,x) for x in related)}</div>
      </section>
    </main>
    <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>''' + subscribe() + footer(r) + tail(r)
        write(f'articles/{a["id"]}/index.html', page)

def build_about():
    r = "../"
    m = SITE["email"]
    page = head(r, f'關於離題｜{SITE["name"]}', SITE["aboutWho"][:110], f"{BASE}/about/") + masthead(r, True) + nav(r, "關於離題") + f'''
    <main class="wrap">
      <div class="crumb"><a href="{r}">首頁</a>　/　關於離題</div>
      <div class="page-simple">
        <h1>關於離題</h1>
        <p>{SITE["aboutWho"]}</p>
        <h2 id="open-call">離題徵集 <span class="about-en">OPEN CALL</span></h2>
        <p>{SITE["openCall"]}</p>
        <p class="about-contact"><a href="{r}submit/">投稿「離友內心戲」</a>　或來信 <a href="mailto:{m}?subject=離題徵集">{m}</a></p>
        <h2 id="collab">合作邀約 <span class="about-en">COLLABORATION</span></h2>
        <p>{SITE["collab"]}</p>
        <p class="about-contact"><a href="mailto:{m}?subject=合作邀約">{m}</a></p>
      </div>
    </main>''' + subscribe() + footer(r) + tail(r)
    write("about/index.html", page)

def build_subscribed():
    r = "../"
    page = head(r, f'訂閱完成｜{SITE["name"]}', SITE["description"], f"{BASE}/subscribed/") + masthead(r, True) + nav(r) + f'''
    <main class="wrap"><div class="notfound">
      <div class="big">訂閱完成，歡迎一起離題</div>
      <p>下一封信會準時寄到你的信箱。在那之前，先挑一篇看看吧。</p>
      <div class="see-all"><a href="{r}articles/">看全部文章</a></div>
    </div></main>
    <script>try{{gtag("event","sign_up",{{method:"newsletter"}});}}catch(e){{}}</script>''' + footer(r) + tail(r)
    write("subscribed/index.html", page)

def build_submit():
    r = "../"
    m = SITE["email"]
    scenes = ["工作", "朋友", "家人", "感情", "一個人的時候", "其他"]
    opts = "".join(f'<label class="scene-opt"><input type="radio" name="scene" value="{x}"{" checked" if i==0 else ""} /> {x}</label>' for i, x in enumerate(scenes))
    page = head(r, f'離友內心戲｜{SITE["name"]}', "那些你在心裡演了一整齣、嘴上只說「沒事」的戲，寫給我們。匿名投稿，挑選改寫後刊在離題生活。", f"{BASE}/submit/") + masthead(r, True) + nav(r, "離友內心戲") + f'''
    <main class="wrap">
      <div class="crumb"><a href="{r}">首頁</a>　/　離友內心戲</div>
      <div class="page-simple submit-page">
        <span class="role" style="font-size:12px;letter-spacing:.34em;color:var(--accent);font-weight:700;">OPEN CALL</span>
        <h1>離友內心戲</h1>
        <p class="submit-lead">那些你在心裡演了一整齣、嘴上只說「沒事」的戲，寫給我們。</p>

        <h2>怎麼投稿</h2>
        <ol class="submit-steps">
          <li><strong>寫一段說不出口的內心戲</strong>：一個場景，加上一句你沒說出口的話就夠了，不用寫成文章。</li>
          <li><strong>我們挑選、改寫</strong>：加上一句吐槽，刊在網站或離題生活的社群上。</li>
          <li><strong>一律匿名</strong>：人名、公司、地點都會改掉，刊出時只用你留的暱稱，不留也可以。</li>
        </ol>

        <h2>不知道寫什麼？從這幾句開始</h2>
        <ul class="submit-prompts">
          <li>主管說「這個很簡單」的時候，我心裡想的是……</li>
          <li>朋友問我最近好嗎，我說還好，其實……</li>
          <li>家族群組又傳來長輩圖，我已讀不回，因為……</li>
          <li>我說「好啊，下次約」的時候，心裡在想……</li>
        </ul>

        <h2>寫給我們</h2>
        <form class="submit-form" id="submitForm" data-email="{m}" novalidate>
          <fieldset><legend>發生在哪裡</legend><div class="scene-opts">{opts}</div></fieldset>
          <label>那個場景<span class="hint">發生了什麼事？兩三句就好</span>
            <textarea name="story" rows="4" placeholder="例：週一開會，主管說這個案子很簡單，下週就要。"></textarea></label>
          <label>你嘴上說的<input type="text" name="said" placeholder="例：好，沒問題。" /></label>
          <label>你心裡演的<span class="hint">最想說、卻沒說出口的那句</span>
            <textarea name="thought" rows="3" placeholder="例：簡單的話，你怎麼不自己做？"></textarea></label>
          <label>刊出時的暱稱（可留空）<input type="text" name="nick" placeholder="例：會議室的盆栽" /></label>
          <label class="agree"><input type="checkbox" name="agree" /> 我同意離題生活改寫並匿名刊登這段內容</label>
          <button type="submit">寄出我的內心戲</button>
          <p class="submit-msg" id="submitMsg" role="status" aria-live="polite">按下寄出會打開你的電子郵件，內容已經幫你填好，寄到 {m}。</p>
        </form>
      </div>
    </main>''' + subscribe() + footer(r) + tail(r)
    write("submit/index.html", page)

def build_404():
    # GitHub Pages 的 404 可能出現在任何路徑，所以用絕對網址
    r = BASE + "/"
    page = head(r, f'找不到這一頁｜{SITE["name"]}', SITE["description"], f"{BASE}/404.html") + masthead(r, True) + nav(r) + f'''
    <main class="wrap"><div class="notfound"><div class="big">這一頁離題得太遠了</div><p>它可能搬家了，或從來沒存在過。</p>
      <div class="see-all"><a href="{r}">回到首頁</a></div></div></main>''' + footer(r) + tail(r)
    write("404.html", page)

def build_sitemap():
    urls = [f"{BASE}/", f"{BASE}/articles/", f"{BASE}/about/"] + \
           [f'{BASE}/columns/{c["slug"]}/' for c in SITE["categories"]] + [f"{BASE}/submit/"] + \
           [f'{BASE}/articles/{a["id"]}/' for a in ARTS]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
          "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    write("sitemap.xml", xml)
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

if __name__ == "__main__":
    build_home(); build_all_articles(); build_categories(); build_article_pages()
    build_about(); build_subscribed(); build_submit(); build_404(); build_sitemap()
    write(".nojekyll", "")
    print(f"完成：{len(ARTS)} 篇文章，{len(SITE['categories'])} 個分類")
