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

from authomatic import Authomatic
from authomatic.adapters import MambaAdapter
from authomatic.providers import oauth2, oauth1
assert oauth1, oauth2

from mamba.utils import config
from mamba.web.response import Ok
from mamba.application import route
from mamba.web.response import Response
from mamba.core import interfaces, templating
from mamba.application.controller import Controller

from application import controller
from application.model.post import Post


def normalize_json_config():
    """Convert class_ string in JSON config to valid auth-o-matic instances
    """

    data = config.Application().blog['login']

    for service in data:
        data[service]['class_'] = eval(data[service]['class_'])


normalize_json_config()
authomatic = Authomatic(
    config.Application().blog['login'], 'mamba rocks w000t!'
)


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
            if offset <= 0:
                offset = 1
        except (ValueError, TypeError):
            offset = 1

        session = request.getSession()
        session.referer = '{}?page={}'.format(
            request.prePathURL(), kwargs.get('page', 1)
        )

        controller.toggle_menu(controller.BLOG)
        template_args = controller.template_args

        limit = config.Application().blog['posts_limit']
        posts, total = yield Post().get_posts(offset, limit)
        if offset > total:
            defer.returnValue(
                Ok(self.template.render(**template_args).encode('utf8')))

        template_args['posts'] = posts
        template_args['pagination'] = self.generate_pagination(
            offset, limit, total
        )

        defer.returnValue(
            Ok(self.template.render(**template_args).encode('utf8')))

    @route('/<int:post_id>', method='GET')
    @defer.inlineCallbacks
    def read(self, request, post_id, **kwargs):
        """Read an specific post
        """

        session = request.getSession()
        controller.toggle_menu(controller.BLOG)
        template_args = controller.template_args

        template_args['referer'] = session.__dict__.get('referer', '')
        template_args['post'] = yield Post().read(post_id)
        defer.returnValue(
            Ok(self.template.render(**template_args).encode('utf8')))

    def generate_pagination(self, offset, limit, total):
        """Generate a paginator
        """

        pagination = []
        pagination.append({
            'class': 'disabled' if offset is 1 else False,
            'number': offset - 1 if offset > 1 else 1,
            'name': 'Prev',
            'link': offset > 1
        })

        steps = total / limit if total % limit == 0 else (total / limit) + 1
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
