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
from storm.twisted.transact import transact
from storm.locals import Storm, Int, Unicode, DateTime, Reference, ReferenceSet

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
    comments = ReferenceSet('Post.id', 'Comment.post_id')

    def __init__(self):
        super(Post, self).__init__()

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
            posts.append(copy)

        return posts, total_posts
