# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. model:: File
    :plarform: Unix, Windows
    :synopsis: This object represents a Release File

.. modelauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from twisted.python import log
from twisted.web.client import Agent
from twisted.internet import reactor, defer
from twisted.web.http_headers import Headers
from storm.locals import Int, Unicode, DateTime, Storm, Reference
from mamba.application import model

from application.lib import bitvector
from application.lib.ssl import WebClientContextFactory
from application.lib.web_client import DownloaderProtocol

# platforms
INDEPENDENT = bitvector.BV0
UNIX = bitvector.BV1
WINDOWS = bitvector.BV2
OSX = bitvector.BV3
FREEBSD = bitvector.BV4
LINUX = bitvector.BV5


class File(model.Model, Storm):
    """
    This object represents a Release File
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'files'

    id = Int(primary=True, unsigned=True, auto_increment=True)
    name = Unicode(size=128)
    type = Int(unsigned=True)
    platform = Int(unsigned=True, size=1)   # Bitvector
    size = Int(unsigned=True)
    release_date = DateTime()
    downloads = Int(unsigned=True)
    md5_sum = Unicode(size=32)
    sha1_sum = Unicode(size=40)

    # references
    release_id = Int(unsigned=True)
    release = Reference(release_id, 'Release.id')

    def __init__(self):
        super(File, self).__init__()

    @defer.inlineCallbacks
    def update_downloads(self):
        """Update downloads acount number by one
        """

        copy = yield File().read(self.id, True)
        copy.downloads = self.downloads + 1
        copy.update()

    def type_string(self):
        """Return back the string for a given type
        """

        types = ('source', 'egg', 'win executable')
        return types[self.type]

    def get_type_from_extension(self, ext):
        """Return back file type index using extension
        """

        index = 0
        if ext == 'egg':
            index = 1
        if ext == 'win32.exe':
            index = 2

        return index

    def platforms_string(self):
        """Return the platforms string for the file
        """

        vector = bitvector.BitVector(self.platform)

        platforms = []
        if vector.is_set(INDEPENDENT):
            platforms.append('independent')
        else:
            if vector.is_set(UNIX):
                platforms.append('unix')
            if vector.is_set(WINDOWS):
                platforms.append('windows')
            if vector.is_set(OSX):
                platforms.append('osx')
            if vector.is_set(FREEBSD):
                platforms.append('freebsd')
            if vector.is_set(LINUX):
                platforms.append('linux')

        return ', '.join(platforms)

    @defer.inlineCallbacks
    def build_release_files(self, release):
        """Build the files for the given release
        """

        context_factory = WebClientContextFactory()
        agent = Agent(reactor, context_factory)
        url = 'http://pypi.python.org/packages'
        for filetype in ['tar.bz2', 'win32.exe']:
            response = yield agent.request(
                'GET',
                '{}/source/m/mamba-framework/mamba-framework-{}.{}'.format(
                    url, release.version, filetype),
                Headers({'User-Agent': ['Mamba Release Updater']}),
                None
            )

            if response.code != 200:
                log.msg(response)
            else:
                d = defer.Deferred()
                response.deliverBody(DownloaderProtocol(
                    'releases/mamba-framework-{}.{}'.format(
                        release.version, filetype
                    )
                ), d)
                d.addCallbacks(
                    self._insert_file,
                    [release, filetype, response.length],
                    log.msg
                )

    def _insert_file(self, digests, release, filetype, length):
        """Generate a file and insert it into the database
        """

        rfile = File()
        rfile.release = release
        rfile.name = 'mamba-framework-{}.{}'.format(release.version, filetype)
        rfile.type = self.get_type_from_extension(filetype)
        rfile.platform = 4 if filetype == 'win32.exe' else 1
        rfile.size = length
        rfile.md5_sum = digests[0]
        rfile.sha1_sum = digests[1]
        rfile.release_date = release.release_date
        rfile.downloads = 0

        rfile.create()
