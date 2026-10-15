"""Refresh data/scholar.json from the public Google Scholar profile.

Run weekly by .github/workflows/scholar.yml (Scholar often blocks GitHub runners), or locally:

    python3 scripts/update_scholar.py && git commit -am "Refresh Google Scholar data" && git push

If Scholar refuses the request or the page layout changes, the script exits without
touching the existing file, so the site keeps showing the last good numbers.
"""
import html, json, re, sys, urllib.request
from datetime import date

USER = "cL60wssAAAAJ"
URL = f"https://scholar.google.com/citations?user={USER}&hl=en&pagesize=100&sortby=pubdate"
OUT = "data/scholar.json"

def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept-Language": "en"})
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    stats = [text(x) for x in re.findall(r'<td class="gsc_rsb_std">(.*?)</td>', page)]
    rows = re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', page, re.S)
    if len(stats) < 6 or not rows:
        sys.exit("Scholar page not recognised; keeping the existing data")
    papers = {}
    for r in rows:
        m = re.search(r'citation_for_view=([^"&]+)"[^>]*class="gsc_a_at">(.*?)</a>', r)
        if not m:
            continue
        c = re.search(r'class="gsc_a_ac[^"]*"[^>]*>(\d*)</a>', r)
        y = re.search(r'class="gsc_a_h gsc_a_hc gs_ibl">(\d*)</span>', r)
        papers[html.unescape(m.group(1))] = {"title": text(m.group(2)), "cites": int(c.group(1)) if c and c.group(1) else 0, "year": int(y.group(1)) if y and y.group(1) else None}
    data = {"updated": date.today().isoformat(), "profile": f"https://scholar.google.com/citations?user={USER}",
            "citations": int(stats[0]), "h_index": int(stats[2]), "i10_index": int(stats[4]), "papers": papers}
    json.dump(data, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(f"{len(papers)} papers, {data['citations']} citations, h-index {data['h_index']}")

if __name__ == "__main__":
    main()
