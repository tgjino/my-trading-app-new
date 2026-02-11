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
    if 'ltp' in message:
        logger.info(f"Received price update: {message.get('symbol')}")
        price_queue.put(message)

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
async def price_stream(websocket:WebSocket, symbol: str = "NSE:NIFTY50-INDEX"):
    await websocket.accept()
    token = db_manager.get_token()
 
    if not token:
        logger.error("No token found. WebSocket connection rejected.")
        await websocket.close()
        return

    try:
        fyers = main.get_fyers_instance(token)
        initial_data = fyers.quotes({"symbols": symbol})
        
        if initial_data.get('s') == 'ok':
            full_data = initial_data['d'][0]['v']
            await websocket.send_json({"symbol": symbol,"data": full_data,"type": "Initial"})
        main.start_fyers_stream(token, on_price_update, symbol)

        while True:
            if not price_queue.empty():
                price = price_queue.get()
                if price.get('symbol') == symbol:
                    await websocket.send_json({"symbol": symbol, "data": price, "status": "Price Update"})
            await asyncio.sleep(0.1)  # Stream-നു ഇടവേള നൽകുന്നു
    
    except WebSocketDisconnect:
        logger.info("User disconnected, stopping stream")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
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
