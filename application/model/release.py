# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. model:: Release
    :plarform: Unix, Windows
    :synopsis: This object represents a Mamba Release

.. modelauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from storm.twisted.transact import transact
from storm.locals import Int, Unicode, DateTime, Storm, ReferenceSet, Desc

from mamba.application import model
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
    @transact
    def last(self):
        """Get the last release source tarball
        """

        store = self.database.store()
        data = store.find(self.__class__).order_by(self.__class__.id).last()

        return data

    @property
    @transact
    def older(self):
        """Get older releases
        """

        store = self.database.store()
        data = store.find(self.__class__).order_by(Desc(self.__class__.id))[1:]

        return data
