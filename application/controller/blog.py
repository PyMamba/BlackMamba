# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. controller:: Blog
    :platform: Unix, Windows
    :synopsis: BlackMamba Blog Controller

.. controllerauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from twisted.internet import defer
from zope.interface import implementer

from mamba.web.response import Ok
from mamba.application import route
from mamba.core import interfaces, templating
from mamba.application.controller import Controller

from application import controller
from application.model.post import Post


@implementer(interfaces.IController)
class Blog(Controller):
    """
    Blog controller from BlackMamba
    """

    name = 'Blog'
    __route__ = 'blog'

    def __init__(self):
        """
        Put your initializarion code here
        """
        super(Blog, self).__init__()
        self.template = templating.Template(controller=self)

    @route('/')
    @defer.inlineCallbacks
    def root(self, request, **kwargs):

        controller.toggle_menu(controller.BLOG)
        template_args = controller.template_args
        posts = yield Post().get_posts()
        template_args['posts'] = posts

        defer.returnValue(
            Ok(self.template.render(**template_args).encode('utf8')))
