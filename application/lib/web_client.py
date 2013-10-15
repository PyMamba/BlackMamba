# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details

"""
Web Client stuff for BlackMamba
"""

import time
import hashlib
from collections import defaultdict
try:
    import ujson as json
except ImportError:
    import json

from mamba.utils import borg
from twisted.python import log
from twisted.internet import protocol
from twisted.internet import reactor, defer
from twisted.web.http_headers import Headers
from twisted.web.client import Agent, readBody

from application.lib.ssl import WebClientContextFactory


class DownloaderProtocol(protocol.Protocol):
    """Just donwload binary data
    """

    def __init__(self, filename, callback):
        self.file = open(filename, 'wb')
        self.callback = callback
        self.md5 = hashlib.md5()
        self.sha1 = hashlib.sha1()

    def dataReceived(self, data):
        """This method is called when we receive some data
        """
        self.file.write(bytes(data))
        self.md5.update(bytes(data))
        self.sha1.update(bytes(data))

    def connectionLost(self, reason):
        """Called on connection lost
        """
        self.file.close()
        self.callback.callback((self.md5, self.sha1))


class PyPIParser(borg.Borg):
    """Parse PyPI json file each hour
    """

    def __init__(self):
        if not hasattr(self, 'pypi_data'):
            self.pypi_data = defaultdict(lambda: {'last_check': None})

    @defer.inlineCallbacks
    def retrieve_pypi_json_data(self, version='latest'):
        """Retrieve the remote PyPI json structure
        """

        hour = 3600
        if (self.pypi_data[version]['last_check'] is None
                or time.time() - self.pypi_data[version]['last_check'] > hour):
            self.pypi_data[version] = yield self.make_request(version)
            self.pypi_data[version]['last_check'] = time.time()

        defer.returnValue(self.pypi_data[version])

    @defer.inlineCallbacks
    def make_request(self, version):
        """Make the request to PyPI and return back the data
        """

        data = {}
        context_factory = WebClientContextFactory()
        agent = Agent(reactor, context_factory)
        url = 'https://pypi.python.org/pypi/mamba-framework/{}json'.format(
            '' if version == 'latest' else '{}/'.format(version))
        pypi_response = yield agent.request(
            'GET', url, Headers({'User-Agent': ['Mamba PyPI Inspector']}), None
        )
        if pypi_response.code != 200:
            log.msg(pypi_response)
        else:
            data = yield readBody(pypi_response)

        defer.returnValue(json.loads(data))
