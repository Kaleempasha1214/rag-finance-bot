import re, glob, json, warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def html_to_text(path):
    html = open(path, encoding="utf-8", errors="ignore").read()
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" "))

def chunk(text, size=400, overlap=50):
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i+size]) for i in range(0, len(words), step)]

chunks = []
pattern = "data/sec-edgar-filings/*/10-K/*/primary-document.html"
files = glob.glob(pattern)
print("Filings found:", len(files))

for path in files:
    parts = path.replace("\\", "/").split("/")
    ticker, accession = parts[-4], parts[-2]
    year = "20" + accession.split("-")[1]
    for i, c in enumerate(chunk(html_to_text(path))):
        chunks.append({"ticker": ticker, "year": year,
                       "chunk_id": i, "text": c})
    print("Done:", ticker, year)

json.dump(chunks, open("chunks.json", "w"))
print("Total chunks:", len(chunks))