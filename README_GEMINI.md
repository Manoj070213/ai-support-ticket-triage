# Free setup with Google Gemini (no credit card)

This project uses Google's Gemini API, which has a free tier — no payment, no
credit card. The free tier allows about 1,500 requests per day, far more than
the 200 tickets we classify.

## Step 1 — Install the package
In PowerShell, inside your project folder:

    pip install -r requirements.txt

## Step 2 — Get your free Gemini API key
1. Go to https://aistudio.google.com
2. Sign in with any Google account.
3. Click "Get API key" (top right or left menu).
4. Click "Create API key" → "Create API key in new project".
5. Copy the key and keep it somewhere safe. Do NOT share it publicly.

No billing setup is required. You can skip any payment prompts.

## Step 3 — Tell PowerShell about your key
Paste this, replacing the placeholder with your real key (keep the quotes):

    $env:GEMINI_API_KEY="paste-your-key-here"

Press Enter. Nothing visible happens — that's normal. (You redo this line each
time you open a new PowerShell window.)

## Step 4 — Test on the sample
    python classify_tickets.py --input sample_tickets.csv --output test.csv

You'll see 10 tickets get tagged live. This is completely free.

## Step 5 — Run on the real data
    python classify_tickets.py --input tickets_ready.csv --output classified.csv --limit 200

This classifies 200 real tickets. At ~4.5 seconds per ticket (to stay under the
free rate limit), expect this to take about 15 minutes. Let it run.

## Step 6 — Get your summary numbers
    python summarize.py --input classified.csv

Then bring those numbers back to the chat to build your dashboard and slides.

## Note for your write-up
The free Gemini tier may use prompts to improve Google's models. That's fine for
a public Kaggle dataset like this one, but worth knowing — and a good detail to
mention in an interview when discussing data privacy considerations.
