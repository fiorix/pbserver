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


import os
import ConfigParser
from cyclone.util import ObjectDict


def xget(func, section, option, default=None):
    try:
        return func(section, option)
    except:
        return default


def parse_config(filename):
    cfg = ConfigParser.RawConfigParser()
    with open(filename) as fp:
        cfg.readfp(fp)
    fp.close()

    settings = {'raw': cfg}

    # web server settings
    settings["debug"] = xget(cfg.getboolean, "server", "debug", False)
    settings["xheaders"] = xget(cfg.getboolean, "server", "xheaders", False)
    settings["cookie_secret"] = cfg.get("server", "cookie_secret")
    settings["xsrf_cookies"] = xget(cfg.getboolean, "server", "xsrf_cookies",
                                    False)

    # get project's absolute path
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    getpath = lambda k, v: os.path.join(root, xget(cfg.get, k, v))

    # locale, template and static directories' path
    settings["locale_path"] = getpath("frontend", "locale_path")
    settings["static_path"] = getpath("frontend", "static_path")
    settings["template_path"] = getpath("frontend", "template_path")

    # sqlite support
    if xget(cfg.getboolean, "sqlite", "enabled", False):
        settings["sqlite_settings"] = ObjectDict(database=cfg.get("sqlite",
                                                                  "database"))
    else:
        settings["sqlite_settings"] = None

    # redis support
    if xget(cfg.getboolean, "redis", "enabled", False):
        settings["redis_settings"] = ObjectDict(
            host=cfg.get("redis", "host"),
            port=cfg.getint("redis", "port"),
            dbid=cfg.getint("redis", "dbid"),
            poolsize=cfg.getint("redis", "poolsize"))
    else:
        settings["redis_settings"] = None

    # mysql support
    if xget(cfg.getboolean, "mysql", "enabled", False):
        settings["mysql_settings"] = ObjectDict(
            host=cfg.get("mysql", "host"),
            port=cfg.getint("mysql", "port"),
            username=xget(cfg.get, "mysql", "username"),
            password=xget(cfg.get, "mysql", "password"),
            database=xget(cfg.get, "mysql", "database"),
            poolsize=xget(cfg.getint, "mysql", "poolsize", 10),
            debug=xget(cfg.getboolean, "mysql", "debug", False))
    else:
        settings["mysql_settings"] = None

    # limits
    settings["limits"] = ObjectDict(
        throttle_interval=cfg.getint("limits", "throttle_interval"),
        throttle_get=cfg.getint("limits", "throttle_get"),
        throttle_post=cfg.getint("limits", "throttle_post"),
        pbsize=cfg.getint("limits", "max_pbsize_bytes"),
        pbexpire=cfg.getint("limits", "pb_expire_seconds"))

    return settings
