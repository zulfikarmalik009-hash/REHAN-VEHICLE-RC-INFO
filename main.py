# main.py
from flask import Flask, request, jsonify
import requests, re, time, logging
from bs4 import BeautifulSoup

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}

# ----------------------
# Helper utilities
# ----------------------
def safe_get(url, headers=None, timeout=10, tries=2, sleep=0.6):
    headers = headers or HEADERS
    last_err = None
    for i in range(tries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_err = e
            time.sleep(sleep)
    logging.warning("safe_get failed for %s : %s", url, last_err)
    return None

def clean(s):
    if not s: return None
    s = re.sub(r'\s+', ' ', s).strip()
    if s == "" or s.lower() in ("na","n/a","none","null"):
        return None
    return s

def find_by_label(soup, label_regex):
    """
    Generic helper: search for nodes that have the label text and try to find the value nearby.
    label_regex: compiled regex or string
    """
    try:
        if isinstance(label_regex, str):
            label_regex = re.compile(re.escape(label_regex), re.I)
        # try <span>text</span> patterns
        span = soup.find(lambda tag: tag.name in ("span","label","b","strong") and tag.string and label_regex.search(tag.string))
        if span:
            # siblings, parent paragraph, next <p>, next sibling text, table row next td
            parent = span.parent
            # check immediate next elements
            nxt = span.find_next_sibling()
            if nxt and nxt.get_text(strip=True):
                return clean(nxt.get_text(" ", strip=True))
            # look for parent <div> or <li> then find <p> or text
            if parent:
                p = parent.find("p")
                if p and p.get_text(strip=True):
                    return clean(p.get_text(" ", strip=True))
                # table cell patterns
                td = parent.find_next("td")
                if td and td.get_text(strip=True):
                    return clean(td.get_text(" ", strip=True))
        # try dt/dd patterns
        dts = soup.find_all("dt")
        for dt in dts:
            if label_regex.search(dt.get_text(" ", strip=True)):
                dd = dt.find_next_sibling("dd")
                if dd:
                    return clean(dd.get_text(" ", strip=True))
        # try table rows where first cell contains label
        rows = soup.find_all("tr")
        for tr in rows:
            tds = tr.find_all(["th","td"])
            if len(tds) >= 2:
                left = tds[0].get_text(" ", strip=True)
                if label_regex.search(left):
                    return clean(tds[1].get_text(" ", strip=True))
        # fallback: search for "Label: Value" in whole text
        txt = soup.get_text(" ", strip=True)
        m = re.search(rf"{label_regex.pattern}\\s*[:\-]{{0,2}}\\s*([A-Za-z0-9\-\./ ,#]+)", txt, re.I)
        if m:
            return clean(m.group(1))
    except Exception as e:
        logging.debug("find_by_label error: %s", e)
    return None

def extract_key_values(soup):
    """
    Generic scan across common patterns to extract many possible label:value pairs.
    Returns dict of found fields.
    """
    out = {}
    # Common labels to try (Hindi/English small set)
    labels = [
        "Owner Name","Owner","Name","Owner's Name",
        "Father's Name","Father Name","Father",
        "Registration No","Registration Number","Registration",
        "Model Name","Model","Vehicle Model","Maker Model","Make",
        "Vehicle Class","Fuel Type","Fuel","Registration Date","Registered On",
        "Insurance Company","Insurance No","Insurance Expiry","Insurance Upto",
        "Fitness Upto","Tax Upto","PUC No","PUC Upto",
        "Registered RTO","RTO","Address","City","Phone","Mobile",
        "Engine No","Engine Number","Chassis No","Chassis Number"
    ]
    for lab in labels:
        try:
            val = find_by_label(soup, lab)
            if val:
                out[lab] = val
        except:
            pass

    # Additionally try to read any two-column tables as generic pairs
    try:
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for tr in rows:
                cols = [td.get_text(" ",strip=True) for td in tr.find_all(["td","th"])]
                if len(cols) >= 2:
                    k = clean(cols[0])
                    v = clean(cols[1])
                    if k and v and len(k) < 50:
                        out[k] = v
    except:
        pass

    return out

# -----------------------
# Primary free source: improved vahanx scraper
# -----------------------
def fetch_from_vahanx(rc):
    url = f"https://vahanx.in/rc-search/{rc}"
    html = safe_get(url)
    if not html:
        return {}, {"source":"vahanx","error":"no-response"}
    soup = BeautifulSoup(html, "html.parser")

    data = extract_key_values(soup)

    # also try meta / JSON-LD inside scripts
    try:
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json
                jd = json.loads(script.string)
                # if jd is dict, try to map some keys
                if isinstance(jd, dict):
                    for k in ("name","address","telephone"):
                        if jd.get(k):
                            data[k] = jd.get(k)
            except:
                pass
    except:
        pass

    return data, {"source":"vahanx","html_snippet": html[:2000]}

# -----------------------
# Secondary free attempt: search-based fallback (public aggregator)
# We'll attempt another public aggregator that exposes RC lookup without auth.
# For free/public endpoints that are purely HTML, we'll try same parsing approach.
# NOTE: If a site is heavily rate-limited or blocks scraping, this may return nothing.
# -----------------------
def fetch_from_public_aggregator(rc):
    # Example aggregator 1 (best-effort). Using generic search-like endpoints is fragile.
    # We'll attempt a small set of known aggregator patterns if reachable.
    tried = []
    results = {}
    # aggregator candidate 1: vahanx already tried
    # aggregator candidate 2: (example) "https://www.vechileinfo.example/rc/<rc>" -- placeholder not used
    # We keep this function pluggable for future aggregator URLs.
    return results, {"source":"aggregator","tried":tried}

# -----------------------
# Merge helper
# -----------------------
def merge_dicts(*dicts):
    res = {}
    for d in dicts:
        if not isinstance(d, dict):
            continue
        for k,v in d.items():
            if v and (k not in res or not res[k]):
                res[k] = v
    return res

# -----------------------
# API endpoint
# -----------------------
@app.route("/", methods=["GET"])
def api_root():
    rc = request.args.get("rc_number")
    debug = request.args.get("debug", "").lower() in ("1","true","yes")
    if not rc:
        return jsonify({"status":"error","message":"Missing rc_number"}), 400

    rc = rc.replace(" ", "").upper()

    # 1) vahanx
    vahan_data, vahan_meta = fetch_from_vahanx(rc)

    # 2) aggregator fallback (placeholder for future aggregator sites)
    agg_data, agg_meta = fetch_from_public_aggregator(rc)

    merged = merge_dicts(vahan_data, agg_data)

    # If merged empty, respond not_found; include raw when debug
    if not merged:
        payload = {"status":"not_found","rc_number":rc,"message":"No details found from free sources"}
        if debug:
            payload["raw_sources"] = {"vahanx": vahan_meta, "aggregator": agg_meta}
        return jsonify(payload), 404

    resp = {
        "status":"success",
        "rc_number": rc,
        "details": merged
    }
    if debug:
        resp["raw_sources"] = {"vahanx": vahan_meta, "aggregator": agg_meta}
    return jsonify(resp), 200

# health
@app.route("/_health")
def health():
    return jsonify({"status":"ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
