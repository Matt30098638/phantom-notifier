# email_notifications.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, RECIPIENT_GROUPS

def compose_email_content(new_releases, age_category):
    content = f"New Releases ({age_category.capitalize()}):\n\n"
    for release in new_releases:
        content += f"- {release['title']} ({release['release_date']})\n"
    return content

def send_email(content, recipients):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = "New Media Releases"
    
    msg.attach(MIMEText(content, 'plain'))
    
    # Connect to Microsoft 365 SMTP server
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(EMAIL_USER, EMAIL_PASS)  # Log in to your Microsoft 365 account
            server.sendmail(EMAIL_USER, recipients, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
