# Spotificate 🎵

> Turn your offline music collection into a Spotify playlist — automatically.

**Live at:** [spotificate.afr1ka.xyz](https://spotificate.afr1ka.xyz) \
**Quick Video Demo** [Google Drive](https://drive.google.com/file/d/1qbGBwIm9LkPk4ha2zH_aWzYs0NHtqFw2/view?usp=drive_link)

---

## 🚧 Status — Proof of Concept

> This app is fully built and deployed but is currently pending **Spotify Extended Quota approval**. Spotify restricts new developer apps to a whitelist of up to 25 manually added users until the app passes their review process. If you'd like to try it, reach out and I'll add your Spotify email to the whitelist. Extended Quota has been applied for and is pending approval.

---

## What It Does

Spotificate takes audio files sitting on your computer — MP3s, FLACs, WAVs, whatever — runs them through the [Audd.io](https://audd.io) song recognition API to identify them, finds each track on Spotify, and creates a private playlist on your account. All in one flow from the browser.

It also saves your playlist history so you can restore any previously created playlist to Spotify at any time.

---

## Features

- **Spotify OAuth 2.0** — log in securely with your Spotify account, no passwords handled by this app
- **Audio file upload** — drag and drop your offline songs directly in the browser
- **Live recognition** — watch each song get identified in real time as it's processed
- **Playlist creation** — recognized tracks are added to a new private Spotify playlist automatically
- **History & restore** — every playlist you create is saved and can be restored to Spotify at any time
- **Session-based API key** — your Audd.io key is held in memory for your session only, never stored

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Auth | Spotify OAuth 2.0 (Authorization Code Flow) |
| Song Recognition | Audd.io API |
| Database | SQLite |
| Container | Docker (multi-platform amd64 + arm64) |
| Orchestration | Kubernetes (k3s) |
| Ingress | ingress-nginx (hostNetwork) |
| TLS | cert-manager + wildcard certificate |
| Cloud | Oracle Cloud Infrastructure (Always Free Tier) |
| DNS | Porkbun |

---

## How It Works

1. **Login** with your Spotify account via OAuth
2. Go to **⚙ Settings** and paste your [Audd.io API key](https://dashboard.audd.io)
3. Go to **Create Playlist**, name it, and upload your audio files
4. Watch the live recognition — each song is identified and matched to Spotify
5. Your playlist is created on Spotify and saved to your history

Full setup guide at [spotificate.afr1ka.xyz/how-it-works](https://spotificate.afr1ka.xyz/how-it-works)

---

## Running Locally

```bash
git clone https://github.com/afrikafunda/spotificate.git
cd spotificate
pip install -r requirements.txt
```

Create a `.env` file in the root:
```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
FLASK_SECRET_KEY=any_random_string
```

Then run:
```bash
python app.py
```

Visit `http://localhost:5000`. Make sure `http://localhost:5000/redirect` is added as a redirect URI in your [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

---

## Project Background

This started as a terminal-based Python script and evolved into a full web application. The original version required running two separate terminal processes and manually clicking a localhost link. The web version consolidates everything into a single browser flow with a proper UI, user scoping, and cloud deployment.

---

## About

Built by **Afrika Funda**

[LinkedIn](https://linkedin.com/in/afrika-adumise-funda-1a7270253) · [Live App](https://spotificate.afr1ka.xyz) · 