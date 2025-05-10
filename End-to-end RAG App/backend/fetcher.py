import requests
from typing import List
from langchain.docstore.document import Document
from bs4 import BeautifulSoup
# import mimetypes

def load_urls(urls:List[str]) -> List[Document]:
    docs = []
    for url in urls:
        try:
            response = requests.get(url)
            content_type = response.headers.get("Content-Type", "")

            if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                from pypdf import PdfReader
                from io import BytesIO

                reader = PdfReader(BytesIO(response.content))
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                docs.append(Document(page_content=text, metadata={"source": url}))

            elif "text/plain" in content_type or url.lower().endswith(".txt"):
                text = response.text
                docs.append(Document(page_content=text, metadata={"source": url}))

            else:  # Assume HTML
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text(separator=" ", strip=True)
                docs.append(Document(page_content=text, metadata={"source": url}))

        except Exception as e:
            print(f"[!] Failed to process URL: {url} - Error: {str(e)}")
    return docs
