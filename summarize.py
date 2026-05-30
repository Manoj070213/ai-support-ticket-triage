"""
summarize.py
------------
Reads the classified.csv produced by classify_tickets.py and prints the
key numbers you need for your dashboard and slide deck:
 - total tickets
 - count + percent by category
 - count + percent by urgency
 - percent negative sentiment
 - top recurring summaries

No API key needed -- this just crunches the CSV you already made.

HOW TO RUN:
    python summarize.py --input classified.csv
"""

import argparse
import csv
from collections import Counter


def pct(part, whole):
    return round(100 * part / whole) if whole else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="classified.csv")
    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    cats = Counter(r["category"] for r in rows)
    urg = Counter(r["urgency"] for r in rows)
    sent = Counter(r["sentiment"] for r in rows)
    summaries = Counter(r["summary"] for r in rows)

    print(f"\n=== TICKET TRIAGE SUMMARY ===")
    print(f"Total tickets: {total}\n")

    print("By category:")
    for cat, n in cats.most_common():
        print(f"  {cat:<18} {n:>4}  ({pct(n, total)}%)")

    print("\nBy urgency:")
    for level in ["High", "Medium", "Low"]:
        n = urg.get(level, 0)
        print(f"  {level:<8} {n:>4}  ({pct(n, total)}%)")

    print(f"\nNegative sentiment: {pct(sent.get('Negative', 0), total)}%")
    print(f"High-urgency tickets: {urg.get('High', 0)}")

    print("\nTop 5 recurring issues:")
    for summary, n in summaries.most_common(5):
        print(f"  {n:>3}x  {summary}")

    print("\nUse these numbers for your slide deck and to validate the dashboard.\n")


if __name__ == "__main__":
    main()
