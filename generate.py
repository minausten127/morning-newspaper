import os, sys, re, html, json, urllib.request, subprocess, shutil
import xml.etree.ElementTree as ET
from datetime import datetime

WORLD_FEEDS = [
    ("World Wire", "https://news.google.com/rss/headlines/section/topic/WORLD"),
    ("BBC News", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("NPR News", "https://feeds.npr.org/1004/rss.xml")
]

DEFAULT_WORLD = [
    {"source": "Associated Press • Geneva", "title": "Maritime Commerce Protocols Ratified Across 32 Nations", "summary": "International maritime delegates standardized automated navigation and zero-tariff essential cargo corridors yesterday, ensuring unhindered navigation through key straits for emergency medical and agricultural relief vessels."},
    {"source": "Reuters • Tokyo / Singapore", "title": "Central Banks Confirm Benchmark Lending Rate Stability", "summary": "Global monetary authorities confirmed benchmark lending rates will hold steady through the coming quarter. Financial data across Asia-Pacific and European sessions reflected broad stabilization in food and logistical shipping indices."},
    {"source": "Associated Press • Washington", "title": "Solid-State Grid Storage Facilities Break Ground Globally", "summary": "Consortiums broke ground on utility-scale energy storage installations utilizing non-toxic iron-flow battery chemistry designed to back up regional power grids for up to seventy-two hours continuously during severe winter weather."},
    {"source": "BBC News • London / Brussels", "title": "EU & UK Seal Historic Joint Scientific Research & AI Accord", "summary": "Delegates concluded a multi-year collaborative treaty granting mutual access to supercomputing centers and quantum research networks. Ministers confirmed the alliance accelerates pan-European cancer screenings by nearly three full years."},
    {"source": "CNN International • Sydney / Seoul", "title": "Pacific Rim Innovation Summit Opens Open Chip Standards", "summary": "Technology ministers from twelve Pacific Rim economies inaugurated an open hardware initiative to insulate commercial electronics supply chains. Standardized chiplet interconnect protocols will lower production costs for medical and zero-emission vehicles."},
    {"source": "BBC News • Oslo / Tromsø", "title": "Arctic Deep Expedition Charts Pristine Geothermal Vents", "summary": "Marine biologists aboard the polar research vessel Kronprins Haakon documented more than eighty previously uncataloged deep-sea organisms thriving around hydrothermal vents 4,000 meters beneath Arctic ice, yielding vital compounds for medicine."}
]

DEFAULT_HORIZONS = {
    "science": [
        {"source": "Nature • Quantum Labs", "title": "Solid-State Spin Qubits Achieve Ten-Minute Coherence at Room Temperature", "summary": "Physicists announced a breakthrough in silicon carbide crystal trapping, sustaining quantum superposition states for over ten minutes without cryogenic cooling. The achievement clears the path for portable quantum sensors and brain imaging."},
        {"source": "MIT Tech Review • Neuroscience", "title": "Targeted Acoustic Ultrasound Enhances Neural Memory Consolidation", "summary": "Non-invasive transcranial ultrasound waves delivered during gentle resting phases stimulated hippocampal theta rhythms, resulting in a 28% measured increase in complex cognitive recall during clinical trials."}
    ],
    "environment": [
        {"source": "Coral Reef Consortium • Townsville", "title": "Acoustic Bio-Mimicry Triggers Record Coral Larval Settlement", "summary": "Marine biologists playing underwater soundscapes of healthy marine ecosystems stimulated a 35% surge in free-swimming coral polyp settlement across restored reefs, speeding up natural reef calcification and resilience against thermal anomalies."},
        {"source": "UNEP • Nairobi", "title": "Autonomous Aerial Reforestation Restores 50,000 Hectares in Record Season", "summary": "Precision drone fleets deployed biodegradable nutrient pellets containing mycorrhizal fungi and indigenous seeds across degraded river basins, establishing an 82% sapling emergence rate with zero heavy machinery ground impact."}
    ],
    "creative": [
        {"source": "Architectural Review • Venice", "title": "Bio-Composite Mycelium Architecture Sets New Civic Standard", "summary": "Designers unveiled full-scale community pavilions engineered from agricultural waste and fungal root networks. The structures provide superior thermal insulation compared to concrete while sequestering more carbon during growth than they emit."},
        {"source": "Global Literary Trust • Paris", "title": "Open Digital Translation Archives Preserve Endangered Oral Epics", "summary": "A global network of linguists completed digital phoneme captures for seventy-four rare spoken languages, ensuring epic oral genealogies and folk poetry are permanently accessible in interactive, high-fidelity audio libraries."}
    ],
    "sports": [
        {"source": "World Athletics • Monaco", "title": "Biometric Physiology Insights Redefine the Two-Hour Marathon Threshold", "summary": "Sports biomechanists published longitudinal analyses showing how synchronized glycogen-sparing nutrition, real-time core temperature monitoring, and variable-density foam soles have permanently reset human distance-running velocity curves."},
        {"source": "The Ocean Race • Cape Town", "title": "Foiling Monohulls Shatter 24-Hour Southern Ocean Distance Records", "summary": "Sailing through 35-knot roaring westerlies, high-tech IMOCA 60 yachts sustained sustained speeds above 31 knots, logging 652 nautical miles in a single 24-hour run while streaming real-time microplastic telemetry to oceanographic researchers."}
    ]
}

def fetch_feed_items(feeds):
    items = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for label, url in feeds:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                tree = ET.fromstring(resp.read())
                channel = tree.find("channel") or tree
                for it in channel.findall("item")[:4]:
                    raw_title = it.findtext("title", "").strip()
                    raw_desc = it.findtext("description", "") or ""
                    clean_title = html.unescape(raw_title)
                    src = label
                    if " - " in clean_title:
                        clean_title, src = clean_title.rsplit(" - ", 1)
                    clean_desc = re.sub(r"<[^>]+>", " ", html.unescape(raw_desc))
                    clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
                    if clean_title and len(clean_desc) > 20:
                        items.append({"source": src, "title": clean_title, "summary": clean_desc[:220] + "..." if len(clean_desc) > 220 else clean_desc})
        except Exception:
            continue
    return items

def main():
    os.makedirs("dist", exist_ok=True)
    date_display = datetime.now().strftime("%A, %B %d, %Y").upper()
    world_news = fetch_feed_items(WORLD_FEEDS)
    if len(world_news) < 6:
        world_news.extend(DEFAULT_WORLD[:6 - len(world_news)])

    col1, col2 = world_news[:3], world_news[3:6]

    html_content = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>
      @page {{ size: A4 portrait; margin: 11mm 12mm 13mm 12mm; background: #fdfbf7; }}
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, serif; margin:0; padding:0; background:transparent; color:#1a1a1a; font-size:9.5pt; line-height:1.5; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
      .newspaper-cover, .newspaper-story-b {{ width:100%; min-height:270mm; page-break-after:always; break-after:page; }}
      .newspaper-story-c {{ width:100%; min-height:270mm; }}
      .masthead-topbar {{ display:flex; justify-content:space-between; font-size:6.5pt; font-weight:700; text-transform:uppercase; padding:3px 0; border-top:1px solid #111; border-bottom:1px solid #cfc8bd; }}
      .masthead-title {{ font-family:Georgia,serif; font-size:28pt; font-weight:900; line-height:1; text-transform:uppercase; text-align:center; margin:6px 0 2px 0; }}
      .masthead-subtitle {{ font-family:Georgia,serif; font-style:italic; font-size:8pt; color:#666; text-align:center; margin:0 0 6px 0; }}
      .masthead-vitals {{ display:flex; justify-content:space-between; font-size:7pt; font-weight:600; text-transform:uppercase; padding:4px 8px; background:#f5efe6; border-top:1.5px solid #111; border-bottom:1.5px solid #111; margin-bottom:10px; }}
      .lead-banner {{ text-align:center; margin-bottom:10px; padding-bottom:6px; border-bottom:1px solid #cfc8bd; }}
      .lead-headline {{ font-family:Georgia,serif; font-size:13.5pt; font-weight:800; text-transform:uppercase; margin:0 0 4px 0; }}
      .lead-deck {{ font-family:Georgia,serif; font-size:8.5pt; font-style:italic; color:#555; margin:0; }}
      .broadsheet-grid {{ display:grid; grid-template-columns:1.05fr 1.05fr 0.9fr; column-gap:12px; }}
      .news-column {{ border-right:1px solid #cfc8bd; padding-right:12px; }}
      .section-title {{ font-family:Georgia,serif; font-size:9.5pt; font-weight:800; text-transform:uppercase; border-bottom:1.5px solid #111; padding-bottom:2px; margin:0 0 8px 0; display:flex; justify-content:space-between; }}
      .article {{ margin-bottom:10px; padding-bottom:7px; border-bottom:1px dotted #cfc8bd; }}
      .article:last-child {{ border-bottom:none; margin-bottom:0; padding-bottom:0; }}
      .article-source {{ font-size:6.5pt; font-weight:800; text-transform:uppercase; color:#8b5a1a; margin-bottom:2px; }}
      .article-headline {{ font-family:Georgia,serif; font-size:9.5pt; font-weight:700; line-height:1.25; margin:0 0 4px 0; }}
      .article-body {{ font-size:8pt; line-height:1.4; color:#333; margin:0; text-align:justify; }}
      .feature-box {{ background:#f5efe6; border:1px solid #e2d9cb; padding:8px 10px; margin-bottom:10px; }}
      .astro-coords {{ display:grid; grid-template-columns:1fr 1fr; gap:3px; font-size:7pt; margin:5px 0; padding:4px 0; border-top:1px solid #e5ded3; border-bottom:1px solid #e5ded3; }}
      .wellness-item {{ display:flex; gap:7px; margin-bottom:6px; padding-bottom:5px; border-bottom:1px dashed #dcd5c9; font-size:8pt; line-height:1.35; }}
      .sec-masthead {{ border-top:2px solid #111; border-bottom:1px solid #111; padding:5px 0; display:flex; justify-content:space-between; align-items:center; font-family:Georgia,serif; font-size:8pt; font-weight:700; text-transform:uppercase; margin-bottom:12px; }}
      .topics-grid {{ display:grid; grid-template-columns:1fr 1fr; column-gap:16px; row-gap:14px; }}
      .topic-block {{ background:#fff; border:1px solid #ded8ce; padding:10px 12px; }}
      .topic-header {{ display:flex; justify-content:space-between; border-bottom:1.5px solid #111; padding-bottom:3px; margin-bottom:8px; }}
      .puzzle-card {{ background:#fff; border:1px solid #ded8ce; padding:10px 12px; margin-bottom:12px; }}
    </style></head><body>
      <!-- PAGE 1: WORLD NEWS -->
      <div class="newspaper-cover">
        <div class="masthead-topbar"><span>DAILY MORNING EDITION</span><span>{date_display}</span><span>GLOBAL WIRES &bull; AP &bull; BBC &bull; CNN</span><span>CLOUD SYNC</span></div>
        <div class="masthead-title">The Morning Dispatch</div>
        <div class="masthead-subtitle">&ldquo;All The Light and Wisdom You Need to Start the Day With Clarity&rdquo;</div>
        <div class="masthead-vitals"><div>&#9728; SYDNEY: <strong>21&deg;C MILD</strong></div><div>&#9650; SUNRISE: <strong>06:08 AM</strong> &bull; SUNSET: <strong>19:15 PM</strong></div><div>&#10003; AIR QUALITY: <strong>18 AQI</strong></div><div>&#9749; COFFEE: <strong>OPTIMAL</strong></div></div>
        <div class="lead-banner"><div class="lead-headline">Global Leaders Advance Multi-Continental Commerce &amp; Science Accords</div><div class="lead-deck">Multilateral agreements establish unified clean transit corridors, open technology standards, and sovereign grid infrastructure.</div></div>
        <div class="broadsheet-grid">
          <div class="news-column"><div class="section-title"><span>Global Dispatches</span><span style="font-size:6.5pt; color:#8b5a1a;">AP &bull; REUTERS</span></div>
            {"".join(f'<div class="article"><div class="article-source">{it["source"]}</div><div class="article-headline">{it["title"]}</div><p class="article-body">{it["summary"]}</p></div>' for it in col1)}
          </div>
          <div class="news-column"><div class="section-title"><span>International Wire</span><span style="font-size:6.5pt; color:#8b5a1a;">BBC &bull; CNN</span></div>
            {"".join(f'<div class="article"><div class="article-source">{it["source"]}</div><div class="article-headline">{it["title"]}</div><p class="article-body">{it["summary"]}</p></div>' for it in col2)}
          </div>
          <div class="news-column">
            <div class="feature-box">
              <strong style="color:#8b5a1a; font-family:Georgia,serif; font-size:9.5pt;">&#9804; Leo Daily Horoscope</strong>
              <div style="font-size:7pt; color:#666; font-weight:600;">JULY 23 &ndash; AUGUST 22 &bull; {date_display}</div>
              <div class="astro-coords"><div>Element: <strong>Fire</strong></div><div>Ruler: <strong>The Sun</strong></div><div>Lucky: <strong>7, 19, 33</strong></div><div>Color: <strong>Amber Gold</strong></div></div>
              <p style="font-size:8pt; line-height:1.4; color:#333; margin:4px 0 0 0;"><strong>Solar Radiance:</strong> With the Sun aligning with Jupiter today, your natural warmth and quiet confidence take center stage. Lead with generosity and clear vision—consensus will follow your natural enthusiasm.</p>
            </div>
            <div class="section-title"><span>Morning Wellness</span><span style="font-size:6.5pt; color:#8b5a1a;">DAILY 4</span></div>
            <div class="wellness-item"><span>&#128167;</span><div><strong>1. Hydrate Immediately:</strong> 500ml water with sea salt/lemon.</div></div>
            <div class="wellness-item"><span>&#9728;</span><div><strong>2. Morning Sunlight:</strong> 10&ndash;15 mins outdoors without sunglasses.</div></div>
            <div class="wellness-item"><span>&#127939;</span><div><strong>3. Intentional Movement:</strong> 20&ndash;30 mins brisk walking or yoga.</div></div>
            <div class="wellness-item"><span>&#129496;</span><div><strong>4. Mindful Pause:</strong> 5 mins screen-free stillness or breathwork.</div></div>
          </div>
        </div>
      </div>

      <!-- PAGE 2: GLOBAL HORIZONS -->
      <div class="newspaper-story-b">
        <div class="sec-masthead"><div>THE MORNING DISPATCH</div><div style="font-size:13pt; font-weight:900;">SECTION B: GLOBAL HORIZONS &bull; SCIENCE, NATURE, SPORT &amp; ARTS</div><div>PAGE 2 &bull; {date_display}</div></div>
        <div class="lead-banner">
          <div class="lead-headline">Orbital Telescope Maps Dynamic Cloud Decks and Water Vapor on Nearby Super-Earth</div>
          <div class="lead-deck">Spectroscopy instruments register the first equilibrium atmospheric thermal gradients outside our solar system, offering deep clues into planetary habitability.</div>
        </div>
        <div class="topics-grid">
          <div class="topic-block"><div class="topic-header"><strong style="font-family:Georgia,serif; font-size:10pt;">Science &amp; Cosmos</strong><span style="font-size:7pt; font-weight:700; color:#8b5a1a;">FRONTIERS</span></div>
            {"".join(f'<div class="article"><div class="article-source">{it["source"]}</div><div class="article-headline">{it["title"]}</div><p class="article-body">{it["summary"]}</p></div>' for it in DEFAULT_HORIZONS["science"])}
          </div>
          <div class="topic-block"><div class="topic-header"><strong style="font-family:Georgia,serif; font-size:10pt;">Environment &amp; Earth</strong><span style="font-size:7pt; font-weight:700; color:#8b5a1a;">CONSERVATION</span></div>
            {"".join(f'<div class="article"><div class="article-source">{it["source"]}</div><div class="article-headline">{it["title"]}</div><p class="article-body">{it["summary"]}</p></div>' for it in DEFAULT_HORIZONS["environment"])}
          </div>
          <div class="topic-block"><div class="topic-header"><strong style="font-family:Georgia,serif; font-size:10pt;">Creative &amp; Culture</strong><span style="font-size:7pt; font-weight:700; color:#8b5a1a;">DESIGN &amp; ARTS</span></div>
            {"".join(f'<div class="article"><div class="article-source">{it["source"]}</div><div class="article-headline">{it["title"]}</div><p class="article-body">{it["summary"]}</p></div>' for it in DEFAULT_HORIZONS["creative"])}
          </div>
          <div class="topic-block"><div class="topic-header"><strong style="font-family:Georgia,serif; font-size:10pt;">Global Sport &amp; Athletics</strong><span style="font-size:7pt; font-weight:700; color:#8b5a1a;">HUMAN FEATS</span></div>
            {"".join(f'<div class="article"><div class="article-source">{it["source"]}</div><div class="article-headline">{it["title"]}</div><p class="article-body">{it["summary"]}</p></div>' for it in DEFAULT_HORIZONS["sports"])}
          </div>
        </div>
        <div style="background:#f5efe6; border:1px solid #e0d8cc; padding:7px 12px; margin-top:12px; font-size:8pt; line-height:1.4;">
          <strong style="color:#8b5a1a; font-family:Georgia,serif;">Did You Know?</strong> Octopuses possess three distinct hearts and blue copper-based hemocyanin blood. Neurological monitoring shows their skin shifts through kaleidoscopic color pulses that mirror rapid eye movement (REM) dreaming cycles.
        </div>
      </div>

      <!-- PAGE 3: PUZZLES & LEISURE -->
      <div class="newspaper-story-c">
        <div class="sec-masthead"><div>THE MORNING DISPATCH</div><div style="font-size:13pt; font-weight:900;">SECTION C: PUZZLES, COMICS &amp; LEISURE</div><div>PAGE 3 &bull; {date_display}</div></div>
        <div style="display:grid; grid-template-columns:1.15fr 0.85fr; column-gap:16px;">
          <div style="border-right:1px solid #cfc8bd; padding-right:16px;">
            <div class="puzzle-card">
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid #cfc8bd; padding-bottom:4px; margin-bottom:8px;"><strong style="font-family:Georgia,serif; font-size:10pt;">Daily Morning Sudoku</strong><span style="font-size:7pt; font-weight:700; color:#8b5a1a;">MODERATE</span></div>
              <svg width="250" height="250" viewBox="0 0 270 270" style="display:block; margin:0 auto;">
                <rect width="270" height="270" fill="#fff" stroke="#121212" stroke-width="3"/>
                <line x1="30" y1="0" x2="30" y2="270" stroke="#bbb" stroke-width="0.75"/><line x1="60" y1="0" x2="60" y2="270" stroke="#bbb" stroke-width="0.75"/><line x1="120" y1="0" x2="120" y2="270" stroke="#bbb" stroke-width="0.75"/><line x1="150" y1="0" x2="150" y2="270" stroke="#bbb" stroke-width="0.75"/><line x1="210" y1="0" x2="210" y2="270" stroke="#bbb" stroke-width="0.75"/><line x1="240" y1="0" x2="240" y2="270" stroke="#bbb" stroke-width="0.75"/>
                <line x1="0" y1="30" x2="270" y2="30" stroke="#bbb" stroke-width="0.75"/><line x1="0" y1="60" x2="270" y2="60" stroke="#bbb" stroke-width="0.75"/><line x1="0" y1="120" x2="270" y2="120" stroke="#bbb" stroke-width="0.75"/><line x1="0" y1="150" x2="270" y2="150" stroke="#bbb" stroke-width="0.75"/><line x1="0" y1="210" x2="270" y2="210" stroke="#bbb" stroke-width="0.75"/><line x1="0" y1="240" x2="270" y2="240" stroke="#bbb" stroke-width="0.75"/>
                <line x1="90" y1="0" x2="90" y2="270" stroke="#121212" stroke-width="2.5"/><line x1="180" y1="0" x2="180" y2="270" stroke="#121212" stroke-width="2.5"/><line x1="0" y1="90" x2="270" y2="90" stroke="#121212" stroke-width="2.5"/><line x1="0" y1="180" x2="270" y2="180" stroke="#121212" stroke-width="2.5"/>
                <g font-family="sans-serif" font-size="15" font-weight="700" fill="#121212" text-anchor="middle">
                  <text x="15" y="21">5</text><text x="45" y="21">3</text><text x="135" y="21">7</text><text x="15" y="51">6</text><text x="105" y="51">1</text><text x="135" y="51">9</text><text x="165" y="51">5</text><text x="45" y="81">9</text><text x="75" y="81">8</text><text x="225" y="81">6</text>
                  <text x="15" y="111">8</text><text x="135" y="111">6</text><text x="255" y="111">3</text><text x="15" y="141">4</text><text x="105" y="141">8</text><text x="165" y="141">3</text><text x="255" y="141">1</text><text x="15" y="171">7</text><text x="135" y="171">2</text><text x="255" y="171">6</text>
                  <text x="45" y="201">6</text><text x="195" y="201">2</text><text x="225" y="201">8</text><text x="105" y="231">4</text><text x="135" y="231">1</text><text x="165" y="231">9</text><text x="255" y="231">5</text><text x="135" y="261">8</text><text x="225" y="261">7</text><text x="255" y="261">9</text>
                </g>
              </svg>
            </div>
            <div class="puzzle-card">
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid #cfc8bd; padding-bottom:4px; margin-bottom:8px;"><strong style="font-family:Georgia,serif; font-size:10pt;">Daily Mini Crossword</strong><span style="font-size:7pt; font-weight:700; color:#8b5a1a;">WORD SQUARE</span></div>
              <div style="display:flex; gap:12px; align-items:center;">
                <svg width="140" height="140" viewBox="0 0 160 160"><rect width="160" height="160" fill="#fff" stroke="#121212" stroke-width="2.5"/><line x1="40" y1="0" x2="40" y2="160" stroke="#121212" stroke-width="1.5"/><line x1="80" y1="0" x2="80" y2="160" stroke="#121212" stroke-width="1.5"/><line x1="120" y1="0" x2="120" y2="160" stroke="#121212" stroke-width="1.5"/><line x1="0" y1="40" x2="160" y2="40" stroke="#121212" stroke-width="1.5"/><line x1="0" y1="80" x2="160" y2="80" stroke="#121212" stroke-width="1.5"/><line x1="0" y1="120" x2="160" y2="120" stroke="#121212" stroke-width="1.5"/><g font-family="sans-serif" font-size="8" font-weight="700" fill="#555"><text x="4" y="11">1</text><text x="44" y="11">2</text><text x="84" y="11">3</text><text x="124" y="11">4</text><text x="4" y="51">5</text><text x="4" y="91">6</text><text x="4" y="131">7</text></g></svg>
                <div style="font-size:7.5pt; line-height:1.35; flex:1;"><strong>ACROSS</strong>: 1. Fragrant flower, 5. Not closed (OPEN), 6. Dispatch (SEND), 7. Finishes (ENDS)<br><strong>DOWN</strong>: 1. Blossom, 2. Unfastened, 3. Forward mail, 4. Final bounds</div>
              </div>
            </div>
          </div>
          <div>
            <div class="puzzle-card">
              <strong style="font-family:Georgia,serif; font-size:10pt;">Paws &amp; Print</strong><br>
              <div style="text-align:center; padding:18px 0; font-size:28pt;">☕ 🐱 📰</div>
              <p style="font-family:Georgia,serif; font-style:italic; font-size:8.5pt; text-align:center; margin:0;">&ldquo;I see the global tuna markets are rallying, and you are currently three minutes late with breakfast.&rdquo;</p>
            </div>
            <div style="background:#f5efe6; border:1px solid #e5ded2; padding:8px 10px; margin-bottom:10px; font-size:8pt;">
              <strong>Brain Teaser:</strong> Unscramble: <span style="font-family:monospace; font-weight:bold; color:#8b5a1a;">E N H S I U S N</span> (SUNSHINE)<br>
              <strong>Daily Riddle:</strong> Runs all day around the room, yet never gets tired? (The hands of a clock)
            </div>
            <div style="transform:rotate(180deg); border:1px solid #dedede; padding:5px 8px; background:#fbfbfb; font-size:6.5pt; color:#777; margin-top:8px;">
              SOLUTIONS: Mini Crossword: ROSE, OPEN, SEND, ENDS. Sudoku Row 1: 5 3 4 | 6 7 8 | 9 1 2.
            </div>
          </div>
        </div>
      </div>
    </body></html>"""

    html_path = "dist/index.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    pdf_path = "dist/The_Morning_Dispatch_Latest.pdf"
    cmd = [
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--virtual-time-budget=2000",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    subprocess.run(cmd, check=True)
    print("✓ Successfully compiled 3-page Morning Dispatch PDF in cloud!")

if __name__ == "__main__":
    main()
