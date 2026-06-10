import glob
import html
import json
import os
import sys
from datetime import date, datetime, timezone
from email.utils import format_datetime
from openai import OpenAI

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "web/static/data")

SYSTEM_PROMPT = """You are an editorial assistant producing a daily press review.
Always write in English. Be concise, factual, and neutral in tone. Do not editorialise."""

USER_PROMPT = """Search news from Europe published in the last week covering any of the following:
- Politicians or public figures deleting social media posts, tweets, or messages
- Politicians or public figures having said something controversial or infuriating on social media
- Online content removal ordered or pressured by governments or political actors
- Censorship or suppression of digital public speech
- Platform moderation controversies involving political figures
- Court or regulatory orders to remove political speech online

Include sources in any European language. Prioritise established news outlets. Do not invent or paraphrase sources — only report what you find.

For each relevant article, extract:
- The headline translated into English
- The source publication name and country
- A 2-3 sentence English summary
- One sentence on why it matters

Then write a short editorial overview (3-5 sentences) summarising the overall picture.

Return a JSON object matching the schema provided."""

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "topic": {"type": "string"},
                "articles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "headline_en": {"type": "string"},
                            "source": {"type": "string"},
                            "summary_en": {"type": "string"},
                            "significance": {"type": "string"},
                        },
                        "required": ["headline_en", "source", "summary_en", "significance"],
                    },
                },
                "editorial_overview": {"type": "string"},
            },
            "required": ["topic", "articles", "editorial_overview"],
        }
    },
}


def update_index(output_dir: str) -> None:
    files = sorted(glob.glob(f"{output_dir}/????-??-??.json"), reverse=True)
    dates = [os.path.splitext(os.path.basename(f))[0] for f in files]
    with open(f"{output_dir}/index.json", "w", encoding="utf-8") as f:
        json.dump({"dates": dates}, f)


def site_url(output_dir: str) -> str:
    if url := os.getenv("SITE_URL"):
        return url.rstrip("/")
    cname_path = os.path.join(os.path.dirname(output_dir), "CNAME")
    if os.path.exists(cname_path):
        with open(cname_path, encoding="utf-8") as f:
            host = f.read().strip()
            if host:
                return f"https://{host}"
    return "http://localhost:5173"


def update_feed(output_dir: str) -> None:
    files = sorted(glob.glob(f"{output_dir}/????-??-??.json"), reverse=True)
    base = site_url(output_dir)
    items = []
    for path in files:
        with open(path, encoding="utf-8") as f:
            digest = json.load(f)
        d = digest.get("date") or os.path.splitext(os.path.basename(path))[0]
        pub_dt = datetime.strptime(d, "%Y-%m-%d").replace(hour=7, tzinfo=timezone.utc)
        headlines = "".join(
            f"<li><strong>{html.escape(a['headline_en'])}</strong> — {html.escape(a['source'])}</li>"
            for a in digest.get("articles", [])
        )
        description = (
            f"<p>{html.escape(digest.get('editorial_overview', ''))}</p>"
            + (f"<ul>{headlines}</ul>" if headlines else "")
        )
        items.append(
            "<item>"
            f"<title>Press Review — {d}</title>"
            f"<link>{base}/?campaign=rss</link>"
            f'<guid isPermaLink="false">press-review-{d}</guid>'
            f"<pubDate>{format_datetime(pub_dt)}</pubDate>"
            f"<description><![CDATA[{description}]]></description>"
            "</item>"
        )

    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">'
        "<channel>"
        "<title>European Press Review</title>"
        f"<link>{base}/</link>"
        "<description>A daily digest of European news on digital speech, content deletion, and online censorship.</description>"
        "<language>en</language>"
        f"<lastBuildDate>{format_datetime(datetime.now(timezone.utc))}</lastBuildDate>"
        f'<atom:link href="{base}/feed.xml" rel="self" type="application/rss+xml" />'
        f"{''.join(items)}"
        "</channel></rss>"
    )

    feed_path = os.path.join(os.path.dirname(output_dir), "feed.xml")
    with open(feed_path, "w", encoding="utf-8") as f:
        f.write(feed)


def main():
    client = OpenAI(
        api_key=os.environ["PERPLEXITY_API_KEY"],
        base_url="https://api.perplexity.ai",
    )

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
        response_format=RESPONSE_FORMAT,
        extra_body={"search_recency_filter": "week"},
    )

    digest = json.loads(response.choices[0].message.content)
    digest["date"] = str(date.today())
    new_citations = getattr(response, "citations", [])

    if not digest["articles"]:
        print("Warning: no articles found.", file=sys.stderr)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = f"{OUTPUT_DIR}/{digest['date']}.json"

    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        existing_headlines = {a["headline_en"] for a in existing["articles"]}
        new_articles = [a for a in digest["articles"] if a["headline_en"] not in existing_headlines]
        existing["articles"].extend(new_articles)
        existing["citations"] = list(dict.fromkeys(existing.get("citations", []) + new_citations))
        digest = existing
        print(f"Merged {len(new_articles)} new articles into existing file")
    else:
        digest["citations"] = new_citations

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(digest, f, indent=2, ensure_ascii=False)

    update_index(OUTPUT_DIR)
    update_feed(OUTPUT_DIR)
    print(f"Saved {len(digest['articles'])} articles total → {out_path}")


if __name__ == "__main__":
    main()
