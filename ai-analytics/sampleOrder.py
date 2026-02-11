from pydantic import BaseModel

# ഓർഡർ ഡാറ്റയുടെ ഘടന
class OrderRequest(BaseModel):
    symbol: str
    qty: int
    side: int  # 1 for Buy, -1 for Sell
    type: int  # 2 for Market Order

@app.post("/api/place-order")
async def place_order(order: OrderRequest):
    token = db_manager.get_token()
    if not token:
        return {"status": "error", "message": "No token found"}
    
    try:
        fyers = main.get_fyers_instance(token)
        data = {
            "symbol": order.symbol,
            "qty": order.qty,
            "type": order.type,
            "side": order.side,
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": "False"
        }
        
        response = fyers.place_order(data=data)
        logger.info(f"Order Response: {response}")
        return response
    except Exception as e:
        logger.error(f"Order Placement Failed: {str(e)}")
        return {"status": "error", "message": str(e)}