# ----------------------------------------------------------------------
# Copyright (c) 2016 Datatonic
# ----------------------------------------------------------------------

"""
This sends an HTML email via the sendgrid email client

"""

import os
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
from inlinestyler.utils import inline_css

def send_email(html, from_email, to_email, subject, sendgrid_key=None):
    """Send html via email"""

    if sendgrid_key:
        sg = sendgrid.SendGridAPIClient(apikey=sendgrid_key)
    else:
        sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
        
    from_email = Email(from_email)
    subject = subject
    to_email = Email(to_email)

    # Inline css in html
    html = inline_css(html)

    content = Content("text/html", html)
    mail = Mail(from_email, subject, to_email, content)

    response = sg.client.mail.send.post(request_body=mail.get())
    print response.status_code
    print response.body
    print response.headers



