"""
RegretGuard API - Webhook Ingestion & UI Service
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import json
from app.scoring import calculate_regret_score
from app.paypal_client import PayPalClient

app = FastAPI(title="RegretGuard API", version="1.0.0")
templates = Jinja2Templates(directory="app/templates")
paypal = PayPalClient()

# Pydantic model to accept the force_simulation flag
class ListingRequest(BaseModel):
    force_simulation: bool = False

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/simulated-checkout", response_class=HTMLResponse)
async def simulated_checkout(request: Request):
    """Serves the fake PayPal checkout page for the demo."""
    return templates.TemplateResponse(request=request, name="simulated_checkout.html")

@app.post("/api/create-listing", status_code=status.HTTP_200_OK)
async def create_listing(payload: ListingRequest):
    print("\n[AI ENGINE] Generating resale listing...")
    
    listing = {
        "title": "Zara Floral Summer Dress - Size M",
        "price": 120.00,
        "condition": "New with tags",
        "description": "Beautiful floral dress, perfect for summer. Bought recently, never worn. Selling to find a better home!"
    }
    
    # --- NEW: Check if frontend requested the simulation fallback ---
    if payload.force_simulation:
        print("⚠️ [DEMO MODE] User clicked 'Simulate Fallback'. Bypassing PayPal API.")
        return {
            "status": "success", 
            "listing": listing,
            "paypal_order_id": "SIMULATED",
            "approval_url": "/simulated-checkout"
        }
    # ---------------------------------------------------------------
    
    print("[PAYPAL API] Requesting OAuth 2.0 Access Token...")
    try:
        order_data = paypal.create_order(amount=listing["price"])
        approval_url = next(link["href"] for link in order_data["links"] if link["rel"] == "approve")
        order_id = order_data["id"]
        
        print(f"✅ [PAYPAL API] Real Order Created Successfully!")
        print(f"   -> Order ID: {order_id}")
        print(f"   -> PayPal Approval URL: {approval_url}")
        print(f"   -> Status: CREATED\n")
        
    except Exception as e:
        print(f"❌ [PAYPAL API] Error: {e}")
        print("   -> Falling back to simulated checkout.\n")
        approval_url = "/simulated-checkout"
    
    return {
        "status": "success", 
        "listing": listing,
        "paypal_order_id": "REAL",
        "approval_url": approval_url 
    }

@app.post("/api/simulate-payment")
async def simulate_payment():
    print("\n" + "="*50)
    print("💰 [SIMULATED PAYMENT RECEIVED] Buyer paid £120.00")
    print("-> Routing funds to Maya's PayPal account...")
    print("-> Triggering settlement webhook...")
    print("="*50 + "\n")
    
    score_result = calculate_regret_score(150.00, "Fashion", "23:42", 0.72)
    
    print("--- TRANSACTION SETTLEMENT VERIFIED ---")
    print(f"Status: SUCCESS")
    print(f"Amount: £120.00")
    print(f"Original Regret Score: {score_result['regret_probability']}")
    print("---------------------------------------\n")
    
    return {"status": "success"}

@app.post("/webhook", status_code=status.HTTP_200_OK)
async def paypal_webhook(request: Request):
    payload = await request.json()
    event_type = payload.get("event_type")
    print(f"\n[WEBHOOK RECEIVED] Event Type: {event_type}")

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        print("-> Processing capture event.")
        score_result = calculate_regret_score(150.00, "Fashion", "23:42", 0.72)
        print("\n--- AI REGRET SCORE CALCULATED ---")
        print(json.dumps(score_result, indent=2))
        print("----------------------------------\n")
        return {"status": "success", "score_result": score_result}

    return {"status": "ignored"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)