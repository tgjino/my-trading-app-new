import os
import logging
from fyers_apiv3 import fyersModel
import db_manager

logger = logging.getLogger("TradingBot.Auth")

def get_session():
    client_id = os.getenv("client_id")
    secret_key = os.getenv("secret_key")
    redirect_uri = os.getenv("redirect_uri")

    return fyersModel.SessionModel(
        client_id = client_id,
        secret_key = secret_key,
        redirect_uri = redirect_uri,
        response_type = "code",
        grant_type = "authorization_code"
    )

def generate_new_token_step1():
    session = get_session()
    auth_url = session.generate_authcode()
    logger.info("Login URL generated successfully")
    return auth_url

def generate_new_token_step2(auth_code):
    
    session = get_session()
    session.set_token(auth_code)

    try:
        response = session.generate_token()
        if response and response.get('s') == 'ok':
            access_token = response.get('access_token')
            db_manager.save_token(access_token)
            logger.info("Access Token generated and saved to database")
            return True
        
        else:
            logger.error(f"Token generation failed:{response}")
            return False
            
    except Exception as e:
        logger.error(f"Error in step 2: {str(e)}")
        return False

        