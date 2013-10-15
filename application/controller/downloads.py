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

from mamba.utils import config
from mamba.core import templating
from mamba.application import route
from mamba.web.response import Ok, Found, NotFound
from mamba.application.controller import Controller

from application import controller
from application.lib import web_client


class Downloads(Controller):
    """
    Download controller from BlackMamba
    """

    name = 'Downloads'
    __route__ = 'download'
    package_type = {
        'sdist': 'source', 'bdist_wininst': 'win executable', 'bdist': 'egg'
    }
    platforms = {'sdist': 'independent', 'bdist_wininst': 'windows'}

    def __init__(self):
        """Constructor
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

        template_args['releases'] = yield self.generate_releases()
        template_args['old_releases'] = yield self.generate_old_releases()

        defer.returnValue(
            Ok(self.template.render(**template_args).encode('utf-8')))

    @route('/latest')
    @defer.inlineCallbacks
    def latest(self, request, **kwargs):
        """Start a download process for the latest mamba version
        """

        pypi_data = yield web_client.PyPIParser().retrieve_pypi_json_data()

        for release in pypi_data['urls']:
            if release['packagetype'] == 'sdist':
                defer.returnValue(Found(str(release['url'])))

        defer.returnValue(NotFound())

    @defer.inlineCallbacks
    def generate_releases(self):
        """Generate releases
        """

        releases = []
        pypi_data = yield web_client.PyPIParser().retrieve_pypi_json_data()

        for release in pypi_data['urls']:
            releases.append(self._prepare_release_data(release))

        defer.returnValue(releases)

    @defer.inlineCallbacks
    def generate_old_releases(self):
        """Generate old releases
        """

        releases = []
        for version in config.Application().old_releases:
            pypi_data = yield web_client.PyPIParser().retrieve_pypi_json_data(
                version)
            for release in pypi_data['urls']:
                releases.append(self._prepare_release_data(release))

        defer.returnValue(releases)

    def _prepare_release_data(self, release):
        """Prepare the release dictionary
        """

        return {
            'name': release['filename'],
            'md5': release['md5_digest'],
            'link': release['url'],
            'type_string': self.package_type[release['packagetype']],
            'platforms_string': self.platforms[release['packagetype']],
            'size': release['size'],
            'release_date': release['upload_time'],
            'downloads': release['downloads']
        }
