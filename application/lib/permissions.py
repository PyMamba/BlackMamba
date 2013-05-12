# -*- encoding: utf-8 -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. module:: permissions
    :platform: Unix, Windows
    :synopsis: The permissions system in BlackMamba is nothing sophisticated
               we just create a serie of Bit Vectors that are applied (or not)
               to any user. Then we define Bit Vector levels to what we call
               `actions` and check if a given user has the needed bitmask to
               perform the action.

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import functools

from mamba.web.response import Unauthorized

from application.lib import bitvector


READ = bitvector.BV00
COMMENT = bitvector.BV01
WRITE = bitvector.BV02
EDIT_OWN = bitvector.BV03
EDIT_OTHERS = bitvector.BV04
MODERATE = bitvector.BV05
# ..
EVERYTHING = bitvector.BV31


def can(user, action):
    """
    Returns True if the given user can do the given action, otherwise
    returns False
    """

    v = bitvector.BitVector(user.access_level)
    return v.is_set(EVERYTHING) or v.is_set(action)


def cant(user, action):
    """
    Returns True if the given user can't do the given action, otherwise
    returns False
    """

    return not can(user, action)


def authed(func):

    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        session = request.getSession()
        if session.is_authed():
            return func(self, request, *args, **kwargs)
        else:
            return Unauthorized()

    return wrapper
