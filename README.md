# European Press Review

A scheduled, automated daily digest of European news on digital speech, content deletion, and online censorship — delivered as a static web app on GitHub Pages.

Each weekday morning, a GitHub Actions job queries the Perplexity Sonar Pro API, saves a structured JSON digest, rebuilds the Svelte frontend, and deploys it to GitHub Pages. No server. No database. No subscription beyond pay-as-you-go API credits (~$1–3/month).

---

## How it works

```
Perplexity Sonar Pro API
        │
        ▼
scraper/press_review.py     ← runs daily via GitHub Actions cron
        │  writes YYYY-MM-DD.json + index.json
        ▼
web/static/data/            ← committed to main, served as static assets
        │
        ▼
SvelteKit build             ← adapter-static, deployed to gh-pages branch
        │
        ▼
GitHub Pages                ← your live site
```

---

## Stack

| Layer | Tool |
|---|---|
| Search + synthesis | Perplexity Sonar Pro |
| Scraper | Python 3.11 + openai SDK (Perplexity-compatible) |
| Frontend | SvelteKit + adapter-static |
| Scheduling + CI | GitHub Actions |
| Hosting | GitHub Pages |

---

## Repo layout

```
press-review/
├── .github/workflows/
│   └── daily.yml          # cron job: scrape → commit → build → deploy
├── scraper/
│   ├── press_review.py    # fetches digest, writes JSON + index
│   └── requirements.txt
└── web/                   # SvelteKit app
    ├── src/
    │   ├── routes/
    │   │   ├── +page.js       # CSR load: fetch index + latest digest
    │   │   └── +page.svelte   # main view, client-side date switching
    │   └── lib/
    │       └── ArticleCard.svelte
    └── static/data/       # JSON digests live here
```

---

## Deploy to GitHub Pages

### 1. Get a Perplexity API key

Sign up at [perplexity.ai/api-platform](https://www.perplexity.ai/api-platform), add billing, and generate a key. Expected cost: ~$1–3/month at daily frequency.

### 2. Push the repo to GitHub

```bash
git init
git add .
git commit -m "init"
gh repo create press-review --public --push --source .
```

### 3. Add the API key as a secret

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|---|---|
| `PERPLEXITY_API_KEY` | your key |

### 4. Set the base path variable (if not using a custom domain)

GitHub Pages serves project repos at `https://username.github.io/press-review`. The SvelteKit build needs to know this prefix.

In your repo: **Settings → Secrets and variables → Actions → Variables → New repository variable**

| Name | Value |
|---|---|
| `BASE_PATH` | `/press-review` |

If you're using a custom domain (e.g. `review.yourdomain.com`), skip this step — leave `BASE_PATH` unset.

### 5. Enable GitHub Pages

In your repo: **Settings → Pages**

- Source: **Deploy from a branch**
- Branch: `gh-pages` / `/ (root)`

The `gh-pages` branch is created automatically on the first workflow run.

### 6. Run the workflow

Go to **Actions → Daily Press Review → Run workflow**.

After ~2 minutes your site will be live at `https://username.github.io/press-review`.

From then on it runs automatically at 07:00 UTC, Monday–Friday.

---

## Local development

### Run the scraper

```bash
cd scraper
pip install -r requirements.txt
export PERPLEXITY_API_KEY=your_key_here
python press_review.py
# output lands in web/static/data/
```

### Run the frontend

```bash
cd web
npm install
npm run dev
# open http://localhost:5173
```

### Build for production

```bash
cd web
BASE_PATH=/press-review npm run build
npm run preview  # preview at http://localhost:4173
```

---

## Configuration

### Change the topic

Edit `USER_PROMPT` in `scraper/press_review.py`. The current topic covers:

- Politicians or public figures deleting social media posts
- Government-ordered content removal
- Platform moderation controversies involving political figures
- Court orders to remove political speech online

### Change the schedule

Edit the cron expression in `.github/workflows/daily.yml`:

```yaml
- cron: '0 7 * * 1-5'   # 07:00 UTC, Monday–Friday
```

Note: GitHub Actions cron runs in UTC. German/Central European Time is UTC+1 (winter) or UTC+2 (summer), so `0 7 * * *` hits at 08:00–09:00 CET.

### Extend the recency window

In `scraper/press_review.py`, change `search_recency_filter`:

```python
extra_body={"search_recency_filter": "week"},   # or "day", "month"
```

---

## Cost

| Item | Cost |
|---|---|
| Perplexity Sonar Pro | ~$0.02–0.06 per run |
| GitHub Actions | Free (well within free tier) |
| GitHub Pages | Free |
| **Total** | **~$1–3/month** |

---

## Known limitations

- **Citations are a flat list** — Perplexity returns source URLs as a list, not linked per article. They appear in the Sources section below the digest.
- **Coverage varies by topic** — niche topics may return few articles on quiet news days. The editorial overview will say so honestly rather than hallucinate.
- **Index lag** — Perplexity's index lags by several hours. The 07:00 UTC run reliably captures the prior day's press.
