# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. controller:: Hooker
    :platform: Unix, Windows
    :synopsis: Get hooks from different services and take actions

.. controllerauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

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

    @route('/github_update', method='POST')
    def github_update(self, request, **payload):
        """Process an update from GitHub
        """

        commit = payload['after']
        refname = payload['ref']

        if not 'refs/heads/' in refname:
            log.msg('Ignoring refname {}: Not a branch'.format(refname))
        else:
            branch = refname.rsplit('/', 1)[1]
            if commit == '0000000000000000000000000000000000000000':
                log.msg('Branch `{}` deleted, ignoring'.format(branch))
            else:
                if len(payload['commits']) > 1:
                    log.msg('Ignoring, not a release commit')
                elif ('release [mamba, version'
                        not in payload['commits'][0]['comments']):
                    log.msg('Ignoring, not a release commit')
                else:
                    version = payload['commits'][0]['comments']
                    release_version = version.rsplit(' ', 1)[1].rstrip(']')
                    log.msg('New Release {}, updating database...'.format(
                        release_version
                    ))

                    # adds release to the donwloads
                    release = Release()
                    release.build_release(release_version)

                    rfile = File()
                    rfile.build_release_files(release)

        return Ok()
