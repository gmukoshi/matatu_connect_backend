def send_email(to_email, subject, content):
    """
    MOCK EMAIL SERVICE (Demo Mode)
    Instead of sending real emails, this logs them to the console.
    """
    print(f"\n[MOCK EMAIL SENT] -----------------------------")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {content}")
    print(f"-----------------------------------------------\n")
    return True
