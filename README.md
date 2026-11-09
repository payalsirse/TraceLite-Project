# TraceLite – Complete Project

## Features
- Generate a unique tracking link for supported destinations.
- Clicking the tracking link redirects directly to the destination.
- The generator/dashboard page stays open; destination link opens in a new tab when using the button.
- Dashboard summary: total visits, generated links, browser and device counts.
- Analytics table: visit ID, tracking code, browser, device and date/time.
- My Links page: saved destination links and visit counts.
- SQLite database.

## Privacy (Basic option)
This version stores browser category, device category, timestamp, tracking-link code and destination URL. It does NOT store IP addresses, approximate location, city, region, country, or raw User-Agent strings. Browser/device detection is approximate.

## Supported domains
YouTube, Instagram, WhatsApp, Telegram, Snapchat and Vimeo. Edit `ALLOWED_HOSTS` in `app.py` to add exact hosts.

## Run on Windows
Open this folder in VS Code. In Terminal, run these commands one by one:

```powershell
py -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

Keep the terminal running. Open `http://127.0.0.1:5000`.

## Pages
- Home: `http://127.0.0.1:5000/`
- Dashboard: `http://127.0.0.1:5000/dashboard`
- Analytics: `http://127.0.0.1:5000/analytics`
- My Links: `http://127.0.0.1:5000/links`

## Important
A `127.0.0.1` tracking link works only on the same computer. To share links with people outside your computer, deploy the Flask app to a public HTTPS server and use its public domain. Before public deployment, add authentication to analytics, set a strong secret key, use HTTPS, and provide appropriate visitor notice/consent.
