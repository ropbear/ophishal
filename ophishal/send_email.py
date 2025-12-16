# ophishal/empail.py
import smtplib
import mimetypes
import magic
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
from email.utils import formatdate
from email.utils import formataddr

from ophishal.log import create_logger
from ophishal.engagement import EmailEngagement

def send_email(eng: EmailEngagement):
    logger = create_logger("send_email")

    # create email headers
    s = eng.sender
    sender_addr = formataddr((f"{s.name}", s.email))
    msg = MIMEMultipart('mixed')
    msg['Reply-To'] = sender_addr
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = eng.subject
    msg['From'] = sender_addr
    msg['To'] = ", ".join(
        [formataddr((tgt.name, tgt.email)) for tgt in eng.targets]
    )

    if eng.attachment is not None:
        # create body and attachment
        msgAlternative = MIMEMultipart('alternative')
        msg.attach(msgAlternative)
        atch_name = eng.attach_params['filename']
        base, alt = eng.attach_params['mime'].split('/')
        attachment = MIMEBase(base, alt)
        attachment.set_payload(eng.attachment)
        if eng.attach_params['encode']:
            encode_base64(attachment) 
        attachment.add_header("Content-Disposition", 'attachment', filename=atch_name)
        msgAlternative.attach(attachment)

    # construct email body
    email_body = MIMEBase('text', 'html')
    email_body.set_payload("")
    encode_base64(email_body)
    email_body.add_header('Content-Transfer-Encoding', "")
    if eng.attachment is not None:
        msgAlternative.attach(MIMEText(eng.body, "html"))
    else:
        msg.attach(MIMEText(eng.body, "html"))



    try:
        mailServer = smtplib.SMTP(eng.server, 25)
    except Exception as e:
        logger.error("Error connecting to mail server at %s: %s", eng.server, e)
        return 1

    print(msg)
    try:
        mailServer.ehlo()
        mailServer.ehlo()
        mailServer.sendmail(eng.sender.email, [tgt.email for tgt in eng.targets], msg.as_string())
        mailServer.close()
    except Exception as e:
        logger.error("Error sending email: %s", e)
        return 1

    logger.info("Sending email via %s", eng.server)
    return 0
