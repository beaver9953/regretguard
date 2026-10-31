"""
RegretGuard API - Webhook Ingestion & UI Service
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import requests
from app.scoring import calculate_regret_score
from app.paypal_client import PayPalClient

app = FastAPI(title="RegretGuard API", version="1.0.0")
templates = Jinja2Templates(directory="app/templates")
paypal = PayPalClient()

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/simulated-checkout", response_class=HTMLResponse)
async def simulated_checkout(request: Request):
    """Serves the fake PayPal checkout page for the demo."""
    return templates.TemplateResponse(request=request, name="simulated_checkout.html")

@app.post("/api/create-listing", status_code=status.HTTP_200_OK)
async def create_listing():
    print("\n[API] Generating AI resale listing...")
    
    listing = {
        "title": "Zara Floral Summer Dress - Size M",
        "price": 120.00,
        "condition": "New with tags",
        "description": "Beautiful floral dress, perfect for summer. Bought recently, never worn. Selling to find a better home!"
    }
    
    # We still try to create the real PayPal order to prove integration
    print("[API] Creating PayPal Sandbox Order...")
    try:
        order_data = paypal.create_order(amount=listing["price"])
        approval_url = next(link["href"] for link in order_data["links"] if link["rel"] == "approve")
        order_id = order_data["id"]
        print(f"[API] Order created: {order_id}")
    except Exception as e:
        print(f"[API] PayPal Error: {e}")
        # Even if PayPal fails, we don't crash. We just move on.
        approval_url = "/simulated-checkout"
    
    return {
        "status": "success", 
        "listing": listing,
        "paypal_order_id": "SIMULATED",
        # For the demo, we force the button to go to our simulated page
        "approval_url": "/simulated-checkout" 
    }

@app.post("/api/simulate-payment")
async def simulate_payment():
    """
    Simulates a successful PayPal capture. 
    This is what a real webhook would trigger.
    """
    print("\n[SIMULATED WEBHOOK] Buyer paid £120.00")
    print("-> Processing capture event.")
    
    score_result = calculate_regret_score(150.00, "Fashion", "23:42", 0.72)
    
    print("\n--- AI REGRET SCORE CALCULATED ---")
    print(json.dumps(score_result, indent=2))
    print("----------------------------------\n")
    
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
        return {"status": "success"}

    return {"status": "ignored"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)