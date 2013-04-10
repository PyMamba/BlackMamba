# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. controller:: Customertest
    :platform: Unix
    :synopsis: Customer Test

.. controllerauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from twisted.internet import defer
from zope.interface import implements

from mamba.web.response import Ok
from mamba.core import interfaces
from mamba.application import route
from mamba.application.controller import Controller, ControllerProvider

from application.model.customer import Customer


class CustomerTest(Controller, ControllerProvider):
    """
    Customer Test
    """

    implements(interfaces.IController)
    name = 'CustomerTest'
    loaded = False
    __route__ = 'customer'

    def __init__(self):
        """
        Put your initializarion code here
        """
        super(CustomerTest, self).__init__()

    @route('/')
    def root(self, request, **kwargs):
        return Ok('I am the CustomerTest, hello world!')

    @route('/test')
    @defer.inlineCallbacks
    def test(self, request, **kwargs):
        c = yield Customer().read(1)
        print c
        print c.username
