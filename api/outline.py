from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup
import re

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/outline", response_class=PlainTextResponse)
async def get_country_outline(country: str):
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return f"# Error\n\nCould not fetch the Wikipedia page for '{country}'."

    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find("div", {"id": "bodyContent"})

    if not content:
        return f"# Error\n\nCould not parse the Wikipedia page for '{country}'."

    # Start Markdown outline
    markdown_lines = ["## Contents", f"# {country.strip()}"]

    # Extract headings (h2 to h6; Wikipedia rarely uses h1 inside bodyContent)
    for tag in content.find_all(re.compile(r'^h[1-6]$')):
        level = int(tag.name[1])
        title = tag.get_text().strip()
        # Skip headings from the table of contents or edit sections
        if 'id' in tag.attrs and tag['id'] in ['toc', 'References', 'External_links']:
            continue
        markdown_lines.append(f"{'#' * level} {title}")

    return "\n\n".join(markdown_lines)