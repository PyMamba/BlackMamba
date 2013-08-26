# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. controller:: Downloads
    :platform: Unix, Windows
    :synopsis: Download controller from BlackMamba

.. controllerauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from twisted.internet import defer
from zope.interface import implements

from mamba.web.response import Ok
from mamba.application import route
from mamba.core import interfaces, templating
from mamba.application.controller import Controller

from application import controller
from application.model.file import File
from application.model.release import Release


class Downloads(Controller):
    """
    Download controller from BlackMamba
    """

    implements(interfaces.IController)
    name = 'Downloads'
    loaded = False
    __route__ = 'download'

    def __init__(self):
        """
        Put your initialization code here
        """
        super(Downloads, self).__init__()
        self.template = templating.Template(controller=self)

    @route('/', method=['GET', 'POST'])
    @defer.inlineCallbacks
    def root(self, request, **kwargs):
        """Renders downloads main page
        """

        controller.toggle_menu(controller.DOWNLOAD)
        template_args = controller.template_args

        template_args['releases'] = yield Release().last_release_files()
        template_args['old_releases'] = yield Release().old_release_files()

        defer.returnValue(
            Ok(self.template.render(**template_args).encode('utf-8')))

    @route('/latest/<type>')
    @defer.inlineCallbacks
    def latest(self, request, type, **kwargs):
        """Start a download process for the latest mamba version
        """

        release = yield Release().last
        source = None
        for f in release:
            if f.type_string() == type:
                source = f

        source.update_downloads()

        request.setHeader('cache-control', 'public')
        request.setHeader('content-type', 'application/octet-stream')

        request.setHeader(
            'content-disposition',
            'attachment; filename={}'.format(source.name))

        with open('releases/' + source.name, 'rb') as last:
            data = last.read()

        defer.returnValue(data)

    @route('/digest/<int:file_id>')
    @defer.inlineCallbacks
    def digest(self, request, file_id, **kwargs):
        """Return back a string with the given file MD5
        """

        file = yield File().read(file_id, True)
        defer.returnValue(str(file.md5_sum) if file is not None else '')
