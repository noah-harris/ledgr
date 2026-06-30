from fastapi import FastAPI

# The purpose of the api will be to serve as the sole bridge to the backend

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

