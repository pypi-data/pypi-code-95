# --------------------------------------------------------------------------------------
# File: "email_notifier.py"
# Dir: "SandsPythonFunctions\src\SandsPythonFunctions"
# --------------------------------------------------------------------------------------

"""
this file is meant to enable easy emailing when a script either completes or has an
error
"""


def get_email_login_info():
    """This function will prompt the user for the email password to use later
    Returns:
        string -- the sender's email address to send the email from
        string -- the sender's email address password
    """
    if "sender_email" not in globals():
        sender_email = input("Please enter your email address (from:) and press enter: ")
    if "email_password" not in globals():
        email_password = input("Please enter your email password (from:) and press enter: ")
    if "receiver_email" not in globals():
        receiver_email = input("Please enter the receiving email address and press enter: ")
    return sender_email, email_password, receiver_email


def send_email(email_subject, email_body, email_password, sender_email):
    """This function will assemble then send the email
    Arguments:
        email_subject {str} -- the subject line you want in the email sent
        email_body {str} -- the body of the message you want sent
        email_password {str} -- the password for the email account
    """
    import smtplib, ssl

    # Create a secure SSL context
    context = ssl.create_default_context()
    email_server = smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=context)
    email_server.login(sender_email, email_password)
    # who you want the email to go to
    receiver_email = "ldsands@outlook.com"
    message = f"Subject: {email_subject}\n\n{email_body}"
    email_server.sendmail(sender_email, receiver_email, message)
