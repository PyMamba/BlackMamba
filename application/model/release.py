# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. model:: Release
    :plarform: Unix, Windows
    :synopsis: This object represents a Mamba Release

.. modelauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import datetime

from mamba.utils import config
from mamba.application import model
from storm.twisted.transact import transact

from storm.locals import Int, Unicode, DateTime, Storm, ReferenceSet, Desc

from application.model.file import File


class Release(model.Model, Storm):
    """
    This object represents a Mamba Release
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'releases'

    id = Int(primary=True, unsigned=True, auto_increment=True)
    version = Unicode(size=16)
    release_date = DateTime()

    # references
    files = ReferenceSet('Release.id', File.release_id)

    def __init_(self):
        super(Release, self).__init__()

    @property
    def last(self):
        """Get the last release files
        """

        return self.last_release_files()

    @transact
    def last_release_files(self):
        """Get the last release files
        """

        files = []
        store = self.database.store()
        release = store.find(self.__class__).order_by(self.__class__.id).last()
        if release is not None:
            for r in release.files:
                rfile = File().copy(r)
                rfile.link = '/download/latest/{}'.format(r.type_string())
                rfile.md5 = '/download/digest/{}'.format(r.id)
                files.append(rfile)

        return files

    @transact
    def old_release_files(self):
        """Get all the files from older releases
        """

        repository = config.Application().git_repository

        files = []
        store = self.database.store()
        releases = store.find(self.__class__).order_by(Desc(
            self.__class__.id))[1:]
        for r in releases:
            release = Release().copy(r)
            rel = {'release': release, 'files': []}
            if r.files.count() == 0:
                rfile = File()
                rfile.name = u'mamba-framework-{}.tar.gz'.format(
                    release.version)
                rfile.type = 0
                rfile.platform = 1
                rfile.size = 0
                rfile.link = '{}/archive/{}.tar.gz'.format(
                    repository, release.version)
                rel['files'].append(rfile)
            else:
                for rf in release.files:
                    rfile = File().copy(rf)
                    rfile.link = '/download/release/{}/{}'.format(
                        release.version, rfile.type_string()
                    )
                    rfile.md5 = '/download/digest/{}'.format(rfile.id)
                    rel['files'].append(rfile)

            files.append(rel)

        return files

    def build_release(self, version):
        """Build a new release with the given version
        """

        self.version = version
        self.release_date = datetime.datetime.now()
        self.create()
