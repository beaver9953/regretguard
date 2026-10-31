# RegretGuard: Payment-Native AI for Post-Purchase Regret

## 💡 The Problem
E-commerce returns are a massive $890 billion problem. A huge driver of this is "sleepy shopping"—impulsive late-night purchases that users regret the moment they wake up. 

Current solutions are paternalistic: they block the purchase or lecture the user about spending. 

## 🛡️ The Solution: RegretGuard
RegretGuard is a PayPal-native AI agent that predicts post-purchase regret at the exact moment of sale and converts it into a **parallel resale transaction before the item even ships**. 

We don't block the purchase. We don't shame the user. We simply offer a profitable exit.

### The Core Loop:
1. **Signal Capture:** A PayPal `PAYMENT.CAPTURE.COMPLETED` webhook fires.
2. **AI Scoring:** The agent analyzes the transaction time, category, and user history to predict regret probability.
3. **Explainable Intervention:** The user gets a non-judgmental nudge showing *exactly why* the AI flagged the purchase.
4. **Human-in-the-Loop:** The AI drafts a resale listing (title, price, description). The user reviews and approves it.
5. **Settlement:** A buyer pays via PayPal Checkout, and funds route directly back to the original user.

---

## 🏗️ Architecture & Tech Stack
- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML, Tailwind CSS, Vanilla JS
- **AI Engine:** Custom heuristic logistic model (v0) with explainable feature contributions.
- **Integration:** PayPal REST API (OAuth 2.0, Orders v2, Webhooks)

### Why Payment-Rail Native?
RegretGuard does **not** use retailer scraping, browser extensions, or cookie tracking. It works entirely off the payment rail. This means it is privacy-preserving, universally compatible with any merchant, and incredibly fast.

---

## ⚠️ Note on PayPal Sandbox Limitations (Important for Judges)
The PayPal Developer Sandbox environment enforces strict regional compliance blocks. During testing, transactions originating from certain developer regions are declined with an `international regulations` compliance error, regardless of the currency or buyer account used. 

**To ensure the judges can evaluate the full end-to-end flow:**
1. The real PayPal OAuth 2.0 and Order Creation APIs are fully implemented in `app/paypal_client.py`.
2. The final checkout screen is **simulated** in the UI (`simulated_checkout.html`) to bypass the regional sandbox bug and demonstrate the webhook and dashboard update.
3. The AI scoring and listing generation are **100% real and functional**.

---

## 🚀 How to Run Locally (For Judges & Testers)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/regretguard.git
cd regretguard


2. Set up the virtual environment
bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
3. Install dependencies
bash
pip install -r requirements.txt
4. Set up Environment Variables
Create a .env file in the root directory and add your PayPal Sandbox credentials:

env
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_secret
PAYPAL_WEBHOOK_ID=your_webhook_id
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com
(Note: If you do not have credentials, the app will still run and use the simulated checkout).

5. Run the server
bash
uvicorn app.main:app --reload
6. View the Demo
Open your browser and navigate to:
http://localhost:8000

🧪 Testing Instructions
Click "Draft AI Listing" to see the AI generate a resale draft based on Maya's late-night shopping pattern.

Click "No Thanks" to see the non-judgmental decline flow. The UI resets automatically after 3 seconds.

Click "Draft AI Listing" again, then click "Post Listing".

Click the blue "Simulate Buyer Checkout" button.

Click "Log In" on the simulated PayPal page.

Watch the dashboard transform into the "Resale Successful" state.

📄 License
This project is licensed under the MIT License.

Built for the PayPal AI Hackathon 2026.


