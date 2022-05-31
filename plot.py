from datetime import datetime
from typing import Iterator

import pygal

from utils import generate_diff


def generate_timeline(timeslots: Iterator[datetime.date]):
    dashboard_diff = generate_diff("dashboard", timeslots)
    devops_diff = generate_diff("devops", timeslots)
    cobro_diff = generate_diff("cobro", timeslots)

    chart = pygal.Dot(width=50 * len(timeslots), x_label_rotation=-90)
    chart.title = "Open / Closed issues difference per team"
    chart.x_labels = map(lambda d: d.strftime("%G, w%V"), timeslots)
    chart.add("devops", devops_diff)
    chart.add("cobro",  cobro_diff)
    chart.add("dashboard", dashboard_diff)
    chart.render_to_file("diff.svg")
