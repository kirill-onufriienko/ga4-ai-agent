import os
import json
from anthropic import Anthropic
from agent.tools import TOOLS
from agent.ga4_client import GA4Client
from agent.sandbox import run_safe


class GA4Agent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        self.ga4 = GA4Client(
            property_id=os.getenv("GA4_PROPERTY_ID", "213025502"),
            use_mock=True
        )

        self.model = "claude-opus-4-5"
        self.max_tokens = 4096

        self.system_prompt = """You are a professional web analytics assistant with access to Google Analytics 4 data.

Your job is to help users understand their website performance by:
1. Fetching relevant GA4 metrics using the query_ga4 tool
2. Analyzing the data and providing clear insights
3. Running Python code for advanced calculations when needed
4. Exporting results to PDF when requested

Guidelines:
- Always fetch data first before analyzing
- Choose metrics that match the user's question
- Explain numbers in plain language, not just raw data
- Point out trends, anomalies, or interesting patterns
- If the user asks about something vague, make reasonable assumptions and explain them
- Always respond in English"""

    def run(self, user_question: str) -> str:
        print(f"\nThinking...\n")

        messages = [
            {"role": "user", "content": user_question}
        ]

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                tools=TOOLS,
                messages=messages
            )

            if response.stop_reason == "end_turn":
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text
                return final_text

            elif response.stop_reason == "tool_use":
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        print(f"Calling tool: {tool_name}")
                        print(f"Parameters: {json.dumps(tool_input, ensure_ascii=False, indent=2)}\n")

                        result = self._execute_tool(tool_name, tool_input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False)
                        })

                messages.append({
                    "role": "user",
                    "content": tool_results
                })

            else:
                return f"Unexpected stop_reason: {response.stop_reason}"

    def _execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        if tool_name == "query_ga4":
            return self.ga4.query(
                metrics=tool_input["metrics"],
                start_date=tool_input["start_date"],
                end_date=tool_input["end_date"],
                dimensions=tool_input.get("dimensions")
            )

        elif tool_name == "run_python_code":
            print(f"Running code:\n{tool_input['code']}\n")
            result = run_safe(tool_input["code"])
            return result

        elif tool_name == "export_to_pdf":
            return self._export_pdf(
                title=tool_input["title"],
                content=tool_input["content"]
            )

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _export_pdf(self, title: str, content: str) -> dict:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import cm
            import datetime

            filename = f"output/reports/report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                leftMargin=2*cm,
                rightMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            styles = getSampleStyleSheet()
            story = []

            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Title"],
                fontSize=18,
                spaceAfter=20
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.5*cm))

            body_style = ParagraphStyle(
                "CustomBody",
                parent=styles["Normal"],
                fontSize=11,
                leading=16,
                spaceAfter=8
            )

            for line in content.split("\n"):
                if line.strip():
                    safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(safe_line, body_style))
                else:
                    story.append(Spacer(1, 0.3*cm))

            doc.build(story)

            return {
                "success": True,
                "filename": filename,
                "message": f"PDF successfully created: {filename}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }