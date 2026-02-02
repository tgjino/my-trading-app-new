import os
import uvicorn
import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
import main 
import auth
import db_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s-%(levelname)s-%(message)s"
)
logger = logging.getLogger("TradingBot")

app = FastAPI(title="NSE Trading Bot API")

@app.on_event("startup")
def startup_event():
    db_manager.init_db()
    logger.info("Database initialized")

def get_valid_fyers():
    token = db_manager.get_token()
    if not token:
        return None
    fyers = main.get_fyers_instance(token)
    return fyers if main.check_token_validity(fyers) else None

@app.get("/")
def home():
    logger.info("Home route accessed")
    fyers = get_valid_fyers()
    if not fyers:
      return RedirectResponse(url="/login") 
    return {"status": "Online", "message":"Nifty Bot API is running"}

@app.get("/login")
def login():
    logger.info("redirecting to Fyers Login")

    return RedirectResponse( url = auth.generate_new_token_step1())

@app.get("/callback")
def callback(auth_code: str = None):
    if not auth_code:
        logger.error("No auth code in callback")
        return {"error":"Failed"}
    if auth.generate_new_token_step2(auth_code):
        logger.info("Successfully generated and saved the token")
        return RedirectResponse(url="/")
    return {"error":"Token failed"}

@app.websocket("/ws/price")
async def price_stream(websocket:WebSocket):
    await websocket.accept()
    fyers = get_valid_fyers()
    if not fyers:
        await websocket.send_json({"error":"Authentication failed"})
        await websocket.close()
        return

    try:
        while True:       
            price = main.fetch_data(fyers)
            await websocket.send_json({"nifty":price})
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

@app.get("/price")
def get_price():
    fyers = get_valid_fyers()
    if not fyers:
      return RedirectResponse(url="/login")  
    
    data = main.fetch_data(fyers)
    return {"symbol":"NIFTY 50","data":data}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
                                    #  reload=True
