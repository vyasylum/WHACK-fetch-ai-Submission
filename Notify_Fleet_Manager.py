import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model

class Notify_Fleet_Manager(Model):
    message: str

# Configuration for email notifications
SMTP_SERVER = "smtp.gmail.com"          # Use your SMTP server (e.g., Gmail's SMTP server)
SMTP_PORT = 587                          # Port for TLS
SENDER_EMAIL = "atharvvyasvalo@gmail.com"   # Your email address
SENDER_PASSWORD = "enpg gchy oxpn jfke"         # Your email password (or app-specific password)
RECIPIENT_EMAIL = "atharvyas2@gmail.com"  # Recipient's email address

# Function to send email
def send_email_alert(message):
    try:
        # Set up the MIME message
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = "Alert: Driver Drowsiness Detected"
        
        # Add message content
        body = f"Attention: {message}+ Please cancel further rides or contact the driver. "
        msg.attach(MIMEText(body, "plain"))
        
        # Connect to the server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enable TLS
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        
        print("Email alert sent successfully.")

    except Exception as e:
        print(f"Error sending email: {e}")

# Agent setup
Notify_Manager = Agent(
    name="Notify_Manager",
    port=8002,
    seed="jshdbfsjkhdbvdjkfhvb",
    endpoint=["http://localhost:8002/submit"]
)

fund_agent_if_low(Notify_Manager.wallet.address())

@Notify_Manager.on_message(model=Notify_Fleet_Manager)
async def message_handler(ctx: Context, sender: str, msg: Notify_Fleet_Manager):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    
    # Send email alert
    send_email_alert(msg.message)

if __name__ == "__main__":
    Notify_Manager.run()
