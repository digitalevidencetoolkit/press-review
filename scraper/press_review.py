import glob
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from openai import OpenAI

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "web/static/data")

SYSTEM_PROMPT = """You are an editorial assistant producing a daily press review.
Always write in English. Be concise, factual, and neutral in tone. Do not editorialise.
Include sources in any European language. Prioritise established news outlets. Do not invent or paraphrase sources — only report what you find.

For each relevant article, extract:
- The headline translated into English
- The source publication name and country
- The direct URL to the article
- A 2-3 sentence English summary
- One sentence on why it matters for investigators and journalists who need to preserve and authenticate disappearing digital content as evidence — focusing on what is at risk of being deleted, suppressed, or disputed, and why that creates an evidentiary challenge

Return a JSON object matching the schema provided."""

TOPICS = [
    (
        "Politicians deleting posts",
        "Search European news from the last week: politicians or public figures deleting social media posts, tweets, or messages.",
    ),
    (
        "Controversial statements online",
        "Search European news from the last week: politicians or public figures making controversial or inflammatory statements on social media.",
    ),
    (
        "Government-ordered content removal",
        "Search European news from the last week: online content removal ordered or pressured by governments or political actors.",
    ),
    (
        "Censorship of digital speech",
        "Search European news from the last week: censorship or suppression of digital public speech in Europe.",
    ),
    (
        "Platform moderation controversies",
        "Search European news from the last week: platform moderation controversies involving political figures in Europe.",
    ),
    (
        "Court and regulatory orders",
        "Search European news from the last week: court or regulatory orders to remove political speech online in Europe.",
    ),
]

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "articles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "headline_en": {"type": "string"},
                            "source": {"type": "string"},
                            "source_url": {"type": "string"},
                            "summary_en": {"type": "string"},
                            "significance": {"type": "string"},
                        },
                        "required": [
                            "headline_en",
                            "source",
                            "source_url",
                            "summary_en",
                            "significance",
                        ],
                    },
                },
            },
            "required": ["articles"],
        }
    },
}


def query_topic(client, label, prompt):
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format=RESPONSE_FORMAT,
        extra_body={"search_recency_filter": "week"},
    )
    articles = json.loads(response.choices[0].message.content)["articles"]
    for a in articles:
        a["topic"] = label
    citations = getattr(response, "citations", [])
    return articles, citations


def merge_articles(all_articles):
    seen_urls = set()
    seen_headlines = set()
    merged = []
    for article in all_articles:
        url = article.get("source_url", "")
        headline = article["headline_en"]
        if (url and url in seen_urls) or headline in seen_headlines:
            continue
        seen_urls.add(url)
        seen_headlines.add(headline)
        merged.append(article)
    return merged


def update_index(output_dir):
    files = sorted(glob.glob(f"{output_dir}/????-??-??.json"), reverse=True)
    dates = [os.path.splitext(os.path.basename(f))[0] for f in files]
    with open(f"{output_dir}/index.json", "w", encoding="utf-8") as f:
        json.dump({"dates": dates}, f)


def main():
    client = OpenAI(
        api_key=os.environ["PERPLEXITY_API_KEY"],
        base_url="https://api.perplexity.ai",
    )

    all_articles = []
    all_citations = []

    with ThreadPoolExecutor(max_workers=len(TOPICS)) as executor:
        futures = {
            executor.submit(query_topic, client, label, prompt): label
            for label, prompt in TOPICS
        }
        for future in as_completed(futures):
            label = futures[future]
            try:
                articles, citations = future.result()
                print(f"  [{label}] {len(articles)} articles found")
                all_articles.extend(articles)
                all_citations.extend(citations)
            except Exception as e:
                print(f"  [{label}] Error: {e}", file=sys.stderr)

    merged = merge_articles(all_articles)
    citations = list(dict.fromkeys(all_citations))

    if not merged:
        print("Warning: no articles found.", file=sys.stderr)

    today = str(date.today())
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = f"{OUTPUT_DIR}/{today}.json"

    digest = {"date": today, "articles": merged, "citations": citations}

    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        existing_headlines = {a["headline_en"] for a in existing["articles"]}
        existing_urls = {a.get("source_url", "") for a in existing["articles"]}
        new_articles = [
            a
            for a in merged
            if a["headline_en"] not in existing_headlines
            and a.get("source_url", "") not in existing_urls
        ]
        existing["articles"].extend(new_articles)
        existing["citations"] = list(
            dict.fromkeys(existing.get("citations", []) + citations)
        )
        digest = existing
        print(f"Merged {len(new_articles)} new articles into existing file")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(digest, f, indent=2, ensure_ascii=False)

    update_index(OUTPUT_DIR)
    print(f"Saved {len(digest['articles'])} articles total → {out_path}")


if __name__ == "__main__":
    main()
