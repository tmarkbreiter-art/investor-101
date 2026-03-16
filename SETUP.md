# Setup Guide — INVESTOR 101

## Step 1: Fork or create the repo
You already have the files. Just push them to GitHub as a repo named `investor-101`.

## Step 2: Enable GitHub Pages
1. Go to your repo on GitHub
2. Click **Settings** → **Pages**
3. Under "Source", select **Deploy from a branch**
4. Branch: `main` · Folder: `/docs`
5. Click **Save**
6. Your live URL will be: `https://YOUR_USERNAME.github.io/investor-101`

## Step 3: Add your API keys as Secrets
1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each one:

| Secret Name       | Value                        |
|-------------------|------------------------------|
| FINNHUB_API_KEY   | your Finnhub key             |
| GROQ_API_KEY      | your Groq key                |
| BUDGET            | e.g. 340                     |
| EMAIL_SENDER      | your Gmail address           |
| EMAIL_PASSWORD    | your Gmail app password      |
| EMAIL_RECEIVERS   | your email (comma-separated) |
| WATCHLIST         | e.g. NVDA,AAPL (optional)    |

## Step 4: Trigger a test run
1. Go to your repo → **Actions** tab
2. Click **AXIOM US Daily Run**
3. Click **Run workflow** → **Run workflow**
4. Watch it run — takes about 2 minutes
5. When done, visit your GitHub Pages URL to see the live dashboard

## Step 5: You're done
Every weekday at 8 AM ET it runs automatically.
You'll get an email and your dashboard URL updates.
