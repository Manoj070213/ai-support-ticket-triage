# AI-Powered Support Ticket Triage

An end-to-end AI pipeline that automatically classifies, prioritizes, and
summarizes customer support tickets using a large language model.

Built as a personal Project. The project takes raw support tickets,
sends each through Google's Gemini model to tag **category**, **urgency**, and
**sentiment** plus a one-line **summary**, and visualizes the results.

## The business problem

Support teams receive thousands of tickets. Sorting and prioritizing them by
hand is slow, inconsistent, and buries important signals like a spike in
billing complaints. This tool automates triage and reveals the trends a team
needs to act on.

## How it works

```
Ticket CSV  ->  Clean/prep  ->  LLM classifier  ->  Structured CSV  ->  Dashboard
```

1. `prep_data.py` cleans the raw dataset (replaces placeholder text, renames columns).
2. `classify_tickets.py` sends each ticket to Gemini and writes tags to a CSV.
3. `summarize.py` aggregates the results into the key numbers.

## Tech stack

- Python (standard library + Google Gemini API)
- Google Gemini (`gemini-2.5-flash-lite`), called via REST
- CSV as a lightweight data layer
- Chart.js for the dashboard visualization

## The data

A public customer-support dataset of 8,469 tickets across five issue types
(refund, technical, cancellation, product inquiry, billing), sourced from
Kaggle. Each ticket has a free-text description plus human-assigned type and
priority labels used for benchmarking.

## Setup

1. Install the dependency:
   ```
   pip install -r requirements.txt
   ```
2. Get a free Gemini API key at https://aistudio.google.com (see `README_GEMINI.md`).
3. Set it as an environment variable (never hard-code it):
   ```
   # Windows PowerShell
   $env:GEMINI_API_KEY="your-key-here"
   # Mac/Linux
   export GEMINI_API_KEY="your-key-here"
   ```

## Usage

```
python prep_data.py --input customer_support_tickets.csv --output tickets_ready.csv
python classify_tickets.py --input tickets_ready.csv --output classified.csv --limit 100
python summarize.py --input classified.csv
```

## Results (sample)

- 43% negative sentiment across the classified sample
- 20% of tickets flagged high urgency
- 100% auto-summarized — summaries the source data never had
- Full dataset is evenly split across five categories; half of all tickets are high-priority or critical

## Lessons learned

- Forcing the model to return strict JSON made outputs reliable and machine-readable.
- Free API tiers have real rate limits that cap sample size; production would need a paid tier or batching.
- Real-world data is messy — the raw dataset had placeholder text that needed cleaning first.
- API keys belong in environment variables, not in the code.

## Files

| File | Purpose |
|------|---------|
| `prep_data.py` | Cleans the raw dataset |
| `classify_tickets.py` | Runs the AI classification |
| `summarize.py` | Aggregates results into key numbers |
| `tickets_ready.csv` | Cleaned, ready-to-classify data |
| `sample_tickets.csv` | 10 tickets for quick testing |
| `requirements.txt` | Python dependencies |
| `AI_Ticket_Triage_Deck.pptx` | Project presentation (Phase 1 + 2) |
