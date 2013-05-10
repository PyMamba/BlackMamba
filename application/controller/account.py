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
from zope.interface import implements
from twisted.internet import defer, reactor
from twisted.web.http_headers import Headers

from mamba.web.response import Ok
from mamba.core import interfaces
from mamba.application import route
from mamba.application import controller

from application.model.user import User
from application.lib.permissions import authed
from application.lib.ssl import WebClientContextFactory


class Account(controller.Controller):
    """
    User and session related stuff
    """

    implements(interfaces.IController)
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

    @route('/sign_in/<email>/<key>', method='POST')
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

        print('Attempting to sign on to user {email}'.format(email=email))
        log.msg('Attempting to sign on to user {email}'.format(email=email))

        account = yield User().sign_in(email, sha512(key).hexdigest())
        if account is not None:
            log.msg('Found user {email}'.format(email=email))
            log.msg('Authenticating session {uuid}'.format(uuid=session.uuid))
            session.authenticate()
            session.user = account
            defer.returnValue({'success': True, 'session_id': session.uuid})
        else:
            log.msg('Account don\'t exists or invalid key!')
            defer.returnValue({'success': False, 'msg': 'Invalid credentials'})

    @route('/sign_out/<uid>', method='POST')
    @authed
    def sign_out(self, request, uid, **kwargs):
        """Just sign off an already signed in user
        """

        session = request.getSession()
        if session.uid == uid:
            log.msg('Disconnecting session {uid} for account {email}'.format(
                uid=uid, email=session.user.email
            ))

            del session.user
            session.expire()

            result = {'success': True}
        else:
            log.msg(
                'sign_out called with uid {uid} but session.uid '
                'is {session_id}'.format(uid=uid, session_id=session.uid)
            )

            result = {'success': False, 'msg': 'Unknown uid'}

        return result

    @route('/register', method='POST')
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

        errors = self._check_register_errors(kwargs)
        if len(errors) > 0:
            return {'success': False, 'msg': '\n'.join(errors)}

        user = User()
        for key, value in kwargs:
            if key == 'key':
                value = sha512(value).hexdigest()

            if hasattr(user, key):
                setattr(user, key, value)

        user.create()
        return {'success': True}

    @route('/delete/<key>', method='POST')
    @authed
    def delete(self, request, key, **kwargs):
        """Delete this account
        """

        session = request.getSession()
        if sha512(key).hexdigest == session.user.key:
            log.msg('Deleting account {email}'.format(
                mail=session.user.email)
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

    def _check_register_erros(self, **kwargs):
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

        if 'key' not in kwargs:
            kwargs['key'] = ''.join(random.choice(
                string.ascii_letters + string.digits) for x in range(12)
            )

        if len(kwargs['key']) < 8:
            errors.append('Key should contain 8 caracters at least')

        if kwargs['key'].count(kwargs['key'][0]) == len(kwargs['key']):
            errors.append(
                'Key should be a real key not {letter} just repeated'.format(
                    letter=kwargs['key'][0]
                )
            )

        if 'github_profile' in kwargs:
            # check if the given Github account really exists
            response = self._check_services_account(
                kwargs['github_profile'], 'github'
            )
            if response.code == 404:
                errors.append('Non valid GitHub account provided')

        if 'bitbucket_profile' in kwargs:
            # check if teh given BitBucket account really exists
            response = self._check_services_account(
                kwargs['bitbucket_profile'], 'bitbucket'
            )
            if response.code == 404:
                errors.append('Non valid BitBukcet account provided')

        if 'twitter' in kwargs:
            # check if the given Twitter account exists
            response = self._check_services_account(
                kwargs['twitter'], 'twitter'
            )

        return errors

    @defer.inlineCallbacks
    def _check_services_account(self, account, service):
        """Just check that GitHub or BitBucket accounts exists
        """
        services = {
            'github': 'github.com',
            'bitbucket': 'bitbucket.org',
            'twitter': 'twitter.com'
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
