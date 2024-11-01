import smtplib
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from utils import log_error, get_email_smtp_client
from config import get_email_config  # Import email configuration retrieval function

logging.basicConfig(level=logging.INFO)

def send_summary_notification(recommendations):
    """Send a summary notification email with a list of new recommendations."""
    try:
        # Retrieve email configuration
        email_config = get_email_config()
        sender = email_config["sender"]
        smtp_server = email_config["smtp_server"]
        smtp_port = email_config["smtp_port"]
        recipient_groups = email_config["recipient_groups"]
        password = email_config["password"]
        threshold = email_config.get("notification_threshold", 5)  # Default threshold if not set

        if len(recommendations) < threshold:
            logging.info(f"New recommendations ({len(recommendations)}) do not exceed the threshold ({threshold}).")
            return  # Do not send email if recommendations are below the threshold

        # Compose the email content
        summary_content = "Here are your new recommendations:\n\n"
        for rec in recommendations:
            summary_content += f"Title: {rec['recommended_title']} (Type: {rec['recommended_type']})\n"
        
        email_content = MIMEText(summary_content, "plain")

        # Prepare the email
        subject = f"New Recommendations - {len(recommendations)} New Items"
        recipients = [email for group in recipient_groups.values() for email in group]

        # Creating the email structure
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        message.attach(email_content)

        # Attach JSON file if recommendations are extensive
        if len(recommendations) > 20:
            attachment = MIMEApplication(json.dumps(recommendations, indent=2).encode("utf-8"))
            attachment.add_header("Content-Disposition", "attachment", filename="recommendations_summary.json")
            message.attach(attachment)

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipients, message.as_string())
        
        logging.info(f"Summary email sent with {len(recommendations)} recommendations.")

    except Exception as e:
        log_error(f"Error sending summary notification: {e}")

def get_new_recommendations():
    """Stub function to retrieve new recommendations. This should interact with the database."""
    # Placeholder: Replace with actual call to retrieve recommendations from the database.
    return [
        {"recommended_title": "Movie Title 1", "recommended_type": "Movie"},
        {"recommended_title": "TV Show Title 1", "recommended_type": "TV Show"},
    ]
