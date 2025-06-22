from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup
import re
import traceback

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/outline", response_class=PlainTextResponse)
async def get_country_outline(request: Request, country: str):
    try:
        print("=== Incoming Request ===")
        print(f"Client: {request.client.host}")
        print(f"URL: {request.url}")
        print(f"Query param: country = {country}")
        print(f"Headers: {dict(request.headers)}")
        print("========================")

        url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
        print(f"Fetching Wikipedia URL: {url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            print(f"Received Wikipedia response: status_code = {response.status_code}")
            if response.status_code != 200:
                return f"# Error\n\nCould not fetch the Wikipedia page for '{country}'."

        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.find("div", {"id": "bodyContent"})

        if not content:
            return f"# Error\n\nCould not parse the Wikipedia page for '{country}'."

        markdown_lines = ["## Contents", f"# {country.strip()}"]

        for tag in content.find_all(re.compile(r'^h[1-6]$')):
            level = int(tag.name[1])
            title = tag.get_text().strip()
            if 'id' in tag.attrs and tag['id'] in ['toc', 'References', 'External_links']:
                continue
            markdown_lines.append(f"{'#' * level} {title}")

        print(f"Extracted {len(markdown_lines) - 2} headings.")
        return "\n\n".join(markdown_lines)

    except Exception as e:
        print("!! Error occurred:")
        print(traceback.format_exc())
        return "# Error\n\nAn unexpected error occurred while processing the request."