import pandas as pd
import random
import smtplib
import os
from email.message import EmailMessage

# --- CONFIGURATION (Change these for real use) ---

# Define the budget limit
BUDGET_LIMIT = 50.0 # $ threshold

# Simulate fetching the current spend (in a real app, this would be an API call)
current_spend = round(random.uniform(30, 70), 2)


# --- SMTP CREDENTIALS ---
# In a real environment, DO NOT hardcode credentials.
# We fetch them from environment variables for security and flexibility.
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.example.com") # e.g., 'smtp.gmail.com'
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587)) # 587 (TLS) or 465 (SSL)
SMTP_USER = os.environ.get("SMTP_USER", "your_sender_email@example.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "your_app_password") 

# Recipients
ALERT_TO_EMAIL = "admin@example.com"
ALERT_FROM_EMAIL = SMTP_USER 


def send_alert(current):
    """
    Connects to the SMTP server and sends the budget alert email.
    
    NOTE: This requires correct SMTP_SERVER, SMTP_USER, and SMTP_PASSWORD 
    environment variables to be set.
    """
    
    # 1. Prepare the email message
    msg = EmailMessage()
    msg["Subject"] = f"⚠️ BUDGET ALERT: Usage Exceeded ${BUDGET_LIMIT:.2f}"
    msg["From"] = ALERT_FROM_EMAIL
    msg["To"] = ALERT_TO_EMAIL
    msg.set_content(
        f"The monthly usage budget has been exceeded.\n\n"
        f"Threshold: ${BUDGET_LIMIT:.2f}\n"
        f"Current Spend: ${current:.2f}\n\n"
        f"Action required: Check services immediately to prevent further overspend."
    )

    try:
        # 2. Connect to the SMTP server (using TLS for security)
        # s = smtplib.SMTP_SSL(SMTP_SERVER, 465) # Use this line if using port 465 (SSL)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # Secure the connection
            
            # 3. Log in to the server
            server.login(SMTP_USER, SMTP_PASSWORD)
            
            # 4. Send the email
            server.send_message(msg)
            
            print(f"🚨 ALERT SENT! Email successfully dispatched to {ALERT_TO_EMAIL}.")
            
    except smtplib.SMTPAuthenticationError:
        print(f"❌ ERROR: SMTP Authentication failed. Check username ({SMTP_USER}) and password/app-token.")
    except smtplib.SMTPException as e:
        print(f"❌ ERROR: Could not send email via {SMTP_SERVER}. Details: {e}")
    except Exception as e:
        print(f"❌ A general error occurred during email transmission: {e}")


# --- MAIN LOGIC EXECUTION ---

print(f"Checking budget against limit: ${BUDGET_LIMIT:.2f}")

if current_spend > BUDGET_LIMIT:
    print(f"🔥 OVER BUDGET! Current spend is ${current_spend:.2f}")
    send_alert(current_spend)
else:
    print(f"✅ Within budget (${current_spend:.2f})")

# Log spend (Always log, regardless of budget status)
try:
    log_df = pd.DataFrame([{"spend": current_spend, "timestamp": pd.Timestamp.now()}])
    log_df.to_csv("budget_log.csv", mode='a', header=not os.path.exists("budget_log.csv"), index=False)
    print("Log updated successfully in budget_log.csv.")
except Exception as e:
    print(f"Error logging data: {e}")