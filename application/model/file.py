# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. model:: File
    :plarform: Unix, Windows
    :synopsis: This object represents a Release File

.. modelauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from twisted.internet import defer
from storm.twisted.transact import transact
from storm.locals import Int, Unicode, DateTime, Storm, Reference

from mamba.application import model

from application.lib import bitvector

# platforms
INDEPENDENT = bitvector.BV00
UNIX = bitvector.BV01
WINDOWS = bitvector.BV02
OSX = bitvector.BV03
FREEBSD = bitvector.BV04
LINUX = bitvector.BV05


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

    # references
    release_id = Int(unsigned=True)
    release = Reference(release_id, 'Release.id')

    def __init__(self):
        super(File, self).__init__()

    @defer.inlineCallbacks
    def update_downloads(self):
        """Update downloads acount number by one
        """

        copy = yield File().read(self.id)
        copy.downloads = self.downloads + 1
        copy.update()

    def type_string(self):
        """Return back the string for a given type
        """

        types = ('source', 'egg', 'win executable')
        return types[self.type]

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
