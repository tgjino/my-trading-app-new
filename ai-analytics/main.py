import os
import logging
from fyers_apiv3 import fyersModel

logger = logging.getLogger("TradingBot.Main")

redirect_uri = os.getenv('redirect_uri')

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
        if profile and profile.get('s') == 'ok':
            return True
        logger.warning("Token expired or invalid")

    except Exception as e :
        logger.error(f"Validity check failed:{str(e)}")
        return False

def fetch_data(fyers):
    try:
        data = {"symbols":"NSE:NIFTY50-INDEX"}
        response = fyers.quotes(data)
        
        # if response.get('s') == 'ok'and response.get('d'):
        if response and response.get('s') == 'ok':
            price = response['d'][0]['v']
            
            # lp = price.get('lp')
            # df = pd.DataFrame(response['data']['optionChain'])
            return price
        else:
            logger.error("Error fetching data: Response status not ok")
            # return None
            return "N/A"
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return "Error"