"""Local data loading extracted from cleaned notebook cells 17 and 19.
No optimization, evaluation, data cleaning or indexing runs here.
"""
import hashlib
import json
import os
import re
import time
from pathlib import Path
from threading import Lock
import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders import CSVLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from openai import AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "Financial_Dataset" / "Financial_Dataset"
SEED = 42
load_dotenv(PROJECT_DIR / ".env", override=False)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "")
if not OPENAI_API_KEY or not OPENAI_BASE_URL:
    raise RuntimeError("Set OPENAI_API_KEY and OPENAI_BASE_URL in the project .env file.")

news_path = DATA_DIR / 'global_news_clean.csv'
prices_path = DATA_DIR / 'all_prices_clean.csv'
news_df = pd.read_csv(news_path)
prices_df = pd.read_csv(prices_path)
required_columns = {'news': {'title', 'description', 'content', 'source', 'url', 'published_at', 'query'}, 'price': {'Date', 'ticker', 'name', 'Open', 'High', 'Low', 'Close', 'Volume'}}
for label, frame in [('news', news_df), ('price', prices_df)]:
    missing = required_columns[label] - set(frame.columns)
    if missing:
        raise ValueError(f'Missing {label} columns: {sorted(missing)}')
news_docs = CSVLoader(file_path=str(news_path), encoding='utf-8-sig').load()
price_docs = CSVLoader(file_path=str(prices_path), encoding='utf-8-sig').load()
for source_type, documents, frame in [('news', news_docs, news_df), ('price', price_docs, prices_df)]:
    for document in documents:
        row_number = document.metadata['row']
        record = frame.iloc[row_number]
        document.metadata.update({'source': Path(document.metadata['source']).name, 'source_type': source_type, 'document_id': f'{source_type}_{row_number}'})
        fields = {'publisher': 'source', 'url': 'url', 'date': 'published_at'} if source_type == 'news' else {'ticker': 'ticker', 'company': 'name', 'date': 'Date'}
        for metadata_key, column in fields.items():
            value = record[column]
            document.metadata[metadata_key] = '' if pd.isna(value) else str(value)
csv_documents = news_docs + price_docs
filings_path = DATA_DIR / "sec_filings_10k.txt"
raw_filing_docs = TextLoader(str(filings_path), encoding="utf-8").load()
raw_filing_text = raw_filing_docs[0].page_content

# Use the delimiter found in the actual data, rather than splitting across reports.
filing_blocks = [block.strip() for block in
                 raw_filing_text.split("--- END OF FILING ---") if block.strip()]
filing_docs = []
for number, block in enumerate(filing_blocks, start=1):
    metadata = {
        "source": filings_path.name,
        "source_type": "filing",
        "filing_id": f"filing_{number:02d}",
        "header_excerpt": block[:100],
    }
    # Some reports begin with an explicit identifier such as aapl-20250628.
    # Preserve that identifier without guessing company names or filing dates.
    header_match = re.match(r"([a-z]+)-(\d{8})\b", block)
    if header_match:
        metadata["report_identifier"] = header_match.group(0)
    filing_docs.append(Document(page_content=block, metadata=metadata))

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
# Sizes are characters, not tokens. Overlap is a target, not an exact guarantee.
filing_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
    add_start_index=True,
)
filing_chunks = filing_splitter.split_documents(filing_docs)
for number, chunk in enumerate(filing_chunks):

    chunk.metadata["chunk_id"] = f"filing_chunk_{number:05d}"
    # start_index is measured within the stripped filing block, not the whole file.


