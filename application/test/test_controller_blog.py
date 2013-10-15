
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details

from twisted.trial import unittest

from application.controller.blog import Blog


class ControllerBlogTest(unittest.TestCase):
    """Tests for blog controller
    """

    def test_generate_pagination(self):
        blog = Blog()
        pagination = blog.generate_pagination(1, 5, 100)
        # total / limit + Prev + Next
        self.assertEqual(len(pagination), 22)

        pagination = blog.generate_pagination(1, 50, 100)
        self.assertEqual(len(pagination), 4)

    def test_generate_pagination_work_on_negative_offset(self):
        blog = Blog()
        pagination = blog.generate_pagination(-10, 5, 100)
        self.assertEqual(len(pagination), 22)

    def test_offset(self):
        blog = Blog()
        pagination = blog.generate_pagination(9, 5, 100)
        self.assertEqual(pagination[9]['link'], False)
        self.assertEqual(pagination[9]['class'], 'active')

        pagination = blog.generate_pagination(19, 5, 100)
        self.assertEqual(pagination[19]['link'], False)
        self.assertEqual(pagination[19]['class'], 'active')
        self.assertEqual(pagination[9]['link'], True)
        self.assertEqual(pagination[9]['class'], False)

    def test_offset_does_not_overflow(self):
        blog = Blog()
        pagination = blog.generate_pagination(500, 5, 100)
        self.assertEqual(len(pagination), 22)

    def test_prev_enabled_on_second_page(self):
        blog = Blog()
        pagination = blog.generate_pagination(2, 5, 100)
        self.assertEqual(pagination[0]['class'], False)
        self.assertEqual(pagination[9]['link'], True)

    def test_next_enabled_on_first_page(self):
        blog = Blog()
        pagination = blog.generate_pagination(1, 5, 100)
        self.assertEqual(pagination[21]['class'], False)
        self.assertEqual(pagination[21]['link'], True)

    def test_prev_is_disabled_on_first_page(self):
        blog = Blog()
        pagination = blog.generate_pagination(1, 5, 100)
        self.assertEqual(pagination[0]['class'], 'disabled')

    def test_next_is_disabled_on_last_page(self):
        blog = Blog()
        pagination = blog.generate_pagination(20, 5, 100)
        self.assertEqual(pagination[21]['class'], 'disabled')
