# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
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


import cyclone.locale
import cyclone.web

from pbserver import views
from pbserver import config
from pbserver.utils import DatabaseMixin


class Application(cyclone.web.Application):
    def __init__(self, config_file):
        handlers = [(r"/(.*)", views.IndexHandler)]
        settings = config.parse_config(config_file)

        # Set up database connections
        DatabaseMixin.setup(settings)

        #settings["login_url"] = "/auth/login"
        #settings["autoescape"] = None
        cyclone.web.Application.__init__(self, handlers, **settings)
