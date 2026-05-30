"""
classify_tickets.py  (Gemini free-tier version, direct REST call)
-----------------------------------------------------------------
Reads a CSV of support tickets, sends each one to Google's Gemini model to tag
it with category, urgency, sentiment, and a one-line summary, then writes the
results to a new CSV that the dashboard reads.

This version calls the Gemini REST API directly, which works with both the new
"AQ." style keys and the older "AIza" keys from Google AI Studio (free tier,
no credit card).

HOW TO RUN:
    python classify_tickets.py --input tickets_ready.csv --output classified.csv --limit 200

The input CSV must have a column called "ticket_text".
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.request
import urllib.error

CATEGORIES = [
    "Refund request",
    "Technical issue",
    "Cancellation request",
    "Product inquiry",
    "Billing inquiry",
    "Other",
]

MODEL = "gemini-2.5-flash-lite"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

PROMPT_TEMPLATE = """You are a support-ticket triage assistant.

Read the customer ticket below and respond with ONLY a JSON object,
no extra words, no markdown fences. Use exactly these keys:

- "category": one of {categories}
- "urgency": one of "High", "Medium", "Low"
- "sentiment": one of "Positive", "Neutral", "Negative"
- "summary": a single sentence (max 15 words) describing the issue

Customer ticket:
\"\"\"{ticket}\"\"\"
"""

FALLBACK = {
    "category": "Other",
    "urgency": "Medium",
    "sentiment": "Neutral",
    "summary": "Could not classify.",
}


def classify_one(api_key, ticket_text):
    """Send a single ticket to Gemini via REST and return a dict of tags."""
    prompt = PROMPT_TEMPLATE.format(
        categories=", ".join(CATEGORIES),
        ticket=ticket_text.strip(),
    )
    url = ENDPOINT.format(model=MODEL)
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")

    for attempt in range(6):
        try:
            req = urllib.request.Request(url, data=body, method="POST")
            req.add_header("Content-Type", "application/json")
            # Pass the key as a header -- works with AQ. and AIza keys.
            req.add_header("x-goog-api-key", api_key)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1].replace("json", "", 1).strip()
            return json.loads(raw)
        except (json.JSONDecodeError, KeyError, IndexError):
            return dict(FALLBACK, summary="Could not parse model output.")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")
            if e.code == 429:
                # Rate limit hit. Wait longer and retry (don't give up).
                wait = 60
                print(f"    (rate limit hit -- waiting {wait}s and retrying...)")
                time.sleep(wait)
                continue
            if attempt < 2:
                time.sleep(5)
            else:
                print(f"    (HTTP {e.code} error: {detail[:200]})")
                return dict(FALLBACK, summary="Skipped due to API error.")
        except Exception as e:
            if attempt < 2:
                time.sleep(5)
            else:
                print(f"    (error: {e})")
                return dict(FALLBACK, summary="Skipped due to API error.")
    # If all retries are exhausted (e.g. repeated rate limits), never return
    # None -- return safe fallback tags so the script keeps going.
    return dict(FALLBACK, summary="Skipped after repeated rate limits.")


def main():
    parser = argparse.ArgumentParser(description="Classify support tickets with Gemini.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="classified.csv")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set your GEMINI_API_KEY environment variable first.")
        print("See README_GEMINI.md for how to get a free key.")
        sys.exit(1)

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "ticket_text" not in reader.fieldnames:
            print("ERROR: Your CSV needs a column named 'ticket_text'.")
            print("Columns found:", reader.fieldnames)
            sys.exit(1)
        rows = list(reader)

    if args.limit > 0:
        rows = rows[: args.limit]

    print(f"Classifying {len(rows)} tickets with Gemini (free tier)...")

    fieldnames = list(rows[0].keys()) + ["category", "urgency", "sentiment", "summary"]
    seen = set()
    fieldnames = [c for c in fieldnames if not (c in seen or seen.add(c))]

    results = []
    for i, row in enumerate(rows, start=1):
        tags = classify_one(api_key, row["ticket_text"])
        results.append({**row, **tags})
        print(f"  [{i}/{len(rows)}] {tags['category']} | {tags['urgency']} | {tags['sentiment']}")

        # Save progress after EVERY ticket so nothing is ever lost, even if you
        # stop the script or it errors out.
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        time.sleep(8)

    print(f"\nDone. Wrote {len(results)} classified tickets to {args.output}")
    print("Next: python summarize.py --input " + args.output)


if __name__ == "__main__":
    main()
