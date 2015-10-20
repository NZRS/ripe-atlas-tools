from __future__ import print_function, absolute_import

import itertools

from ripe.atlas.cousteau import MeasurementRequest

from .base import Command as BaseCommand
from ..helpers.colours import colourise
from ..helpers.validators import ArgumentType


class Command(BaseCommand):

    NAME = "measurements"
    LIMITS = (1, 1000)

    STATUS_SPECIFIED = 0
    STATUS_SCHEDULED = 1
    STATUS_ONGOING = 2
    STATUS_STOPPED = 4
    STATUS_FORCED_STOP = 5
    STATUS_NO_SUITABLE_PROBES = 6
    STATUS_FAILED = 7
    STATUSES = {
        "scheduled": (STATUS_SPECIFIED, STATUS_SCHEDULED,),
        "ongoing": (STATUS_ONGOING,),
        "stopped": (
            STATUS_STOPPED,
            STATUS_FORCED_STOP,
            STATUS_NO_SUITABLE_PROBES,
            STATUS_FAILED,
        )
    }

    DESCRIPTION = (
        "Fetches and prints measurements fulfilling specified criteria based "
        "on given filters."
    )

    def add_arguments(self):

        self.parser.add_argument(
            "--search",
            type=str,
            help="A search string.  This could match the target or description"
        )
        self.parser.add_argument(
            "--status",
            type=str,
            choices=self.STATUSES.keys(),
            help="The measurement status"
        )
        self.parser.add_argument(
            "--af",
            type=int,
            choices=(4, 6),
            help="The address family"
        )
        self.parser.add_argument(
            "--type",
            type=str,
            choices=("ping", "traceroute", "dns", "sslcert", "ntp", "http"),
            help="The measurement type"
        )

        timing = self.parser.add_argument_group("Timing")
        for position in ("started", "stopped"):
            for chrono in ("before", "after"):
                timing.add_argument(
                    "--{}-{}".format(position, chrono),
                    type=ArgumentType.datetime,
                    help="Filter for measurements that {} {} a specific date. "
                         "The format required is YYYY-MM-DDTHH:MM:SS".format(
                             position, chrono)
                )

        self.parser.add_argument(
            "--limit",
            type=ArgumentType.integer_range(self.LIMITS[0], self.LIMITS[1]),
            default=50,
            help="The number of measurements to return.  The number must be "
                 "between {} and {}".format(self.LIMITS[0], self.LIMITS[1])
        )

    def run(self):

        filters = self._get_filters()
        measurements = MeasurementRequest(**filters)

        print(self._get_filter_display(filters))

        print("{:<8} {:10} {:<45} {:>14}\n{}".format(
            "ID", "Type", "Description", "Status", "=" * 80
        ))
        for measurement in itertools.islice(measurements, self.arguments.limit):

            destination = measurement.destination_name or \
                measurement.destination_address or \
                ""

            status_id = measurement.meta_data["status"]["id"]
            print(colourise("{:<8} {:10} {:<45} {:>14}".format(
                measurement.id,
                measurement.type.lower(),
                destination[:45],
                measurement.status
            ), self._get_colour_from_status(status_id)))

        # Print total count of found measurements
        print("{}\n{:>80}\n".format(
            "=" * 80,
            "Showing {} of {} total measurements".format(
                min(self.arguments.limit, measurements.total_count),
                measurements.total_count
            )
        ))

    @staticmethod
    def _get_filter_display(filters):

        if len(filters.keys()) == 1:  # There's always at least one internal one
            return ""

        r = colourise("\nFilters:\n", "white")
        for k, v in filters.items():
            if k == "return_objects":
                continue
            r += colourise(
                "  {}: {}\n".format(
                    k.capitalize().replace("__", " "),
                    str(v).capitalize()),
                "cyan"
            )

        return r

    def _get_filters(self):

        r = {"return_objects": True}

        if self.arguments.search:
            r["search"] = self.arguments.search
        if self.arguments.status:
            r["status__in"] = self.STATUSES[self.arguments.status]
        if self.arguments.af:
            r["af"] = self.arguments.af
        if self.arguments.type:
            r["type"] = self.arguments.type
        if self.arguments.started_before:
            r["start_time__lt"] = self.arguments.started_before
        if self.arguments.started_after:
            r["start_time__gt"] = self.arguments.started_after
        if self.arguments.stopped_before:
            r["stop_time__lt"] = self.arguments.stopped_before
        if self.arguments.stopped_after:
            r["stop_time__gt"] = self.arguments.stopped_after

        return r

    def _get_colour_from_status(self, status):
        if status in self.STATUSES["ongoing"]:
            return "green"
        if status == self.STATUS_STOPPED:
            return "yellow"
        if status in self.STATUSES["stopped"]:
            return "red"
        if status in self.STATUSES["scheduled"]:
            return "blue"
        return "white"
