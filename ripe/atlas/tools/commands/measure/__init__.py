# Copyright (c) 2015 RIPE NCC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, absolute_import

import sys

from ...exceptions import RipeAtlasToolsException
from ..base import Factory as BaseFactory
from .ping import PingMeasureCommand
from .traceroute import TracerouteMeasureCommand
from .dns import DnsMeasureCommand
from .sslcert import SslcertMeasureCommand
from .http import HttpMeasureCommand
from .ntp import NtpMeasureCommand


class Factory(BaseFactory):

    TYPES = {
        "ping": PingMeasureCommand,
        "traceroute": TracerouteMeasureCommand,
        "dns": DnsMeasureCommand,
        "sslcert": SslcertMeasureCommand,
        "http": HttpMeasureCommand,
        "ntp": NtpMeasureCommand,
    }

    def __init__(self):

        self.build_class = None
        if len(sys.argv) >= 2:
            self.build_class = self.TYPES.get(sys.argv[1].lower())

        if not self.build_class:
            self.raise_log()

    def raise_log(self):
        """Depending on the input raise with different log message."""
        # cases: 1) ripe-atlas measure 2) ripe-atlas measure --help/-h
        if (
            len(sys.argv) == 1 or
            (len(sys.argv) == 2 and sys.argv[1] in ("--help", "-h"))
        ):
            log = (
                "For extended options for a specific measurement type, "
                "try ripe-atlas measure <type> --help."
            )
        # cases: ripe-atlas measure bla
        else:
            log = (
                "The measurement type you requested is invalid.  "
                "Please choose one of {}."
            ).format(", ".join(self.TYPES.keys()))
        raise RipeAtlasToolsException(log)

    def create(self, *args, **kwargs):
        return self.build_class(*args, **kwargs)
