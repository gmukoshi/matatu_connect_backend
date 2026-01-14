import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app

def send_email(to_email, subject, content):
    """
    Sends an email using SendGrid.
    """
    api_key = current_app.config.get('SENDGRID_API_KEY')
    sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')

    if not api_key:
        print("WARNING: SENDGRID_API_KEY not configured. Email not sent.")
        return False

    message = Mail(
        from_email=sender_email,
        to_emails=to_email,
        subject=subject,
        html_content=content
    )
    
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"Email sent to {to_email} | Status Code: {response.status_code}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to send email to {to_email}. Error: {str(e)}")
        return False
