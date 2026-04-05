import glob
import json
import os
import sys
from datetime import date
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
- The direct URL to the article
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
                            "source_url": {"type": "string"},
                            "summary_en": {"type": "string"},
                            "significance": {"type": "string"},
                        },
                        "required": ["headline_en", "source", "source_url", "summary_en", "significance"],
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
    print(f"Saved {len(digest['articles'])} articles total → {out_path}")


if __name__ == "__main__":
    main()
