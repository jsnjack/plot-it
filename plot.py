from datetime import datetime
from typing import Iterator

import pygal

from utils import (CAPACITY_REPORT_FILE, MILESTONE_PROGRESS_REPORT_FILE,
                   NEW_ISSUES_REPORT_FILE, calculate_capacity,
                   calculate_milestone_progress, get_issues_overview)


def generate_team_capacity_report(timeslots: Iterator[datetime.date]):
    dashboard_diff = calculate_capacity("dashboard", timeslots)
    devops_diff = calculate_capacity("devops", timeslots)
    cobro_diff = calculate_capacity("cobro", timeslots)

    chart = pygal.Dot(width=50 * len(timeslots), x_label_rotation=-90)
    chart.title = "Open / Closed issues difference per team"
    chart.x_labels = map(lambda d: d.strftime("%G, w%V"), timeslots)
    chart.add("devops", devops_diff)
    chart.add("cobro",  cobro_diff)
    chart.add("dashboard", dashboard_diff)
    chart.render_to_file(CAPACITY_REPORT_FILE)


def generate_milestone_progress_report(name: str):
    progress = int(calculate_milestone_progress(name) * 100)

    chart = pygal.SolidGauge(half_pie=True, inner_radius=0.70)
    chart.title = "Roadmap progress"
    chart.value_formatter = lambda x: '{:.10g}%'.format(x)

    chart.add(name, [{"value": progress, "max_value": 100}])
    chart.render_to_file(MILESTONE_PROGRESS_REPORT_FILE)


def generate_new_issues_report():
    data = get_issues_overview()
    chart = pygal.Pie(inner_radius=.75)
    chart.title = "New issues distribution per client, last 7 days"
    for issue_type, amount in data.items():
        chart.add(issue_type, amount)
    chart.render_to_file(NEW_ISSUES_REPORT_FILE)
