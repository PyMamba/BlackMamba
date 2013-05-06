
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details

"""
Small and stupid sending mail library. This is mainly based on Twisted
Mail Sending example on Twisted Documentation.
"""

from email.mime.text import MIMEText

from twisted.python import log
from twisted.mail.smtp import sendmail as txsendmail


def sendmail(message, subject, sender, recipients, host):
    """
    Send email to one or more addresses in plain text
    """
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    d = txsendmail(host, sender, recipients, msg.as_string())

    def cb_success(ignore):
        log.msg('Email sended to {} (at least to the SMTP server)'.format(
            ', '.join(recipients))
        )
        return True

    def cb_error(error):
        log.err(error)
        return False

    d.addCallbacks(cb_success, cb_error)

    return d


__all__ = ['sendmail']
