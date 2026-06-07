TOOLS = [
    {
        "name": "query_ga4",
        "description": """Query Google Analytics 4 data. Use this tool when the user asks
        about website metrics like users, sessions, pageviews, bounce rate, etc.
        Always use this before run_python_code unless you already have the data.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": """List of GA4 metrics to fetch. Available metrics:
                    - activeUsers (active users)
                    - sessions (number of sessions)  
                    - screenPageViews (pageviews)
                    - bounceRate (bounce rate 0-1)
                    - averageSessionDuration (avg session duration in seconds)
                    - newUsers (new users)
                    - totalRevenue (total revenue)"""
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date in format YYYY-MM-DD or relative like '7daysAgo', '30daysAgo', 'yesterday'"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in format YYYY-MM-DD or 'today'"
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": """Optional dimensions to group by:
                    - date (by day)
                    - country (by country)
                    - deviceCategory (mobile/desktop/tablet)
                    - pagePath (by page)
                    - sessionSource (traffic source)"""
                }
            },
            "required": ["metrics", "start_date", "end_date"]
        }
    },
    {
        "name": "run_python_code",
        "description": """Execute Python code for advanced data analysis.
        Use this when you need to calculate, transform, or visualize data
        that you already fetched from GA4. The code runs in a sandbox.
        You have access to: pandas, json, math, datetime, statistics modules.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute. Use print() to output results."
                },
                "reason": {
                    "type": "string",
                    "description": "Brief explanation of why you need to run this code."
                }
            },
            "required": ["code", "reason"]
        }
    },
    {
        "name": "export_to_pdf",
        "description": """Export the analysis results to a PDF report.
        Use this when the user asks for a report or to save/export results.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the PDF report"
                },
                "content": {
                    "type": "string",
                    "description": "Full text content of the report including all findings"
                }
            },
            "required": ["title", "content"]
        }
    }
]