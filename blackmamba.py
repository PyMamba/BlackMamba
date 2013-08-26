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
from twisted.application import service

from mamba.application.app import Mamba
from mamba.web.page import Page


def MambaApplicationFactory(settings):
    # load the configuration
    application = service.MultiService()
    application.setName(settings.name)

    # register settings through Mamba Borg
    app = Mamba(settings)

    # create the root page
    root = Page(app)

    # create the site
    mamba_app_site = server.Site(root)

    return mamba_app_site, application
