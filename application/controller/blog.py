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

        try:
            offset = int(kwargs.get('page'))
        except (ValueError, TypeError):
            offset = 1

        controller.toggle_menu(controller.BLOG)
        template_args = controller.template_args
        posts, total = yield Post().get_posts(offset)
        template_args['posts'] = posts
        template_args['pagination'] = self.generate_pagination(offset, total)

        defer.returnValue(
            Ok(self.template.render(**template_args).encode('utf8')))

    def generate_pagination(self, offset, total):
        """Generate a paginator
        """

        if offset is None:
            return False

        if offset <= 0:
            offset = 1

        pagination = []
        pagination.append({
            'class': 'disabled' if offset is 1 else False,
            'number': offset - 1 if offset > 1 else 1,
            'name': 'Prev',
            'link': offset > 1
        })

        steps = total / 10 if total % 10 == 0 else (total / 10) + 1
        for step in range(1, steps + 1):
            pagination.append({
                'class': 'active' if offset == step else False,
                'number': step,
                'name': step,
                'link': offset != step
            })

        pagination.append({
            'class': 'disabled' if offset == steps else False,
            'number': offset + 1,
            'name': 'Next',
            'link': offset < steps
        })

        return pagination
