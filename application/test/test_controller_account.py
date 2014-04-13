
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details

from collections import namedtuple

from twisted.web import http
from twisted.trial import unittest
from twisted.internet import defer
from mamba.core.session import Session
from twisted.python.monkey import MonkeyPatcher
from mamba.test.test_controller import ControllerRequest

from application.model import user
from application.controller.account import Account


class DummyRequest(ControllerRequest):
    """
    Dummy Request object with JSON encoded data and content type
    """

    def __init__(self, postpath, params, session=None):
        ControllerRequest.__init__(self, postpath, params, session)
        self.method = 'POST'
        self.requestHeaders.addRawHeader(
            'content-type', 'application/x-www-form-urlencoded')


def sign_in(self, email, key):

    if email == 'valid@test.com':
        return True

    return None


class ControllerAccountTest(unittest.TestCase):
    """Tests for account controller
    """

    account = Account()

    def generate_request_and_session(self, url, auth=None, uid=None):
        request = DummyRequest([url], {})
        session = Session(0, request)

        if auth is not None:
            session.is_authed = auth
        if uid is not None:
            session.uid = uid

        request.session = session

        return request

    def generate_request(self, uri, params):
        request = ControllerRequest(uri, {})
        request.method = 'POST'
        request.requestHeaders.addRawHeader('content-type', 'application/json')
        request.content.truncate()
        request.content.write(params)
        request.content.seek(0, 0)

        return request

    def setUp(self):
        self.account.render = lambda req: self.account._router.dispatch(
            self.account, req)
        monkey_patcher = MonkeyPatcher((user.User, 'sign_in', sign_in))
        monkey_patcher.patch()

    @defer.inlineCallbacks
    def test_sign_works_on_valid_credentials(self):

        request = self.generate_request(
            ['/sign_in'], params='''{
                "email": "valid@test.com",
                "key": "valid"
            }'''
        )
        session = Session(0, request)
        session.uid = '73s7b33f'
        request.session = session
        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(type(result.subject), dict)
        self.assertEqual(result.headers['content-type'], 'application/json')
        self.assertEqual(result.subject['success'], True)
        self.assertEqual(result.subject['session_id'], '73s7b33f')

    @defer.inlineCallbacks
    def test_sign_works_on_invalid_credentials(self):

        request = self.generate_request(
            ['/sign_in'], params='''{
                "email": "invalid@test.com",
                "key": "invalid"
            }'''
        )
        request.session = Session(0, request)
        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(type(result.subject), dict)
        self.assertEqual(result.headers['content-type'], 'application/json')
        self.assertEqual(result.subject['success'], False)
        self.assertEqual(result.subject['msg'], 'Invalid credentials')

    @defer.inlineCallbacks
    def test_sign_out_needs_be_authed(self):

        url = '/sign_out/{}'.format('73s7b33f')

        request = self.generate_request_and_session(url, auth=lambda: False)
        result = yield self.account.render(request)

        self.assertEqual(result.code, http.UNAUTHORIZED)
        self.assertEqual(result.subject, 'Unauthorized')

    @defer.inlineCallbacks
    def test_sign_out_fails_on_diferent_uids(self):

        url = '/sign_out/{}'.format('one')

        request = self.generate_request_and_session(
            url, auth=lambda: True, uid='two'
        )
        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(result.subject['success'], False)
        self.assertEqual(result.subject['msg'], 'Unknown uid')

    @defer.inlineCallbacks
    def test_sign_out_works_on_authed(self):

        url = '/sign_out/{}'.format('73s7b33f')

        ctuple = namedtuple('named_user', 'email')
        user_tuple = ctuple('valid@test.com')

        request = self.generate_request_and_session(
            url, auth=lambda: True, uid='73s7b33f')
        request.session.user = user_tuple
        request.session.expire = lambda: None
        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(type(result.subject), dict)
        self.assertEqual(result.headers['content-type'], 'application/json')
        self.assertEqual(result.subject['success'], True)

    @defer.inlineCallbacks
    def test_register_fails_on_no_name_and_email_given(self):

        request = DummyRequest(['/register'], {})
        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(type(result.subject), dict)
        self.assertEqual(result.headers['content-type'], 'application/json')
        self.assertFalse(result.subject['success'])
        self.assertEqual(
            result.subject['msg'],
            'Name is required\nEmail is required'
        )

    @defer.inlineCallbacks
    def test_register_fails_on_invalid_github_account(self):

        request = self.generate_request(['/register'], '''{
            "name": "Someone",
            "email": "someone@somewhere.com",
            "github_profile": "8sdgsag8"
        }''')
        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(type(result.subject), dict)
        self.assertEqual(result.headers['content-type'], 'application/json')
        self.assertFalse(result.subject['success'])
        self.assertEqual(
            result.subject['msg'],
            'Non valid GitHub account provided'
        )

    @defer.inlineCallbacks
    def test_register_fails_on_invalid_bitbucket_account(self):

        request = self.generate_request(['/register'], '''{
            "name": "Someone",
            "email": "someone@somewhere.com",
            "bitbucket_profile": "6s8adysuh"
        }''')
        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(type(result.subject), dict)
        self.assertEqual(result.headers['content-type'], 'application/json')
        self.assertFalse(result.subject['success'])
        self.assertEqual(
            result.subject['msg'],
            'Non valid BitBucket account provided'
        )

    @defer.inlineCallbacks
    def test_register_fails_on_invalid_twitter_account(self):

        request = self.generate_request(['/register'], '''{
            "name": "Someone",
            "email": "someone@somewhere.com",
            "twitter": "@8syadusadguisad89"
        }''')
        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(type(result.subject), dict)
        self.assertEqual(result.headers['content-type'], 'application/json')
        self.assertFalse(result.subject['success'])
        self.assertEqual(
            result.subject['msg'],
            'Non valid Twitter account provided'
        )

    @defer.inlineCallbacks
    def test_regsiter_works_with_valid_accounts(self):

        request = self.generate_request(['/register'], '''{
            "name": "Someone",
            "github": "DamnWidget",
            "bitbucket": "DamnWidget",
            "twitter": "@damnwidget"
        }''')
        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(type(result.subject), dict)
        self.assertEqual(result.headers['content-type'], 'application/json')
        self.assertFalse(result.subject['success'])
        self.assertEqual(result.subject['msg'], 'Email is required')

    @defer.inlineCallbacks
    def test_regsiter_works_when_provided_information_is_valid(self):

        def create(fles):

            self.assertEqual(fles.name, 'Someone')
            self.assertEqual(fles.email, 'someone@somewhere.com')

        monkey_patcher = MonkeyPatcher((user.User, 'create', create))
        monkey_patcher.patch()
        request = self.generate_request(['/register'], '''{
            "name": "Someone",
            "email": "someone@somewhere.com"
        }''')

        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(type(result.subject), dict)
        self.assertEqual(result.headers['content-type'], 'application/json')
        self.assertTrue(result.subject['success'])

    @defer.inlineCallbacks
    def test_delete_returns_unauthorized_on_not_authed(self):

        url = '/delete/b4d535102'
        request = self.generate_request_and_session(
            url, auth=lambda: False, uid='73s7b33f'
        )

        result = yield self.account.render(request)

        self.assertEqual(result.code, http.UNAUTHORIZED)
        self.assertEqual(result.subject, 'Unauthorized')

    @defer.inlineCallbacks
    def test_delete_returns_invalid_credentials_on_invalid_key(self):

        url = '/delete/key'
        request = self.generate_request_and_session(
            url, auth=lambda: True, uid='73s7b33f'
        )
        ctuple = namedtuple('named_user', 'email key')
        user_tuple = ctuple('valid@test.com', 'key2')
        request.session.user = user_tuple

        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(result.subject['success'], False)
        self.assertEqual(result.subject['msg'], 'Invalid credentials')

    @defer.inlineCallbacks
    def test_delete_works_on_valid_credentials(self):

        from hashlib import sha512

        ctuple = namedtuple('named_user', 'email key')
        user_tuple = ctuple('valid@test.com', sha512('key').hexdigest())

        def delete(fles, user):
            self.assertEqual(user.email, 'valid@test.com')
            self.assertEqual(user, user_tuple)

        monkey_patcher = MonkeyPatcher((user.User, 'delete', delete))
        monkey_patcher.patch()

        url = '/delete/key'
        request = self.generate_request_and_session(
            url, auth=lambda: True, uid='73s7b33f'
        )
        request.session.user = user_tuple
        request.session.expire = lambda: True

        result = yield self.account.render(request)

        self.assertEqual(result.code, http.OK)
        self.assertEqual(result.subject['success'], True)

    @defer.inlineCallbacks
    def test_check_services_account_twitter(self):

        response = yield self.account._check_services_account(
            '@damnwidget', 'twitter')
        self.assertEqual(response.code, 200)

    @defer.inlineCallbacks
    def test_check_services_account_github(self):

        response = yield self.account._check_services_account(
            'DamnWidget', 'github')
        self.assertEqual(response.code, 200)

    @defer.inlineCallbacks
    def test_check_services_account_bitbucket(self):

        response = yield self.account._check_services_account(
            'damnwidget', 'bitbucket')
        self.assertEqual(response.code, 200)
