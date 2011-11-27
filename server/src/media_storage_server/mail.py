import logging
from email.mime.text import MIMEText
import smtplib
import time

from config import CONFIG

_COOLDOWN_TIME = 300 #The number of seconds to wait between sending e-mails of specific types

_logger = logging.getLogger('media_server.email')

def _send_message(message, host, port, tls, username, password):
    try:
        _logger.info('Connecting to %(host)s:%(port)i...' % {
         'host': CONFIG.email_alert_host,
         'port': CONFIG.email_alert_port,
        })
        smtp = smtplib.SMTP(CONFIG.email_alert_host, CONFIG.email_alert_port)
        smtp.ehlo()
        if CONFIG.email_alert_tls:
            _logger.info('Enabling TLS...')
            smtp.starttls()
            smtp.ehlo()
        if CONFIG.email_alert_username:
            _logger.info('Authenticating...')
            smtp.login(CONFIG.email_alert_username, CONFIG.email_alert_password)
        _logger.info('Sending...')
        smtp.sendmail(message['From'], [message['To']], message.as_string())
        _logger.info('Sent')
    except Exception as e:
        _logger.error('Unable to send e-mail: %(error)s' % {
         'error': str(e),
        })
    finally:
        try:
            smtp.close()
        except Exception:
            pass
            
_ALERT_COOLDOWN = 0.0
def send_alert(message):
    global _ALERT_COOLDOWN
    if not CONFIG.email_alert or time.time() < _ALERT_COOLDOWN:
        return
    _ALERT_COOLDOWN = time.time() + _COOLDOWN_TIME
    _logger.info('Sending alert e-mail...')
    
    msg = MIMEText(message)
    msg['Subject'] = CONFIG.email_alert_subject
    msg['From'] = CONFIG.email_alert_from
    msg['To'] = CONFIG.email_alert_to
    
    _send_message(
     msg,
     CONFIG.email_alert_host, CONFIG.email_alert_port,
     CONFIG.email_alert_tls,
     CONFIG.email_alert_username, CONFIG.email_alert_password
    )
    
