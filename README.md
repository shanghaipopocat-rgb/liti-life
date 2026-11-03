# 離題生活 網站

網址：https://shanghaipopocat-rgb.github.io/liti-life/

## 網站結構

| 頁面 | 位置 |
|---|---|
| 首頁 | `index.html` |
| 全部文章（可篩選、搜尋） | `articles/` |
| 每篇文章 | `articles/<文章代號>/` |
| 分類：生活異思／荒謬觀察／人生練習 | `columns/rethink/`、`columns/absurd/`、`columns/practice/` |
| 關於離題（含徵稿、合作） | `about/` |

所有頁面都已裝上 Google Analytics（G-B2XKTVK0JB）。

## 平常怎麼改內容

網頁是程式產生的，**不要直接改 html 檔**，改下面三個檔案就好：

- `content/site.json`：標語、首頁文案、分類說明、關於頁、社群連結
- `content/articles.json`：所有文章
- `content/today.json`：「今天聊什麼」的題目

改完後執行：

```
python3 scripts/build.py
```

## 新增一篇文章

1. 圖片存成兩個檔：`images/<代號>.webp` 和 `images/<代號>.jpg`（寬 1600px 左右即可）。
2. 在 `content/articles.json` 加一筆：

```json
{
  "id": "group-ok",
  "cat": "荒謬觀察",
  "title": "群組裡的「收到」，有幾個是真的收到",
  "excerpt": "列表上顯示的摘要",
  "hook": "一句紅字鉤子",
  "img": "group-ok",
  "imgAlt": "圖片描述",
  "kind": "插畫",
  "date": "2026-11-04",
  "body": ["第一段", {"heading": "小標"}, "第二段"]
}
```

沒有圖片時，改用 `"typo": "大字"`、`"typoSmall": "英文小字"`。
想放首頁大圖精選，加 `"featured": true`；想放首頁橫幅，加 `"wide": true`。

## 追蹤

- GA 會自動記錄每篇文章的瀏覽量和來源（Facebook、IG、LINE、Google 等）。
- 文章分享按鈕會自動加上 `utm_source`，在 GA「流量開發」報表裡可以看到是從哪個平台分享進來的。
- 另外記錄的事件：`share`（分享按鈕）、`article_read_complete`（讀到文末）、`outbound_click`（點社群連結）、`search`、`today_scene`。
