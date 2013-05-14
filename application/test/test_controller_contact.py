
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details

from twisted.web import http
from twisted.trial import unittest
from twisted.internet import defer
from twisted.python.monkey import MonkeyPatcher

from mamba.utils import config
from mamba.test.test_controller import ControllerRequest

from application.lib import smtp
from application.controller.contact import Contact

config.Application('config/application.json')
assert(config.Database().loaded)
print dir(config.Application())


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


class DummyRequest(ControllerRequest):
    """
    Dummy Request object with JSON encoded data and content type
    """

    def __init__(self, postpath, params, session=None):
        ControllerRequest.__init__(self, postpath, params, session)
        self.method = 'POST'
        self.requestHeaders.addRawHeader(
            'content-type', 'application/x-www-form-urlencoded')


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

        request = DummyRequest(['/form_request/{}/{}/{}'.format(
            'anonymous', 'anon@ymous.com', 'This is the content'
        )], {})

        result = yield self.contact.render(request)
        self.assertEqual(result.code, http.OK)
        self.assertTrue(result.subject['success'])
