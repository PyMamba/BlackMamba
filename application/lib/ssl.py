# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details

"""
Just some SSL helper classes and stuff
"""

from twisted.internet.ssl import ClientContextFactory


class WebClientContextFactory(ClientContextFactory):
    """Just a convenience class to can use Agent over SSL connections
    """

    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)
