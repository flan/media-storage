"""
media-storage : mail
====================

Offers e-mail handling for important alerts.

This module is shared by every server facet of the media-storage project and
changes to one instance should be reflected in all.
 
Legal
-----

This file is part of the media-storage project.
This module is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
 
(C) Neil Tallim, 2011
"""
import logging
from email.mime.text import MIMEText
import smtplib
import time

from config import CONFIG

_logger = logging.getLogger('media_storage-mail')

def _send_message(message):
    """
    Sends the given message to the configured SMTP host.
    
    On failure, a log message is written.
    """
    try:
        _logger.info('Connecting to %(host)s:%(port)i...' % {
         'host': CONFIG.email_host,
         'port': CONFIG.email_port,
        })
        smtp = smtplib.SMTP(CONFIG.email_host, CONFIG.email_port, timeout=CONFIG.email_timeout)
        smtp.ehlo()
        if CONFIG.email_tls:
            _logger.info('Enabling TLS...')
            smtp.starttls()
            smtp.ehlo()
        if CONFIG.email_username:
            _logger.info('Authenticating...')
            smtp.login(CONFIG.email_username, CONFIG.email_password)
        _logger.info('Sending...')
        smtp.sendmail(message['From'], [message['To']], message.as_string())
        _logger.info('Sent')
    except Exception as e:
        _logger.error('Unable to send e-mail: %(error)s' % {
         'error': str(e),
        })
    finally:
        try:
            smtp.quit()
        except Exception:
            pass
            
_ALERT_COOLDOWN = 0.0
def send_alert(message):
    """
    If alerts are enabled and the alert cooldown period has elapsed, constructs and sends an alert
    e-mail to the configured recipient, using the configured SMTP server.
    """
    global _ALERT_COOLDOWN
    if not CONFIG.email_alert or time.time() < _ALERT_COOLDOWN:
        return
    _ALERT_COOLDOWN = time.time() + CONFIG.email_alert_cooldown
    _logger.warn('Sending alert e-mail...')
    
    msg = MIMEText(message)
    msg['Subject'] = CONFIG.email_alert_subject
    msg['From'] = CONFIG.email_alert_from
    msg['To'] = CONFIG.email_alert_to
    
    _send_message(msg)
    
