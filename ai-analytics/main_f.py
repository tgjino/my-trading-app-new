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

#code from api_app.py ->

# @app.on_event("startup")
# def startup_event():
#     db_manager.init_db()
#     logger.info("Database initialized")

# @app.get("/login")
# def login():
#     logger.info("redirecting to Fyers Login")

#     return RedirectResponse( url = auth.generate_new_token_step1())

# @app.get("/callback")
# def callback(auth_code: str = None):
#     if not auth_code:
#         logger.error("No auth code in callback")
#         return {"error":"Failed"}
#     if auth.generate_new_token_step2(auth_code):
#         logger.info("Successfully generated and saved the token")
#         return RedirectResponse(url="/")
#     return {"error":"Token failed"}
#  <- code from api_app.py

### main.py -->
# import os
# import logging
# from fyers_apiv3 import fyersModel

# logger = logging.getLogger("TradingBot.Main")

# def get_fyers_instance(token):
#     client_id = os.getenv("client_id")
    
#     return fyersModel.FyersModel(
#         client_id = client_id,
#         token = token,
#         is_async = False,
#         log_path =os.getcwd()
#     )

# def check_token_validity(fyers):
#     try:
#         profile =fyers.get_profile()
#         logger.warning("Token expired or invalid")
#         return profile and profile.get('s') == 'ok'
        
#     except Exception as e :
#         logger.error(f"Validity check failed:{str(e)}")
#         return False

# def is_market_open_live(fyers, exchanage="NSE"):
#     try:
#         response = fyers.market_status()
#         if response and response.get('s') == 'ok':
#             for status in response.get('d', []):
#                 if status.get('market') == exchanage:
#                     return status.get('status') == 'OPEN', status.get('status')
#         logger.warning("Could not determine market status")
#         return False
#     except Exception as e:
#         logger.error(f"Error checking market status: {e}")
#         return False, "Error"

# def start_fyers_stream(token, on_message_callback):
#     try:
#         client_id = os.getenv("client_id")
#         access_token = f"{client_id}:{token}"

#         fyers_socket = data_ws.FyersDataSocket(
#             access_token=access_token,
#             log_path=os.getcwd(),
#             lpt_data=on_message_callback,
#             on_connect=lambda: logger.info("Connected to Fyers Stream"),
#             on_error=lambda err: logger.error(f"Stream Error: {str(err)}"),
#             on_close=lambda: logger.info("Stream Connection Closed")
#         )

#         fyers_socket.connect()
#         fyers_socket.subscribe(symbols=["NSE:NIFTY50-INDEX"], data_type="symbolData")
#         return fyers_socket
#     except Exception as e:
#         logger.error(f"Error starting Fyers stream: {str(e)}")
#         return None
        
# def fetch_data(fyers):
#     try:
#         data = {"symbols":"NSE:NIFTY50-INDEX"}
#         response = fyers.quotes(data)
        
#         # if response.get('s') == 'ok'and response.get('d'):
#         if response and response.get('s') == 'ok':
#             price = response['d'][0]['v']
            
#             # lp = price.get('lp')
#             # df = pd.DataFrame(response['data']['optionChain'])
#             return price
#         else:
#             logger.error("Error fetching data: Response status not ok")
#             # return None
#             return "N/A"
#     except Exception as e:
#         logger.error(f"Error fetching data: {str(e)}")
#         return "Error"

### <-- main.py