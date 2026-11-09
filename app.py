from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
from zoneinfo import ZoneInfo
import sqlite3, secrets, re
from config import SECRET_KEY, DATABASE, APP_TIMEZONE

app = Flask(__name__)
app.secret_key = SECRET_KEY
Path(DATABASE).parent.mkdir(parents=True, exist_ok=True)

ALLOWED_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be",
    "instagram.com", "www.instagram.com",
    "whatsapp.com", "www.whatsapp.com", "web.whatsapp.com",
    "telegram.org", "www.telegram.org", "t.me",
    "snapchat.com", "www.snapchat.com", "vimeo.com", "www.vimeo.com"
}

def db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL,
            destination TEXT NOT NULL, created_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT, link_code TEXT NOT NULL,
            browser TEXT NOT NULL, device TEXT NOT NULL, visited_at TEXT NOT NULL,
            FOREIGN KEY(link_code) REFERENCES links(code))""")

def now_text():
    try:
        return datetime.now(ZoneInfo(APP_TIMEZONE)).strftime("%d-%m-%Y %I:%M:%S %p")
    except Exception:
        return datetime.now().astimezone().strftime("%d-%m-%Y %I:%M:%S %p")

def detect_browser_device(user_agent):
    ua = (user_agent or "").lower()
    if "edg/" in ua: browser = "Microsoft Edge"
    elif "opr/" in ua or "opera" in ua: browser = "Opera"
    elif "firefox/" in ua: browser = "Firefox"
    elif "chrome/" in ua and "chromium" not in ua: browser = "Google Chrome"
    elif "safari/" in ua and "chrome/" not in ua: browser = "Safari"
    else: browser = "Other / Unknown"
    if "ipad" in ua or "tablet" in ua: device = "Tablet"
    elif any(x in ua for x in ("mobile", "android", "iphone")): device = "Mobile"
    else: device = "Desktop"
    return browser, device

def validate_url(value):
    value = (value or "").strip()
    if not value: return None
    if not re.match(r"^https?://", value, re.I): value = "https://" + value
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in ("http", "https") or host not in ALLOWED_HOSTS: return None
    return value

@app.route("/")
def home():
    return render_template("index.html", generated_link=None)

@app.route("/generate", methods=["POST"])
def generate():
    destination = validate_url(request.form.get("destination"))
    if not destination:
        flash("Enter a valid URL from a supported website.", "error")
        return redirect(url_for("home"))
    code = secrets.token_urlsafe(8).replace("-", "").replace("_", "")[:8]
    with db() as conn:
        while conn.execute("SELECT 1 FROM links WHERE code=?", (code,)).fetchone():
            code = secrets.token_urlsafe(8).replace("-", "").replace("_", "")[:8]
        conn.execute("INSERT INTO links(code,destination,created_at) VALUES(?,?,?)",
                     (code, destination, now_text()))
    link = url_for("visit", code=code, _external=True)
    return render_template("index.html", generated_link=link, destination=destination)

@app.route("/r/<code>")
def visit(code):
    with db() as conn:
        link = conn.execute("SELECT destination FROM links WHERE code=?", (code,)).fetchone()
        if not link: return render_template("not_found.html"), 404
        browser, device = detect_browser_device(request.headers.get("User-Agent", ""))
        conn.execute("INSERT INTO visits(link_code,browser,device,visited_at) VALUES(?,?,?,?)",
                     (code, browser, device, now_text()))
        destination = link["destination"]
    return redirect(destination, code=302)

@app.route("/dashboard")
def dashboard():
    with db() as conn:
        total_visits = conn.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
        total_links = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
        browsers = conn.execute("SELECT browser,COUNT(*) total FROM visits GROUP BY browser ORDER BY total DESC").fetchall()
        devices = conn.execute("SELECT device,COUNT(*) total FROM visits GROUP BY device ORDER BY total DESC").fetchall()
        recent = conn.execute("""SELECT visits.*, links.destination FROM visits
            LEFT JOIN links ON visits.link_code=links.code ORDER BY visits.id DESC LIMIT 10""").fetchall()
    return render_template("dashboard.html", total_visits=total_visits, total_links=total_links,
                           browsers=browsers, devices=devices, visits=recent)

@app.route("/analytics")
def analytics():
    with db() as conn:
        visits = conn.execute("""SELECT visits.*, links.destination FROM visits
            LEFT JOIN links ON visits.link_code=links.code ORDER BY visits.id DESC""").fetchall()
    return render_template("analytics.html", visits=visits, total=len(visits))

@app.route("/links")
def links():
    with db() as conn:
        links = conn.execute("""SELECT links.*,COUNT(visits.id) visits_count FROM links
            LEFT JOIN visits ON links.code=visits.link_code GROUP BY links.code ORDER BY links.id DESC""").fetchall()
    return render_template("links.html", links=links)

@app.route("/clear-analytics", methods=["POST"])
def clear_analytics():
    with db() as conn: conn.execute("DELETE FROM visits")
    flash("Analytics history cleared.", "success")
    return redirect(url_for("analytics"))

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
