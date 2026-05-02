import os
import anthropic
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from dotenv import load_dotenv

load_dotenv()

def get_website_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    return text[:2000]

def save_pdf(content, company):
    print(f"Saving PDF to: {os.getcwd()}")
    filename = f"{company}_competitor_analysis.pdf"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(script_dir, f"{company}_competitor_analysis.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title = Paragraph(f"{company} Competitor Analysis", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    for line in content.split("\n"):
        clean = line.replace("**", "").replace("*", "").replace("#", "").replace("<br>", " ").replace("|", " ").replace("_", " ")
        if clean.strip():
            paragraph = Paragraph(clean, styles['Normal'])
            story.append(paragraph)
            story.append(Spacer(1, 6))
    
    doc.build(story)
    print(f"Report PDF saved as {filename}")

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


tools = [
    {
        "name": "web_search",
        "description": "Search the web for up-to-date information on a topic. Use this tool to find recent news, articles, and other relevant content.",
        "input_schema":{
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
           "required": ["query"]

        }
    },
    {
        "name": "get_website_content",
        "description": "Fetch the content of a website. Use this tool to retrieve information from a specific URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the website to fetch content from"
                }
            },
            "required": ["url"]
        }
    }]  

company = input("Enter a company to research competitors for: ")

messages = [
    {"role": "user", "content": f"""Research {company}'s top 3 competitors.
For each competitor find their products, funding, and weaknesses.
Limit yourself to 3-4 searches total then give me a summary."""}
]

max_steps = 10
step = 0

while step < max_steps:
    step += 1
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    if response.stop_reason == "end_turn":
        report = response.content[0].text
        print(report)
        save_pdf(report, company) 
        break

    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        
        tool_results = []
        seen_ids = set()  
        
        for block in response.content:
            if block.type == "tool_use" and block.id not in seen_ids:
                seen_ids.add(block.id)
                print(f"Claude is using: {block.name} → {block.input}")

                if block.name == "web_search":
                    query = block.input["query"]
                    results = list(search(query, num_results=5))
                    tool_result = "\n".join(results)

                elif block.name == "get_website_content":
                    url = block.input["url"]
                    tool_result = get_website_content(url)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": tool_result
                })

        messages.append({"role": "user", "content": tool_results})

