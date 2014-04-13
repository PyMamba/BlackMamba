
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details

# import urllib
# import datetime

# from twisted.trial import unittest
# from twisted.internet import defer
# from mamba.test.test_controller import ControllerRequest

# from application.controller.hooker import Hooker

# payload = """{
#     "after": "a51f799678cf740fb02aaf1f67741035445dbad4",
#     "before": "8255c15a41e7185a81600cd274eabfb9d3e4d261",
#     "commits": [
#         {
#             "added": [],
#             "author": {
#                 "email": "oscar.campos@member.fsf.org",
#                 "name": "Oscar Campos",
#                 "username": "DamnWidget"
#             },
#             "committer": {
#                 "email": "oscar.campos@member.fsf.org",
#                 "name": "Oscar Campos",
#                 "username": "DamnWidget"
#             },
#             "distinct": true,
#             "id": "a51f799678cf740fb02aaf1f67741035445dbad4",
#             "message": "release [mamba, version 0.3.5]",
#             "modified": [ "README.md" ],
#             "removed": [],
#             "timestamp": "2013-05-09T04:34:45-07:00",
#             "url": "https://github.com/DamnWidget/testing/commit/a51f799678cf740fb02aaf1f67741035445dbad4"
#         }
#     ],
#     "compare": "https://github.com/DamnWidget/testing/compare/8255c15a41e7...a51f799678cf",
#     "created": false,
#     "deleted": false,
#     "forced": false,
#     "head_commit": {
#         "added": [],
#         "author": {
#             "email": "oscar.campos@member.fsf.org",
#             "name": "Oscar Campos", "username": "DamnWidget"
#         },
#         "committer": {
#             "email": "oscar.campos@member.fsf.org",
#             "name": "Oscar Campos",
#             "username": "DamnWidget"
#         },
#         "distinct": true,
#         "id": "a51f799678cf740fb02aaf1f67741035445dbad4",
#         "message": "release [mamba, version 0.3.5]",
#         "modified": [ "README.md" ],
#         "removed": [],
#         "timestamp": "2013-05-09T04:34:45-07:00",
#         "url": "https://github.com/DamnWidget/testing/commit/a51f799678cf740fb02aaf1f67741035445dbad4"
#     },
#     "pusher": {
#         "email": "oscar.campos@member.fsf.org",
#         "name": "DamnWidget"
#     },
#     "ref": "refs/heads/master",
#     "repository": {
#         "created_at": 1368046103,
#         "description": "Just a testing repo for tests with Github API",
#         "fork": false,
#         "forks": 0,
#         "has_downloads": true,
#         "has_issues": true,
#         "has_wiki": true,
#         "id": 9945666,
#         "master_branch": "master",
#         "name":  "testing",
#         "open_issues": 0,
#         "owner": {
#             "email": "oscar.campos@member.fsf.org",
#             "name": "DamnWidget"
#         },
#         "private": true,
#         "pushed_at": 1368099285,
#         "size": 148,
#         "stargazers": 0,
#         "url": "https://github.com/DamnWidget/testing",
#         "watchers": 0
#     }
# }"""


# class DummyRequest(ControllerRequest):
#     """
#     Dummy Request object with JSON encoded data and content type
#     """

#     def __init__(self, postpath, params, session=None):
#         ControllerRequest.__init__(self, postpath, params, session)
#         self.method = 'POST'
#         self.requestHeaders.addRawHeader(
#             'content-type', 'application/x-www-form-urlencoded')
#         self.requestHeaders.addRawHeader('content-length', '2543')


# class DummyRelease(object):
#     """Dummy Release Stub
#     """

#     def __init__(self, **kwargs):
#         for k, v in kwargs.iteritems():
#             setattr(self, k, v)

#     def build_release(self, release_version):
#         self.release_version = release_version


# class DummyFile(DummyRelease):
#     """Dummy File Stub
#     """

#     def __init__(self, **kwargs):
#         super(DummyFile, self).__init__(**kwargs)

#     def build_release_files(self, release):
#         self.release = release


# class ControllerHookerTest(unittest.TestCase):
#     """Test Hooker controller
#     """

#     hooker = Hooker()

#     def setUp(self):
#         self.hooker.render = lambda r: self.hooker._router.dispatch(
#             self.hooker, r)

#     def request(self, pay=None):

#         pay = payload if pay is None else pay
#         request = DummyRequest(
#             ['/github_update/' + urllib.urlencode({'payload': pay})], {}
#         )
#         request.release = DummyRelease(release_date=datetime.datetime.now())
#         request.rfile = DummyFile()

#         return request

#     @defer.inlineCallbacks
#     def test_payload_fails_on_no_a_release_commit(self):

#         pay = payload.replace('release [mamba, version 0.3.5]', 'None')

#         result = yield self.hooker.render(self.request(pay))
#         self.assertEqual(result.code, 200)
#         self.assertEqual(result.subject, 'ignored not a release')

#     @defer.inlineCallbacks
#     def test_payload_fails_on_branch_deletion(self):

#         pay = payload.replace(
#             'a51f799678cf740fb02aaf1f67741035445dbad4',
#             '0000000000000000000000000000000000000000'
#         )

#         result = yield self.hooker.render(self.request(pay))
#         self.assertEqual(result.code, 200)
#         self.assertEqual(result.subject, 'ignored branch deletion')

#     @defer.inlineCallbacks
#     def test_payload_fails_on_not_branch_commit_tags(self):

#         pay = payload.replace('refs/heads/master', 'refs/tags/1.0')

#         result = yield self.hooker.render(self.request(pay))
#         self.assertEqual(result.code, 200)
#         self.assertEqual(result.subject, 'ignored not a branch')

#     @defer.inlineCallbacks
#     def test_payload_success_on_release_commit(self):

#         result = yield self.hooker.render(self.request())
#         self.assertEqual(result.code, 200)
#         self.assertEqual(result.subject, 'released')

#     @defer.inlineCallbacks
#     def test_hooker_return_404_nof_found_on_root(self):

#         request = DummyRequest(['/'], {})
#         result = yield self.hooker.render(request)
#         self.assertEqual(result.code, 404)
