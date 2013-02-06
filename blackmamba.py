# This file is part of BlackMamba
# Copyright (c) ${year} - damnwidget <damnwidget@localhost>

"""
.. module:: BlackMamba
    :platform: Unix, Windows
    :synopsis: Black Mamba is a small and simple blog system that uses Mamba
               as backend framework

.. moduleauthor:: damnwidget <damnwidget@localhost>
"""

from twisted.web import server
from twisted.python import log
from twisted.application import service

from mamba import Mamba
from mamba.web import Page


def MambaApplicationFactory(settings):
    # load the configuration
    application = service.Application(settings.name)

    # register settings through Mamba Borg
    app = Mamba(settings)
    # we need log at routing registration so open log file
    log.startLogging(open('twistd.log', 'w+'))

    # create the root page
    root = Page(app)

    # create the site
    mamba_app_site = server.Site(root)

    return mamba_app_site, application
