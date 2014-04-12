# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. controller:: Account
    :platform: Unix, Windows
    :synopsis: User and session related stuff

.. controllerauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import string
import random
from hashlib import sha512

from twisted.python import log
from twisted.web.client import Agent
from twisted.internet import defer, reactor
from twisted.web.http_headers import Headers

from mamba.web.response import Ok
from mamba.application import route
from mamba.application import controller
from mamba.utils.checkers import Checkers

from application.model.user import User
from application.lib.permissions import authed
from application.lib.ssl import WebClientContextFactory


class Account(controller.Controller):
    """
    User and session related stuff
    """

    name = 'Account'
    loaded = False
    __route__ = 'account'

    def __init__(self):
        """
        Put your initializarion code here
        """
        super(Account, self).__init__()

    @route('/')
    def root(self, request, **kwargs):
        return Ok('I am the Account, hello world!')

    @route('/sign_in', method='POST')
    @defer.inlineCallbacks
    def sign_in(self, request, email, key, **kwargs):
        """Sign in into user's account
        """

        session = request.getSession()

        if session.is_authed():
            defer.returnValue({
                'success': False,
                'msg': 'This session is already signed in, to sing in with '
                       'another account you must sign out first'
            })

        log.msg('Attempting to sign in to user {email}'.format(email=email))

        account = yield User().sign_in(
            unicode(email), unicode(sha512(key).hexdigest()))
        if account is not None:
            log.msg('Found user {email}'.format(email=email))
            log.msg('Authenticating session {uuid}'.format(uuid=session.uid))
            session.authenticate()
            session.user = account
            defer.returnValue({'success': True, 'session_id': session.uid})
        else:
            log.msg('Account don\'t exists or invalid key!')
            defer.returnValue({'success': False, 'msg': 'Invalid credentials'})

    @route('/sign_out/<uuid>', method='POST')
    @authed
    def sign_out(self, request, uuid, **kwargs):
        """Just sign off an already signed in user
        """

        session = request.getSession()
        if session.uid == uuid:
            log.msg('Disconnecting session {uuid} for account {email}'.format(
                uuid=uuid, email=session.user.email
            ))

            del session.user
            session.expire()

            result = {'success': True}
        else:
            log.msg(
                'sign_out called with uid {uuid} but session.uuid '
                'is {session_id}'.format(uuid=uuid, session_id=session.uid)
            )

            result = {'success': False, 'msg': 'Unknown uid'}

        return result

    @route('/register', method='POST')
    @defer.inlineCallbacks
    def register(self, request, **kwargs):
        """
        Register a new user with those params on kwargs

        :param name: the user's name
        :type name: str
        :param realname: the user's realnamee (optional)
        :type realname: str
        :param email: the user's email
        :type email: str
        :param key: the user's key (optional/autogenerated)
        :type key: str
        :param github_profile: the user's github profile (optional)
        :type github_profile: str
        :param bitbucket_profile: the user's bitbucket profile (optional)
        :type bitbucket_profile: str
        :param twitter: the user's twitter account (optional)
        :type twitter: str
        """

        errors = yield self._check_register_errors(**kwargs)
        if len(errors) > 0:
            defer.returnValue({'success': False, 'msg': '\n'.join(errors)})

        user = User()
        for key, value in kwargs.iteritems():
            if key == 'key':
                value = sha512(value).hexdigest()

            if hasattr(user, key):
                setattr(user, key, value)

        user.create()
        defer.returnValue({'success': True})

    @route('/delete/<key>', method='POST')
    @authed
    def delete(self, request, key, **kwargs):
        """Delete this account
        """

        session = request.getSession()
        if sha512(key).hexdigest() == session.user.key:
            log.msg('Deleting account {email}'.format(
                email=session.user.email)
            )

            User().delete(session.user)
            del session.user
            session.expire()

            result = {'success': True}
        else:
            log.msg('Wrong key in account deletion for account {email}'.format(
                email=session.user.email
            ))

            result = {'success': False, 'msg': 'Invalid credentials'}

        return result

    @defer.inlineCallbacks
    def _check_register_errors(self, **kwargs):
        """
        Just check common register errors

        The front-end JavaScript code is supossed to prevent any of those
        errors but we know we can't just trust JavaScript because it can
        be cheated or query can be faked
        """

        errors = []
        if 'name' not in kwargs:
            errors.append('Name is required')

        if 'email' not in kwargs:
            errors.append('Email is required')
        else:
            if not Checkers.check_email(kwargs['email']):
                errors.append('Email should be a valid email')

        if 'key' not in kwargs:
            kwargs['key'] = ''.join(random.choice(
                string.ascii_letters + string.digits) for x in range(12)
            )

        success, fails = Checkers.check_password(kwargs['key'])
        if not success:
            for error in fails:
                errors.append(error)

        if kwargs['key'].count(kwargs['key'][0]) == len(kwargs['key']):
            errors.append(
                'Key should be a real key not {letter} just repeated'.format(
                    letter=kwargs['key'][0]
                )
            )

        if 'github_profile' in kwargs:
            # check if the given Github account really exists
            response = yield self._check_services_account(
                kwargs['github_profile'], 'github'
            )
            if response.code == 404:
                errors.append('Non valid GitHub account provided')

        if 'bitbucket_profile' in kwargs:
            # check if teh given BitBucket account really exists
            response = yield self._check_services_account(
                kwargs['bitbucket_profile'], 'bitbucket'
            )
            if response.code == 404:
                errors.append('Non valid BitBucket account provided')

        if 'twitter' in kwargs:
            # check if the given Twitter account exists
            response = yield self._check_services_account(
                kwargs['twitter'], 'twitter'
            )
            if response.code == 404:
                errors.append('Non valid Twitter account provided')

        defer.returnValue(errors)

    @defer.inlineCallbacks
    def _check_services_account(self, account, service):
        """Just check that GitHub or BitBucket accounts exists
        """

        services = {
            'github': 'github.com',
            'twitter': 'twitter.com',
            'bitbucket': 'bitbucket.org'
        }

        context_factory = WebClientContextFactory()
        agent = Agent(reactor, context_factory)
        response = yield agent.request(
            'GET', 'https://{service}/{profile}'.format(
                service=services[service],
                profile=account
            ),
            Headers({'User-Agent': ['Mamba Services Checker']}),
            None
        )

        defer.returnValue(response)
