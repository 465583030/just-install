#!/usr/bin/env python
#
# just-install - The stupid package installer
#
# Copyright (C) 2013-2016  Lorenzo Villani
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import, division, print_function, unicode_literals

import contextlib
import glob
import json
import os
from subprocess import check_call

HERE = os.path.dirname(__file__)
TOP_LEVEL = os.path.abspath(os.path.join(HERE, ".."))

with open(os.path.join(TOP_LEVEL, ".releng.json"), "r") as f:
    VERSION = json.load(f)["version"]


def main():
    os.chdir(TOP_LEVEL)

    os.environ["JUST_INSTALL_MSI_VERSION"] = VERSION

    setup()
    clean()
    build()
    build_msi()


def setup():
    call("go", "get", "-u", "github.com/kardianos/govendor")
    call("govendor", "sync")


def clean():
    def remove(*args):
        for f in args:
            try:
                os.remove(f)
            except:
                pass

    remove("just-install")
    remove(*glob.glob("*.exe"))
    remove(*glob.glob("*.msi"))
    remove(*glob.glob("*.wixobj"))
    remove(*glob.glob("*.wixpdb"))


def build():
    with scoped_environ("GOARCH", "386"):
        call(
            "go", "build", "-o", "just-install.exe",
            "-ldflags", "-X main.version={}".format(VERSION), "./bin")


@contextlib.contextmanager
def scoped_environ(name, value):
    try:
        os.environ[name] = value
        yield
    finally:
        del os.environ[name]


def build_msi():
    call("candle", "just-install.wxs")
    call("light", "just-install.wixobj")


def call(*args):
    print("+", " ".join(args))
    check_call(args)

if __name__ == "__main__":
    main()
