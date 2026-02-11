import os
import logging
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws

logger = logging.getLogger("TradingBot.Main")

def get_fyers_instance(token):
    client_id = os.getenv("client_id")
    return fyersModel.FyersModel(
        client_id = client_id,
        token = token,
        is_async = False,
        log_path =os.getcwd()
    )

def check_token_validity(fyers):
    try:
        profile =fyers.get_profile()   
        return profile and profile.get('s') == 'ok'    
    except Exception as e :
        logger.error(f"Validity check failed:{str(e)}")
        return False

def is_market_open_live(fyers, exchanage="NSE"):
    try:
        response = fyers.market_status()
        if response and response.get('s') == 'ok':
            for status in response.get('d', []):
                if status.get('market') == exchanage:
                    return status.get('status') == 'OPEN', status.get('status')
        logger.warning("Could not determine market status")
        return False, "Unknown"
    except Exception as e:
        logger.error(f"Error checking market status: {e}")
        return False, "Error"

def start_fyers_stream(token, on_message_callback, symbol="NSE:NIFTY50-INDEX"):
    try:
        client_id = os.getenv("client_id")
        access_token = f"{client_id}:{token}"

        fyers_socket = data_ws.FyersDataSocket(
            access_token=access_token,
            log_path=os.getcwd(),
            on_message=on_message_callback,
            on_connect=lambda: logger.info(f"Connected to Fyers Stream {symbol}"),
            on_error=lambda err: logger.error(f"Stream Error: {str(err)}"),
            on_close=lambda: logger.info("Stream Connection Closed")
        )

        fyers_socket.connect()
        fyers_socket.subscribe(symbols=[symbol], data_type="symbolData")
        logger.info(f"Subscription request sent for symbol: {symbol}")
        return fyers_socket
    except Exception as e:
        logger.error(f"Error starting Fyers stream: {str(e)}")
        return None

def fetch_data(fyers):
    try:
        data = {"symbols":"NSE:NIFTY50-INDEX"}
        response = fyers.quotes(data)    

        if response and response.get('s') == 'ok':
           return response['d'][0]['v']
               
        logger.error("Error fetching data: Response status not ok")
        return "N/A"

    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return "Error"