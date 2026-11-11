"""
RegretGuard API
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import os
import google.generativeai as genai
from app.scoring import calculate_regret_score
from app.paypal_client import PayPalClient

app = FastAPI(title="RegretGuard API", version="1.0.0")
templates = Jinja2Templates(directory="app/templates")
paypal = PayPalClient()

if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/simulated-checkout", response_class=HTMLResponse)
async def simulated_checkout(request: Request):
    return templates.TemplateResponse(request=request, name="simulated_checkout.html")

@app.post("/webhook", status_code=status.HTTP_200_OK)
async def paypal_webhook(request: Request):
    """
    Simulates the real PayPal PAYMENT.CAPTURE.COMPLETED webhook.
    """
    payload = await request.json()
    event_type = payload.get("event_type")
    print(f"\n[WEBHOOK RECEIVED] Event Type: {event_type}")

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        # Extract data from the simulated PayPal payload
        resource = payload.get("resource", {})
        amount = float(resource.get("amount", 150.00))
        merchant = resource.get("merchant_name", "Zara")
        time_str = resource.get("time", "23:42")
        
        print(f"-> Processing: {merchant} for £{amount} at {time_str}")
        
        score_result = calculate_regret_score(
            amount=amount,
            merchant_name=merchant,
            purchase_time_str=time_str,
            historical_rate=0.72
        )
        
        print("\n--- AI REGRET SCORE CALCULATED ---")
        print(json.dumps(score_result, indent=2))
        print("----------------------------------\n")
        
        return {
            "status": "success", 
            "score_result": score_result,
            "transaction": {
                "amount": amount,
                "merchant": merchant,
                "time": time_str
            }
        }

    return {"status": "ignored"}

@app.post("/api/create-listing", status_code=status.HTTP_200_OK)
async def create_listing(request: Request):
    data = await request.json()
    item_name = data.get("item_name", "Zara Floral Summer Dress")
    price = data.get("price", 120.00)
    
    print(f"\n[API] Generating AI resale listing for: {item_name}...")
    
    prompt = f"""
    You are an AI assistant for RegretGuard. A user bought a "{item_name}" and wants to resell it.
    Write a compelling resale listing. 
    Return ONLY a valid JSON object with exactly these keys: 
    'title' (max 8 words), 'price' (a float, around {price}), and 'description' (2 sentences).
    Do not include markdown formatting like ```json.
    """
    
    listing = {}
    try:
        model = genai.GenerativeModel('gemini-3.8-flash')
        response = model.generate_content(prompt)
        listing = json.loads(response.text)
    except Exception as e:
        print(f"[API] LLM Error: {e}")
        listing = {
            "title": f"{item_name} - Excellent Condition",
            "price": price,
            "description": "Bought recently, never worn. Selling to find a better home!"
        }

    try:
        order_data = paypal.create_order(amount=float(listing["price"]))
        approval_url = "/simulated-checkout" 
    except Exception:
        approval_url = "/simulated-checkout"

    return {"status": "success", "listing": listing, "approval_url": approval_url}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)