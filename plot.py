from datetime import datetime
from typing import Iterator

import pygal

from utils import generate_diff, milestone_progress


def generate_timeline(timeslots: Iterator[datetime.date]):
    dashboard_diff = generate_diff("dashboard", timeslots)
    devops_diff = generate_diff("devops", timeslots)
    cobro_diff = generate_diff("cobro", timeslots)

    chart = pygal.Dot(width=1600, x_label_rotation=-90)
    chart.title = "Open / Closed issues difference per team"
    chart.x_labels = map(lambda d: d.strftime("%G, w%V"), timeslots)
    chart.add("devops", devops_diff)
    chart.add("cobro",  cobro_diff)
    chart.add("dashboard", dashboard_diff)
    chart.render_to_file("diff.svg")


def generate_milestone_progress(name: str):
    progress = int(milestone_progress(name) * 100)

    chart = pygal.SolidGauge(half_pie=True, inner_radius=0.70)
    chart.title = "Roadmap progress"
    chart.value_formatter = lambda x: '{:.10g}%'.format(x)

    chart.add(name, [{"value": progress, "max_value": 100}])
    chart.render_to_file("progress.svg")
