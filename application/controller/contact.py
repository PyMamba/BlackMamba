# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. controller:: Contact
    :platform: Linux
    :synopsis: Contact Controller

.. controllerauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from zope.interface import implements

from mamba.web.response import Ok
from mamba.application import route
from mamba.core import interfaces, templating
from mamba.application.controller import Controller, ControllerProvider

from application.controller import template_args


class Contact(Controller, ControllerProvider):
    """
    Contact Controller
    """

    implements(interfaces.IController)
    name = 'Contact'
    loaded = False
    __route__ = 'contact'

    def __init__(self):
        """
        Put your initializarion code here
        """
        super(Contact, self).__init__()

        self.template = templating.Template(controller=self)

    @route('/')
    def root(self, request, **kwargs):
        template_args['menu_options'][0]['active'] = False
        template_args['menu_options'][5]['active'] = True

        return Ok(self.template.render(**template_args).encode('utf-8'))
