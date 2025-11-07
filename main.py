# main.py
from flask import Flask, request, jsonify
import requests, re, time, logging
from bs4 import BeautifulSoup

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>वाहन जानकारी - Rehan Z4X</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">

<style>
:root{
  --bg:#000;
  --accent:#00ff9f;
  --text-color:#00ff9f;
  --label-color:#00ffaa;
  --glass: rgba(0,0,0,0.35);
  --font-main:'Poppins', monospace;
}

body{
  margin:0;
  padding:0;
  font-family:var(--font-main);
  background:var(--bg);
  color:var(--text-color);
  overflow-x:hidden;
  position:relative;
}

/* BACKGROUND LAYERS */
#matrix, #glitchNoise, #scanlines, #hexGrid{
  position:fixed;
  inset:0;
  width:100%;
  height:100%;
  pointer-events:none;
  z-index:0;
}

#glitchNoise{ opacity:0.17; }
#scanlines{ opacity:0.12; }
#hexGrid{ opacity:0.25; }

/* HEADER */
header{
  padding:50px 20px 70px 20px;
  display:flex;
  flex-direction:column;
  align-items:center;
  position:relative;
  z-index:2;
  text-align:center;
}

header img{
  width:180px;
  height:180px;
  border-radius:50%;
  border:4px solid var(--accent);
}

/* Inputs */
input{
  padding:12px 15px;
  width:280px;
  border:2px solid var(--accent);
  border-radius:15px;
  font-size:16px;
  background:var(--glass);
  color:var(--text-color);
  outline:none;
}

/* Buttons */
button{
  padding:12px 18px;
  background:var(--accent);
  color:#000;
  border:none;
  border-radius:12px;
  cursor:pointer;
  font-size:16px;
  font-weight:bold;
}

/* Result */
.result{
  background:var(--glass);
  margin-top:30px;
  padding:25px;
  border-radius:20px;
  width:100%;
  max-width:700px;
  font-size:16px;
  line-height:1.8;
  color:var(--text-color);
  position:relative;
  z-index:2;
  white-space:pre-wrap;
}

.result b{
  color:var(--label-color);
}

.credit{
  text-align:center;
  font-size:14px;
  margin-top:30px;
  opacity:0.7;
  z-index:2;
}
</style>
</head>

<body>

<!-- ✅ ALL HACKER BACKGROUND LAYERS -->
<canvas id="matrix"></canvas>
<canvas id="glitchNoise"></canvas>
<canvas id="scanlines"></canvas>
<canvas id="hexGrid"></canvas>

<header>
  <img src="https://i.ibb.co/FbpgNfbZ/Screenshot-20250923-145058-edit-226003820134146.jpg">
  <a href="https://instagram.com/rehan_z4x" target="_blank" 
     style="color:var(--text-color);margin-top:15px;font-size:20px;font-weight:600;">
     Instagram: @rehan_z4x
  </a>
</header>

<main style="position:relative;z-index:2;text-align:center;">
  <h2 style="color:var(--accent); margin-bottom:20px;">🚗 वाहन जानकारी देखें</h2>

  <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:10px;">
    <input type="text" id="rcInput" placeholder="वाहन नंबर डालें..." />
    <button onclick="fetchVehicle()">🔍 खोजें</button>
  </div>

  <div id="result" class="result" style="display:none;"></div>
</main>

<div class="credit">© 2025 Rehan Z4X</div>

<script>
/* ✅ VEHICLE API SYSTEM */
const API_URL="https://rehan-vehicle-rc-info.vercel.app/";

async function fetchVehicle(){
  const rc=document.getElementById("rcInput").value.trim();
  const resultDiv=document.getElementById("result");
  if(!rc){alert("कृपया वाहन नंबर डालें!");return;}

  resultDiv.style.display="block";
  resultDiv.innerHTML="⏳ जानकारी लायी जा रही है...";

  try{
    const res=await fetch(`${API_URL}?rc_number=${rc}`);
    const data=await res.json();

    if(data.status!=="success"){
      resultDiv.innerHTML=`❌ ${data.message}`;
      return;
    }

    let fullText=`🔹 Developer: rehan_z4x 🔹\n\n`;

    for(const [key,value] of Object.entries(data.details)){
      if(value) fullText+=`<b>${key}</b>: ${value}\n`;
    }

    resultDiv.innerHTML =
      fullText +
      '<button onclick="copyInfo()" style="margin-top:20px;padding:10px 20px;background:#00ff9f;border:none;border-radius:10px;font-weight:bold;">📋 कॉपी करें</button>';

  }catch(e){
    resultDiv.innerHTML=`⚠️ जानकारी लाने में त्रुटि।`;
  }
}

