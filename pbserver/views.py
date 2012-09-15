# coding: utf-8
#
# Copyright 2012 Alexandre Fiori
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import cyclone.escape
import cyclone.locale
import cyclone.web

import random
import string
import time

from twisted.internet import defer
from twisted.python import log

from pbserver import base62
from pbserver.utils import BaseHandler
from pbserver.utils import DatabaseMixin
from pbserver.utils import TemplateFields


class IndexHandler(BaseHandler, DatabaseMixin):
    @defer.inlineCallbacks
    def get(self, n):
        self.set_header("Content-Type", "text/plain")

        # throttle
        k = "g:%s" % self.request.remote_ip
        try:
            r = yield self.redis.get(k)
            assert r < self.settings.limits.throttle_get
            yield self.redis.incr(k)
            if not r:
                yield self.redis.expire(k,
                                        self.settings.limits.throttle_interval)
        except AssertionError:
            raise cyclone.web.HTTPError(403)  # Forbidden
        except Exception, e:
            log.err("redis failed on get (throttle): %s" % e)
            raise cyclone.web.HTTPError(503)  # Service Unavailable

        if n:
            try:
                k = "n:%s" % base62.base62_decode(n)
            except:
                raise cyclone.web.HTTPError(404)

            try:
                buf = yield self.redis.get(k)
            except Exception, e:
                log.err("redis failed on get: %s" % e)
                raise cyclone.web.HTTPError(503)  # Service Unavailable
            else:
                self.finish(buf)
        else:
            if "text/html" in self.request.headers.get("Accept"):
                self.render("index.html")
            else:
                self.finish("Use: xpbpaste <pbid>\r\n")

    @defer.inlineCallbacks
    def post(self, *ign):
        self.set_header("Content-Type", "text/plain")

        k = "g:%s" % self.request.remote_ip
        blen = len(self.request.body)
        if blen > self.settings.limits.pbsize:
            raise cyclone.web.HTTPError(400,
                                        "buffer too large (%d bytes)" % blen)

        # throttle
        k = "p:%s" % self.request.remote_ip
        try:
            r = yield self.redis.get(k)
            assert r < self.settings.limits.throttle_post
            yield self.redis.incr(k)
            if not r:
                yield self.redis.expire(k,
                                        self.settings.limits.throttle_interval)
        except AssertionError:
            raise cyclone.web.HTTPError(403)  # Forbidden
        except Exception, e:
            log.err("redis failed on post (throttle): %s" % e)
            raise cyclone.web.HTTPError(503)  # Service Unavailable

        try:
            n = yield self.redis.incr("n")
            if n == 1:
                yield self.redis.expire("n",
                                self.settings.limits.pbexpire * 10)

            k = "n:%d" % n
            yield self.redis.set(k, self.request.body)
            yield self.redis.expire(k, self.settings.limits.pbexpire)
        except Exception, e:
            log.err("redis failed on post: %s" % e)
            raise cyclone.web.HTTPError(503)  # Service Unavailable
        else:
            self.finish("xpbpaste %s\r\n" % base62.base62_encode(n))
            #self.finish("%s://%s/%s\r\n" % (self.request.protocol,
            #                                self.request.host,
            #                                base62.base62_encode(n)))

    def write_error(self, status_code, **kwargs):

        if status_code == 400:
            self.finish("Bad request: %s\r\n" %
                        kwargs["exception"].log_message)

        elif status_code == 403:
            self.finish("Forbidden: reached maximum service quotas. "
                        "Try again later.\r\n")

        elif status_code == 404:
            self.finish("Not found.\r\n")

        elif status_code == 503:
            self.finish("Service temporarily unavailable. "
                        "Try again later.\r\n")

        else:
            BaseHandler.write_error(self, status_code, **kwargs)
