import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from config import config
from utils import log_error, get_email_smtp_client


def send_summary_notification(recommendations):
    """Send a summary notification email with a list of new recommendations."""
    try:
        threshold = config.get("notification_threshold", 5)
        if len(recommendations) < threshold:
            print(f"New recommendations ({len(recommendations)}) do not exceed the threshold ({threshold}).")
            return  # Do not send email if recommendations are below the threshold

        # Compose the email content
        summary_content = f"Here are your new recommendations:\n\n"
        for rec in recommendations:
            summary_content += f"Title: {rec['recommended_title']} (Type: {rec['recommended_type']})\n"
        
        email_content = MIMEText(summary_content, "plain")
        
        # Prepare the email
        sender = config["email"]["sender"]
        recipient = config["email"]["recipient"]
        subject = f"New Recommendations - {len(recommendations)} New Items"
        
        # Creating the email structure
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(email_content)

        # Check if JSON attachment is needed
        if len(recommendations) > 20:
            attachment = MIMEApplication(json.dumps(recommendations, indent=2).encode("utf-8"))
            attachment.add_header("Content-Disposition", "attachment", filename="recommendations_summary.json")
            message.attach(attachment)

        # Send the email
        with get_email_smtp_client() as server:
            server.sendmail(sender, recipient, message.as_string())
        print(f"Summary email sent with {len(recommendations)} recommendations.")

    except Exception as e:
        log_error(f"Error sending summary notification: {e}")


def get_new_recommendations():
    """Stub function to retrieve new recommendations. This should interact with the database."""
    # Placeholder: Replace with actual call to retrieve recommendations from the database.
    return [
        {"recommended_title": "Movie Title 1", "recommended_type": "Movie"},
        {"recommended_title": "TV Show Title 1", "recommended_type": "TV Show"},
    ]
