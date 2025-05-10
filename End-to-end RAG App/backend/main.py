from fastapi import FastAPI
from models import URLRequest, QueryRequest, QueryResponse
from fetcher import load_urls
from embed_data import embed_documents, clear_vectordb
from rag_qa import ArticleQAEngine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_methods=["*"],
    allow_headers=["*"]
)

qa = ArticleQAEngine()

@app.post('/process-urls/')
def process_urls(request: URLRequest):
    print("✅ Received URL request")
    docs = load_urls(request.urls)
    print(f"✅ Loaded {len(docs)} documents")
    embed_documents(docs)
    print("✅ Embedding completed")
    qa.set_retriever_from_local()
    print("✅ Retriever initialized")
    return {'status':'success', 'message':'Articles Processed & Embedded'}

@app.post("/ask/", response_model=QueryResponse)
def ask_question(request:QueryRequest):
    try:
        answer = qa.answer_question(request.question)
        return QueryResponse(answer=answer)
    except ValueError as e:
        # ✅ If retriever wasn't initialized, return clear error
        return QueryResponse(answer=str(e))

@app.post("/reset/")
def reset_engine():
    global qa
    clear_vectordb()  # Fully clears stored vectors and article data
    qa = ArticleQAEngine()  # Reinitialize to reflect cleared store
    return {"status": "success", "message": "Reset successful. QA engine reloaded. Please reprocess articles."}
