import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app


def send_email(to_email: str, subject: str, html_content: str):
    """
    Generic email sender using SendGrid
    """
    try:
        message = Mail(
            from_email=current_app.config["MAIL_DEFAULT_SENDER"],
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )

        sg = SendGridAPIClient(
            api_key=current_app.config["SENDGRID_API_KEY"]
        )
        response = sg.send(message)

        return response.status_code

    except Exception as e:
        current_app.logger.error(f"SendGrid error: {str(e)}")
        return None


def send_welcome_email(user_email: str, user_name: str):
    """
    Sends welcome email after successful registration
    """
    subject = "Welcome to Matatu Connect 🚍"
    html_content = f"""
    <h2>Welcome, {user_name}!</h2>
    <p>Your Matatu Connect account has been created successfully.</p>
    <p>You can now book rides, track matatus in real time, and manage your trips.</p>
    <br>
    <p>Safe travels,<br><strong>Matatu Connect Team</strong></p>
    """

    return send_email(user_email, subject, html_content)
