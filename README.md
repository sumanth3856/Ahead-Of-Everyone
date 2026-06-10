# 🚀 Ahead of Everyone (AoE) - Daily Tech Digest

<div align="center">
  <h3><em>"Five minutes. Then you are ahead of everyone."</em></h3>
  <p>A fully autonomous, AI-powered tech journalism pipeline that scrapes global news, writes premium editorial summaries, and delivers a stunning dark-mode PDF magazine straight to Telegram every single morning.</p>
</div>

---

## ⚡ The Architecture

This project is a 100% serverless, zero-maintenance Python pipeline running on **GitHub Actions**.

1. **Multi-Source RSS Aggregation:** Scrapes the last 24 hours of news from *TechCrunch, The Verge, Wired,* and *HackerNews*.
2. **AI Editorial Engine:** Feeds raw, messy HTML into a multi-model AI cascade. The AI structures the news into a premium editorial format (`The Brief`, `Core Breakdown`, and `The Edge`).
3. **Custom UI Rendering:** Utilizes a custom `fpdf2` engine to render a gorgeous, dark-mode cyberpunk PDF (featuring a custom `Deep Purple #711bd1` palette and custom Montserrat typography).
4. **Automated Dispatch:** Dispatches the final PDF payload via the Telegram Bot API.

---

## 🧠 Multi-Model AI Cascade

To guarantee absolute reliability and maximize free-tier API usage, the scraper features a **Multi-Model Fallback Cascade** via OpenRouter:

*   **Primary Engine:** `nvidia/nemotron-3-ultra-550b-a55b:free` (A massive 619B parameter heavyweight for deep analysis).
*   **Secondary Engine:** `google/gemma-4-31b-it:free` (Extremely fast, highly capable fallback).
*   **Tertiary Engine:** `openrouter/free` (Dynamically routes to the most available free model globally).

If all AI models hit their daily rate limit, the system gracefully degrades to a **Raw Text Fallback**, guaranteeing the PDF magazine is still generated and delivered without crashing the pipeline.

---

## 🛠️ Tech Stack

*   **Python 3.11** (Core Logic)
*   **OpenRouter API** (LLM Routing & Summarization)
*   **FPDF2** (PDF Generation & UI Rendering)
*   **Feedparser** (RSS Scraping)
*   **GitHub Actions** (CRON Scheduling & Automation)
*   **Telegram API** (Payload Delivery)

---

## ⚙️ Deployment & Setup

You do not need a server to run this. It is entirely powered by GitHub Actions.

### 1. Environment Variables (Secrets)
Go to your GitHub Repository **Settings > Secrets and variables > Actions > New repository secret** and add the following:

| Secret Name | Description |
| :--- | :--- |
| `OPENROUTER_API_KEY` | Your free API key from [OpenRouter.ai](https://openrouter.ai/) |
| `TELEGRAM_BOT_TOKEN` | The token given to you by Telegram's `@BotFather` |
| `TELEGRAM_CHAT_ID` | The Chat ID of the user/channel receiving the PDF |

### 2. Autonomous Execution
The pipeline is pre-configured via `.github/workflows/daily_digest.yml`.
By default, it is set to run automatically on a `cron` schedule every single day. 

*You can also trigger it manually at any time by going to the **Actions** tab in GitHub and clicking **Run workflow**.*

---

<div align="center">
  <p><strong>Curated & Engineered by Sumanth.</strong></p>
</div>