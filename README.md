# GA4 AI Agent

An AI-powered Google Analytics 4 assistant built with Claude (Anthropic) and Python.
The agent answers natural language questions about website analytics data,
runs advanced Python analysis, and exports results to PDF reports.

## Features

- Natural language queries about GA4 data
- Automatic metric selection based on question context
- Safe Python code execution in a sandboxed environment
- PDF report export
- Mock mode for testing without real GA4 access

## Tech Stack

- Python 3.12+
- Anthropic Claude API (claude-opus-4-5)
- Google Analytics Data API
- ReportLab (PDF generation)

## Project Structure

    ga4-ai-agent/
    ├── agent/
    │   ├── agent.py        # Main agent loop with tool use
    │   ├── tools.py        # Tool definitions for Claude
    │   ├── ga4_client.py   # GA4 API client (real + mock)
    │   └── sandbox.py      # Safe Python code execution
    ├── output/
    │   └── reports/        # Generated PDF reports
    ├── main.py             # CLI entry point
    ├── .env.example        # Environment variables template
    └── requirements.txt    # Python dependencies

## Setup

1. Clone the repository

        git clone https://github.com/YOUR_USERNAME/ga4-ai-agent.git
        cd ga4-ai-agent

2. Create virtual environment and install dependencies

        python -m venv .venv
        .venv\Scripts\activate
        pip install -r requirements.txt

3. Copy .env.example to .env

        cp .env.example .env

4. Fill in your credentials in .env

        ANTHROPIC_API_KEY=your_anthropic_api_key
        GA4_PROPERTY_ID=your_ga4_property_id
        GOOGLE_APPLICATION_CREDENTIALS=credentials.json

5. Place your Google service account JSON file in the project root as credentials.json

## Running

    python main.py

## Switching to Real GA4 Data

By default the agent runs in mock mode with realistic test data.
To connect real GA4, open agent/agent.py and change:

    use_mock=True  ->  use_mock=False

Make sure your service account email has Viewer access to your GA4 property.

## Example Questions

- How many users visited the site in the last 30 days?
- Show me sessions by device category this week
- What are the top traffic sources in the last 90 days?
- Compare new vs returning users last month and export to PDF

## Example Output

    You: How many users last 30 days? Export results to PDF.

    Thinking...

    Calling tool: query_ga4
    Calling tool: export_to_pdf

    Agent: Here are your website user statistics for the last 30 days:

    Metric          Value
    Active Users    12,137
    New Users        7,310
    Total Sessions  12,298

    PDF report saved to: output/reports/report_20260607_162915.pdf