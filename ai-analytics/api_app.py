import os
import uvicorn
import asyncio
import logging
import queue
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import main 
import db_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s-%(levelname)s-%(message)s"
)
logger = logging.getLogger("TradingBot")

app = FastAPI(title="Trading Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # പ്രൊഡക്ഷനിൽ ഇത് ഫ്രണ്ട് എൻഡ് URL മാത്രം നൽകുക
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenData(BaseModel):
    access_token: str

def get_valid_fyers():
    token = db_manager.get_token()
    logger.info("New tocken is -------- saved in DB and fetched for use in API")
    if not token:
        return None
    fyers = main.get_fyers_instance(token)
    return fyers if main.check_token_validity(fyers) else None

price_queue = queue.Queue()

def on_price_update(message):
    if message.get('ltp'):
        price = message.get('ltp')
        logger.info(f"Received price update: {price}")
        price_queue.put(price)

@app.get("/")
def home():
    fyers = get_valid_fyers()
    if not fyers:
      return {"status": "Offline", "message": "Please login via .NET app"}
    return {"status": "Online", "message":"Nifty Bot API is running"}

@app.post("/process-data")
async def process_data(data: TokenData):
    try:
        db_manager.save_token(data.access_token)
        # തിരിച്ച് .NET-ലേക്ക് നൽകുന്ന മറുപടി
        return {
            "status": "Success",
            "message": "Token saved in Python DB"
        }
    except Exception as e:
        return {"statue":"Error","message":str(e)}

@app.websocket("/ws/price")
async def price_stream(websocket:WebSocket):
    await websocket.accept()
    token = db_manager.get_token()
    fyers = get_valid_fyers()
    
    if not fyers:
        await websocket.send_json({"error":"Authentication failed"})
        await websocket.close()
        return

    is_open, status = main.is_market_open_live(fyers)
    if not is_open:
        await websocket.send_json({"status": "Offline","Message": f"Market is{status}"})

    fyers_socket = main.start_fyers_stream(token, on_price_update)
    try:
        while True:   
            try:
                price = price_queue.get(timeout=1.0)
                await websocket.send_json({"nifty":price})
            except queue.Empty:
                continue
    
    except WebSocketDisconnect:
        logger.info("User disconnected, stopping stream")
    # finally:
    #     pass

# @app.get("/price")
# def get_price():
#     fyers = get_valid_fyers()
#     if not fyers:
#       return RedirectResponse(url="/login")  
    
#     data = main.fetch_data(fyers)
#     return {"symbol":"NIFTY 50","data":data}

@app.get("/test-stream")
def test_stream():
    token = db_manager.get_token()
    if not token:
        return {"error": "No token found"}
    main.start_fyers_stream(token, on_price_update)
    return {"message": "Stream start command sent. Check logs!"}



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
                                    #  reload=True
