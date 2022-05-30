#!/usr/bin/env python3

import argparse
import datetime
import logging

from plot import generate_timeline
from utils import generate_timeslots, get_closest_thursday


def get_args():
    parser = argparse.ArgumentParser("Github analytics")
    parser.add_argument(
        "--since",
        type=datetime.date.fromisoformat,
        default="2022-01-01",
        help="Analyze issues since provided date, Thursday to Thursday to match pitwall"
    )
    parser.add_argument(
        "--every",
        type=int,
        default=1,
        help="Group issues by provided amount of weeks"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print verbose logs"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()

    if args.verbose:
        logging.basicConfig(format='%(message)s', level="INFO")
    else:
        logging.basicConfig(format='%(message)s')

    timeslots = generate_timeslots(get_closest_thursday(args.since))
    generate_timeline(timeslots)
