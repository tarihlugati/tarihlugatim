import requests, feedparser, html, datetime, pathlib

screen_name = "tarihlugati"   # hesabın
NITTER_HOSTS = [
    "https://nitter.net",
    "https://nitter.cz",
    "https://nitter.it",
    "https://nitter.tiekoetter.com",
]
MAX_ITEMS = 10
TIMEOUT = 10

def fetch_rss():
    for host in NITTER_HOSTS:
        url = f"{host}/{screen_name}/rss"
        try:
            r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
            if r.ok and r.text.strip().startswith("<?xml"):
                return r.text, url
        except Exception:
            pass
    return None, None

def item_html(entry):
    title = html.escape(getattr(entry, "title", "").strip())
    link  = getattr(entry, "link", "").strip()
    date  = getattr(entry, "published", "") or getattr(entry, "updated", "")
    date  = html.escape(date)
    return f"""
    <article class="tw">
      <p class="t">{title}</p>
      <a class="lnk" href="{link}" target="_blank" rel="noopener">Gönderiyi aç</a>
      <span class="dt">{date}</span>
    </article>"""

def build_page(entries, source_url, err=None):
    updated = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    body = "\n".join(item_html(e) for e in entries) if entries else f"""
      <div class="empty">
        Şu anda içerik çekilemedi{": " + html.escape(err) if err else ""}. 
        Lütfen daha sonra tekrar deneyin.
      </div>"""
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Tarih Lügati – Son Paylaşımlar</title>
  <style>
    body{{margin:0;background:#fff;font:16px/1.55 system-ui,Arial}}
    .wrap{{max-width:920px;margin:0 auto;padding:16px}}
    h2{{margin:4px 0 12px}}
    .src{{font-size:12px;color:#666;margin-bottom:10px}}
    .tw{{border-bottom:1px solid #eee;padding:10px 0}}
    .t{{margin:0 0 6px;white-space:pre-wrap}}
    .lnk{{color:#1da1f2;text-decoration:none}}
    .lnk:hover{{text-decoration:underline}}
    .dt{{display:block;color:#888;font-size:12px;margin-top:4px}}
    .foot{{color:#777;font-size:12px;margin-top:10px}}
    .empty{{color:#777;padding:14px 0}}
  </style>
</head>
<body>
  <div class="wrap">
    <h2>@{screen_name} – Son Paylaşımlar</h2>
    <div class="src">Kaynak: {html.escape(source_url) if source_url else "RSS erişilemedi"}</div>
    {body}
    <div class="foot">Güncellendi: {updated}</div>
  </div>
</body>
</html>"""

def main():
    xml, used = fetch_rss()
    err = None
    entries = []
    if xml:
        try:
            d = feedparser.parse(xml)
            entries = d.entries[:MAX_ITEMS]
        except Exception as e:
            err = str(e)
    else:
        err = "RSS kaynaklarına ulaşılamadı"
    page = build_page(entries, used, err)
    pathlib.Path("embed.html").write_text(page, encoding="utf-8")
    print("embed.html üretildi", f"(kaynak: {used})")

if __name__ == "__main__":
    main()
