# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. model:: User
    :plarform: Unix, Windows
    :synopsis: Users model for BlackMamba

.. modelauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from storm.twisted.transact import transact
from storm.locals import Int, Unicode, DateTime

from mamba.application import model


class User(model.Model):
    """
    Users model for BlackMamba
    """

    __storm_table__ = 'users'

    name = Unicode(size=128)
    realname = Unicode(size=256)
    email = Unicode(primary=True, size=128)
    key = Unicode(size=128)
    access_level = Int(unsigned=True)
    github_profile = Unicode(size=128)
    bitbucket_profile = Unicode(size=128)
    twitter = Unicode(size=64)
    registered = DateTime()
    last_login = DateTime()

    def __init__(self):
        super(User, self).__init__()

    @transact
    def sign_in(self, email, key):
        """Try to sign in the user

        :param email: the user's email
        :param key: the user's key
        :returns: a :class:`twisted.internet.defer.Deferred` object
        """

        store = self.database.store()
        user = store.find(User, User.email == email, User.key == key).one()
        if user is not None:
            user = User().copy(user)

        return user
