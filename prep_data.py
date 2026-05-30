"""
prep_data.py
------------
Prepares the raw Kaggle "Customer Support Ticket Dataset" for classification.

It does two things:
 1. Replaces the literal "{product_purchased}" placeholder in each ticket
    description with the real product name from the "Product Purchased" column.
 2. Renames "Ticket Description" to "ticket_text" so classify_tickets.py can
    read it.

It also keeps the human labels ("Ticket Type", "Ticket Priority") so you can
later compare them against the AI's tags.

HOW TO RUN:
    python prep_data.py --input customer_support_tickets.csv --output tickets_ready.csv
"""

import argparse
import csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="tickets_ready.csv")
    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    cleaned = []
    for r in rows:
        desc = r.get("Ticket Description", "") or ""
        product = r.get("Product Purchased", "") or "the product"
        # Swap the placeholder for the real product name.
        desc = desc.replace("{product_purchased}", product)
        cleaned.append({
            "ticket_id": r.get("Ticket ID", ""),
            "ticket_text": desc.strip(),
            "human_type": r.get("Ticket Type", ""),       # kept for benchmarking
            "human_priority": r.get("Ticket Priority", ""),
        })

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "ticket_text", "human_type", "human_priority"])
        writer.writeheader()
        writer.writerows(cleaned)

    print(f"Cleaned {len(cleaned)} tickets -> {args.output}")
    print("Placeholder swapped for real product names; 'Ticket Description' renamed to 'ticket_text'.")
    print("Next: python classify_tickets.py --input " + args.output + " --output classified.csv --limit 200")


if __name__ == "__main__":
    main()
