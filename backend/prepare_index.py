"""Build/resume the application index from current source data.
Run explicitly with --allow-api-calls; new embeddings may incur API charges.
"""
import argparse
import hashlib
import json
import chromadb
from langchain_openai import OpenAIEmbeddings
from backend.data import (PROJECT_DIR, OPENAI_API_KEY, OPENAI_BASE_URL,
                          csv_documents, filing_chunks)


def prepare():
    docs = csv_documents + filing_chunks
    ids = [hashlib.sha256(json.dumps({'text': d.page_content, 'metadata': d.metadata},
        sort_keys=True, ensure_ascii=False).encode()).hexdigest() for d in docs]
    model = 'text-embedding-3-small'
    signature = hashlib.sha256((model+'|'+'|'.join(ids)).encode()).hexdigest()[:16]
    client = chromadb.PersistentClient(path=str(PROJECT_DIR / '.app_chroma'))
    collection = client.get_or_create_collection('financial_baseline_'+signature,
        metadata={'hnsw:space': 'cosine'})
    existing = set(collection.get(include=[])['ids'])
    missing = [(identifier, doc) for identifier, doc in zip(ids, docs) if identifier not in existing]
    print(f'{len(existing)} existing records; {len(missing)} need embedding API calls.')
    embeddings = OpenAIEmbeddings(model=model, api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL, request_timeout=60, max_retries=2)
    for offset in range(0, len(missing), 128):
        batch = missing[offset:offset+128]
        vectors = embeddings.embed_documents([doc.page_content for _, doc in batch])
        collection.upsert(ids=[identifier for identifier, _ in batch],
            documents=[doc.page_content for _, doc in batch],
            metadatas=[doc.metadata for _, doc in batch], embeddings=vectors)
        print(f'Embedded {min(offset+128,len(missing))}/{len(missing)} missing records.')
    if set(collection.get(include=[])['ids']) != set(ids):
        raise RuntimeError('Application index verification failed.')
    print('Verified application index:', collection.count(), 'records')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-api-calls', action='store_true', required=True,
                        help='Allow paid embedding requests for missing records.')
    parser.parse_args()
    prepare()
