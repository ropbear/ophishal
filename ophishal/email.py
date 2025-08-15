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
from ophishal.engagement import Engagement

def get_mime_details(attachment: bytes) -> dict:
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(attachment)
    mime_ext = mimetypes.guess_extension(mime_type)

    match mime_type:
        case "text/calendar":
            method = ""
            for line in attachment.split(b"\n"):
                field, val = line.split(b":", 1)
                if field == "METHOD":
                    method = val
            alt = f"calendar;method={method}"
        case _:
            alt = ""
    return {
        "mimetype":mime_type,
        "ext":mime_ext,
        "alttype":alt
    }


def send_email(eng: Engagement):
    logger = create_logger("email:send_email")

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

    # create body and attachment
    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)

    atch_mime = get_mime_details(eng.attachment)
    atch_name = eng.attach_params["filename"] if "filename" in eng.attach_params else "attachment"
    atch_name += atch_mime["ext"]
    attachment = MIMEBase(atch_mime["mimetype"], f' ;name="{atch_name}"')
    attachment.set_payload(eng.attachment)
    encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename="{atch_name}"')

    email_body = MIMEBase('text/plain', '')
    email_body.set_payload("")
    encode_base64(email_body)
    email_body.add_header('Content-Transfer-Encoding', "")

    msgAlternative.attach(MIMEText(eng.body, "html"))

    match atch_mime["mimetype"].split("/")[0]:
        case "application":
            msgAlternative.attach(
                MIMEApplication(eng.attachment, atch_mime["alttype"])
            )
        case "text":
            msgAlternative.attach(
                MIMEText(eng.attachment.decode('utf-8'), atch_mime["alttype"])
            )
        case "image":
            msgAlternative.attach(
                MIMEImage(eng.attachment, atch_mime["alttype"])
            )
        case "audio":
            msgAlternative.attach(
                MIMEAudio(eng.attachment, atch_mime["alttype"])
            )
        case _:
            logger.error("Unhandled mimetype: %s", atch_mime["mime"])
            

    mailServer = smtplib.SMTP(eng.server, 25)
    mailServer.ehlo()
    mailServer.ehlo()
    mailServer.sendmail(eng.sender.email, [tgt.email for tgt in eng.targets], msg.as_string())
    mailServer.close()

    logger.info("Sending email via %s", eng.server)
    return 0