function copyInfo(){
  navigator.clipboard.writeText(document.getElementById("result").innerText);
  alert("✅ कॉपी हो गया!");
}

/* ✅ MATRIX RAIN */
(function(){
  const canvas=document.getElementById('matrix');
  const ctx=canvas.getContext('2d');

  let W=innerWidth, H=innerHeight;
  const fontSize=18;
  const columns=Math.floor(W/fontSize);
  let drops=[];

  canvas.width=W; canvas.height=H;

  for(let x=0;x<columns;x++){ drops[x]=Math.random()*H; }

  function draw(){
    ctx.fillStyle='rgba(0,0,0,0.05)';
    ctx.fillRect(0,0,W,H);

    ctx.fillStyle='#00ff9f';
    ctx.font=fontSize+'px monospace';

    for(let i=0;i<drops.length;i++){
      const text=String.fromCharCode(0x30A0 + Math.random()*96);
      ctx.fillText(text, i*fontSize, drops[i]*fontSize);

      if(drops[i]*fontSize > H && Math.random()>0.975){
        drops[i]=0;
      }
      drops[i]++;
    }
  }

  setInterval(draw, 40);
})();

/* ✅ GLITCH NOISE */
(function(){
  const canvas=document.getElementById("glitchNoise");
  const ctx=canvas.getContext("2d");

  function resize(){
    canvas.width=innerWidth;
    canvas.height=innerHeight;
  }

  resize();

  function generateNoise(){
    const W=canvas.width, H=canvas.height;
    const imageData=ctx.createImageData(W,H);
    const buffer=new Uint32Array(imageData.data.buffer);

    for(let i=0;i<buffer.length;i++){
      buffer[i]=(255<<24) | ((Math.random()*50)<<16) | ((Math.random()*255)<<8) | (Math.random()*50);
    }

    ctx.putImageData(imageData,0,0);
  }

  function animate(){
    generateNoise();
    requestAnimationFrame(animate);
  }

  animate();
  addEventListener("resize", resize);
})();

/* ✅ CRT SCANLINES */
(function(){
  const canvas=document.getElementById("scanlines");
  const ctx=canvas.getContext("2d");

  function resize(){
    canvas.width=innerWidth;
    canvas.height=innerHeight;
  }

  resize();

  function draw(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle="rgba(0,255,100,0.04)";

    for(let y=0;y<canvas.height;y+=3){
      ctx.fillRect(0,y,canvas.width,1);
    }
    requestAnimationFrame(draw);
  }

  draw();
  addEventListener("resize", resize);
})();

/* ✅ HEXAGONAL HACKER GRID */
(function(){
  const canvas=document.getElementById("hexGrid");
  const ctx=canvas.getContext("2d");

  function resize(){
    canvas.width=innerWidth;
    canvas.height=innerHeight;
  }

  resize();

  const size=30;
  const h=size*Math.sqrt(3)/2;

  let tick=0;

  function draw(){
    ctx.clearRect(0,0,canvas.width,canvas.height);

    for(let y=0; y<canvas.height+size; y+=h){
      for(let x=0; x<canvas.width+size; x+=size*1.5){

        const offset = (Math.floor(y/h) % 2) * (size*0.75);

        let glow = Math.sin((x+y+tick)/40)*20 + 40;

        ctx.strokeStyle = `rgba(0,255,120,${glow/150})`;
        ctx.lineWidth = 1;

        drawHex(x+offset, y);
      }
    }

    tick++;
    requestAnimationFrame(draw);
  }

  function drawHex(x,y){
    const r=size/2;
    ctx.beginPath();
    for(let i=0;i<6;i++){
      const angle=Math.PI/3*i;
      ctx.lineTo(x + r*Math.cos(angle), y + r*Math.sin(angle));
    }
    ctx.closePath();
    ctx.stroke();
  }

  draw();
  addEventListener("resize", resize);
})();
</script>

</body>
</html> Chrome/115.0 Safari/537.36"
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
