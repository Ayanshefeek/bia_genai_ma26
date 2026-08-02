import pandas as pd, random, smtplib, os
from email.message import EmailMessage

BUDGET_LIMIT = 50.0  # $ threshold
current_spend = round(random.uniform(30, 70), 2)

# --- CONCEPTUAL CODE USING A FAKE API CLIENT ---
# import openai_api_client # Example: A library to talk to the LLM vendor
# from datetime import date

# def get_current_llm_spend():
#     """Fetches the actual spend from the vendor's API for the current month."""
#     
#     # 1. Define the time range (e.g., first of the month to today)
#     start_date = date.today().replace(day=1)
#     end_date = date.today()
#     
#     try:
#         # 2. Make the API call
#         response = openai_api_client.get_usage(start=start_date, end=end_date)
#         
#         # 3. Parse the response to find the total cost
#         total_cost_usd = response.get("total_cost_usd", 0.0)
#         return total_cost_usd
#         
#     except Exception as e:
#         print(f"Error fetching API spend: {e}")
#         return 0.0

# current_spend = get_current_llm_spend()

def send_alert(current):
    msg = EmailMessage()
    msg["Subject"] = "⚠️ Budget Alert – AgentOps"
    msg["From"] = "ai-monitor@example.com"
    msg["To"] = "admin@example.com"
    msg.set_content(f"Monthly usage exceeded: ${current:.2f}")
    print("Simulated alert email:")
    print(msg)

if current_spend > BUDGET_LIMIT:
    send_alert(current_spend)
else:
    print(f"✅ Within budget (${current_spend:.2f})")

# Log spend
pd.DataFrame([{"spend": current_spend}]).to_csv("budget_log.csv", index=False)
