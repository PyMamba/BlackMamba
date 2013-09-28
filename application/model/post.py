# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. model:: Post
    :plarform: Unix, Windows
    :synopsis: BlackMamba Post Model Object

.. modelauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

# import sys
import datetime

from storm.expr import Desc
# from storm.tracer import debug
from storm.base import Storm
from storm.references import Reference
from storm.twisted.transact import transact
from storm.properties import Int, Unicode, DateTime

from mamba.application import model

from application.model.user import User

# debug(True, stream=sys.stdout)


class Post(model.Model, Storm):
    """
    BlackMamba Post Model Object
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'posts'

    id = Int(primary=True, unsigned=True, auto_increment=True)
    title = Unicode(size=256)
    image = Unicode(default=None, size=256)
    content = Unicode()
    publish_date = DateTime(default=datetime.datetime.now())
    last_update = DateTime()

    # references
    author_email = Unicode(size=128)
    author = Reference(author_email, 'User.email')

    def __init__(self):
        super(Post, self).__init__()

    @transact
    def read(self, id):
        """Override read method of mamba.model.Model
        """

        store = self.database.store()
        data = store.get(self.__class__, id)
        post = self.copy(data)
        post.author = User().copy(data.author)

        return post

    @property
    @transact
    def last(self):
        """Get the last post in the system
        """

        return self.database.store().find(self.__class__).order_by(
            self.__class__.id).last()

    @transact
    def get_posts(self, offset, limit=10):
        """Get posts starting in offset with the given limit

        :param offset: the record from where to start
        :type offset: int
        :param limit: the limit of posts to get from the database
        :type limit: int
        """

        posts = []
        result = self.database.store().find(Post).order_by(Desc(Post.id))
        total_posts = result.count()
        for post in result.config(offset=(offset - 1) * limit, limit=limit):
            copy = Post().copy(post)
            copy.author = User().copy(post.author)
            readmore = True if len(copy.content) > 450 else False
            if readmore:
                copy.content = copy.content[:len(copy.content) / 2]

            copy.readmore = readmore
            posts.append(copy)

        return posts, total_posts
