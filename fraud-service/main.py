from fastapi import FastAPI

app = FastAPI(title="PayFlow AI Fraud Service")


@app.get("/health")
def health():
    return {"status": "ok"}