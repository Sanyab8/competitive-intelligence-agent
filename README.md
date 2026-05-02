# Competitive Intelligence Agent

An agentic AI pipeline built with Claude AI that autonomously conducts 
competitive market research and generates analyst-grade PDF reports.

## How it works
1. You enter any company name
2. The agent autonomously searches the web multiple times
3. Visits competitor websites for deeper research  
4. Chains all findings together using a ReAct loop
5. Generates a formatted PDF report

## Tech Stack
- Python
- Anthropic Claude API (claude-opus-4-5)
- Google Search API
- BeautifulSoup4
- ReportLab

## Setup
1. Clone the repo
2. Install dependencies: pip install -r requirements.txt
3. Add your Anthropic API key to .env
4. Run: python app.py
