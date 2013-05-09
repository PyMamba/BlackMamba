# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. controller:: Hooker
    :platform: Unix, Windows
    :synopsis: Get hooks from different services and take actions

.. controllerauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import json
import urlparse

from twisted.python import log
from zope.interface import implements

from mamba.web.response import Ok
from mamba.core import interfaces
from mamba.application import route
from mamba.application import controller

from application.model.file import File
from application.model.release import Release


class Hooker(controller.Controller):
    """
    Get hooks from different services and take actions
    """

    implements(interfaces.IController)
    name = 'Hooker'
    loaded = False
    __route__ = 'hooker'

    def __init__(self):
        """
        Put your initializarion code here
        """
        super(Hooker, self).__init__()

    @route('/')
    def root(self, request, **kwargs):
        return Ok('I am the Hooker, hello world!')

    @route('/github_update/<payload>', method='POST')
    def github_update(self, request, payload, **kwargs):
        """Process an update from GitHub
        """

        payload = json.loads(dict(urlparse.parse_qsl(payload))['payload'])
        log.msg('Received github hook payload: {}'.format(payload))

        commit = payload['after']
        refname = payload['ref']
        release = request.release if hasattr(request, 'release') else Release()
        rfile = request.rfile if hasattr(request, 'rfile') else File()
        retval = 'ignored'

        if commit == '0000000000000000000000000000000000000000':
            log.msg('Branch deletion, this is not a release, ignoring')
            retval += ' branch deletion'
        elif not 'refs/heads/' in refname:
            log.msg('Ignoring refname {}: Not a branch'.format(refname))
            retval += ' not a branch'
        elif len(payload['commits']) > 1:
            log.msg('Ignoring, not a release commit')
            retval += ' not a release'
        elif ('release [mamba, version'
                not in payload['head_commit']['message']):
            log.msg('Ignoring, not a release commit')
            retval += ' not a release'
        else:
            retval = 'released'
            version = payload['head_commit']['message']
            release_version = version.rsplit(' ', 1)[1].rstrip(']')
            log.msg('New Release {}, updating database...'.format(
                release_version
            ))

            release.build_release(release_version)
            rfile.build_release_files(release)

        return Ok(retval)
