# ophishal/empail.py
from ophishal.log import create_logger

def send_email():
    logger = create_logger("email:send_email")
    logger.info("Sending email")
    return 0
