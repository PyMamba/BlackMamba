
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details

import json
from cStringIO import StringIO

from twisted.web import http
from twisted.trial import unittest
from twisted.internet import defer
from twisted.web.http_headers import Headers
from twisted.python.monkey import MonkeyPatcher
from twisted.web.test.test_web import DummyRequest

from mamba.utils import config

from application.lib import smtp
from application.controller.contact import Contact

config.Application('config/application.json')
assert(config.Database().loaded)


class ContactRequest(DummyRequest):
    """Contact Dummy Request
    """

    def __init__(self, postpath, params):
        DummyRequest.__init__(self, postpath, None)
        self.content = StringIO()
        self.content.write(json.dumps(params))
        self.content.seek(0, 0)
        self.requestHeaders = Headers()
        self.method = 'POST'
        self.requestHeaders.addRawHeader('content-type', 'application/json')


@defer.inlineCallbacks
def sendmail(message, subject, sender, recipients, host):
    """Just a fake sendmail
    """

    assert 'This is the content' in message
    assert subject == '[PyMamba] Contact Form Request anonymous'
    assert sender == 'contact@pymamba.com'
    assert recipients
    assert host == 'localhost'

    yield True
    defer.returnValue(True)


class ControllerContactTest(unittest.TestCase):
    """Tests for contact controller
    """

    contact = Contact()

    def setUp(self):
        self.contact.render = lambda r: self.contact._router.dispatch(
            self.contact, r)
        monkey_patcher = MonkeyPatcher((smtp, 'sendmail', sendmail))
        monkey_patcher.patch()

    @defer.inlineCallbacks
    def test_invalid_email(self):

        request = ContactRequest(['/form_request'], {
            'name': 'anonymous',
            'email': 'anon@ymous.com',
            'content': 'This is the content'
        })

        result = yield self.contact.render(request)
        self.assertEqual(result.code, http.OK)
        self.assertTrue(result.subject['success'])
