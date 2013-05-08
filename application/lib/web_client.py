# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details

"""
Web Client stuff for BlackMamba
"""

import hashlib

from twisted.internet import protocol


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
