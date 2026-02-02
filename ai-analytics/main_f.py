import uvicorn
from fastapi import FastAPI
from litedata import init_db, save_token,get_token



app = FastAPI()


@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
