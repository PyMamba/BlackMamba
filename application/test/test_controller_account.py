
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details

from twisted.trial import unittest
from twisted.internet import defer
from mamba.core import GNU_LINUX
from mamba.core.session import Session
from mamba.test.test_controller import ControllerRequest

from application.model import user
from application.controller.account import Account
from application.test.test_controller_hooker import hooker

account = Account()
account.render = lambda request: account._router.dispatch(account, request)


def cleanup(test):
    test.addCleanup(
        account._styles_manager.notifier.loseConnection)
    test.addCleanup(
        account._scripts_manager.notifier.loseConnection)
    test.addCleanup(
        hooker._styles_manager.notifier.loseConnection)
    test.addCleanup(
        hooker._scripts_manager.notifier.loseConnection)


class DummyRequest(ControllerRequest):
    """
    Dummy Request object with JSON encoded data and content type
    """

    def __init__(self, postpath, params, session=None):
        ControllerRequest.__init__(self, postpath, params, session)
        self.method = 'POST'
        self.requestHeaders.addRawHeader(
            'content-type', 'application/x-www-form-urlencoded')
        self.requestHeaders.addRawHeader('content-length', '2543')


class FakeUser(object):

    def sign_in(self, email, key):
        if email == 'valid@test.com' and email == 'valid':
            return True

        return False


class ControllerAccountTest(unittest.TestCase):
    """Tests for account controller
    """

    def setUp(self):
        self.real_user = user.User
        user.User = FakeUser
        if GNU_LINUX:
            cleanup(self)

    def tearDown(self):
        user.User = self.real_user

    @defer.inlineCallbacks
    def test_sign_works_on_valid_credentials(self):

        url = '/sign_in/{}/{}'.format('valid@test.com', 'valid')
        request = DummyRequest([url], {})
        request.session = Session(0, request)
        result = yield account.render(request)
