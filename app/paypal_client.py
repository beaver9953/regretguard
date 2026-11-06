"""
PayPal API Client
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

class PayPalClient:
    def __init__(self):
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
        self.base_url = os.getenv("PAYPAL_API_BASE", "https://api-m.sandbox.paypal.com")
        # This pulls the live URL from Render, or falls back to localhost for local dev
        self.app_base_url = os.getenv("APP_BASE_URL", "http://localhost:8000")
        
    def get_access_token(self):
        """Generates an OAuth 2.0 access token."""
        auth = (self.client_id, self.client_secret)
        data = {"grant_type": "client_credentials"}
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        
        response = requests.post(
            f"{self.base_url}/v1/oauth2/token", 
            headers=headers, auth=auth, data=data
        )
        response.raise_for_status()
        return response.json().get("access_token")

    def create_order(self, amount: float):
        """Creates a PayPal order in GBP."""
        token = self.get_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "GBP",
                    "value": f"{amount:.2f}"
                },
                "description": "RegretGuard Resale Item"
            }],
            "application_context": {
                # Now it dynamically uses the Render URL or localhost
                "return_url": f"{self.app_base_url}/?payment=success",
                "cancel_url": f"{self.app_base_url}/?payment=cancelled"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/v2/checkout/orders",
            headers=headers, json=payload
        )
        response.raise_for_status()
        return response.json()