from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/test")
def test():
    return {"message": "Hello from tradesEngine backend!"}

if __name__ == "__main__": 
    uvicorn.run(app, host="0.0.0.0", port=4000)