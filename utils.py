import logging
from datetime import datetime, timedelta
from typing import Any, Iterator

from jinja2 import Template
from gh import search_issues


CAPACITY_REPORT_FILE = "capacity_report.svg"
MILESTONE_PROGRESS_REPORT_FILE = "milestone_progress_report.svg"
NEW_ISSUES_REPORT_FILE = "new_issues_report.svg"


def get_closest_thursday(date: datetime.date) -> datetime.date:
    isocal = date.isocalendar()
    return datetime.strptime(
        f"{isocal.year} {isocal.week} 4", "%G %V %u"
    ).date()


def generate_timeslots(date: datetime.date) -> Iterator[datetime.date]:
    result = []
    while date <= datetime.now().date():
        result.append(date)
        date = date + timedelta(days=7)
    return result


def calculate_capacity(team: str, timeslots: Iterator[datetime.date]) -> Iterator[int]:
    data = [0 for x in timeslots]
    all_open_query = " ".join((
        "repo:surfly/it",
        f"created:>={timeslots[0].isoformat()}",
        f"label:team:{team}",
    ))
    all_closed_query = " ".join((
        "repo:surfly/it",
        f"closed:>={timeslots[0].isoformat()}",
        f"label:team:{team}",
    ))

    open_issues = search_issues(all_open_query)
    logging.info(f"Found {len(open_issues)} opened issues for team {team}")
    assign_issues_to_timeslots(data, timeslots, open_issues, True)

    closed_issues = search_issues(all_closed_query)
    logging.info(f"Found {len(closed_issues)} closed issues for team {team}")
    assign_issues_to_timeslots(data, timeslots, closed_issues, False)

    return data


==== BASE ====
def assign_issues_to_timeslots(data: Iterator[int], timeslots: Iterator[datetime.date], issues: Iterator[Any], opened: Bool):
==== BASE ====
    for week_number, week_until in enumerate(timeslots):
        for item in issues:
            event_date = datetime.fromisoformat(item["created_at"][:-1]).date()
            if week_number < len(timeslots) - 1:
                if event_date >= week_until and event_date < timeslots[week_number+1]:
                    logging.info(
                        f"Addidng {item['html_url']} created on {event_date.isoformat()} to slot for {week_until}"
                    )
                    if opened:
                        data[week_number] += 1
                    else:
                        data[week_number] -= 1
            else:
                if event_date >= week_until:
                    logging.info(
                        f"Addidng {item['html_url']} created on {event_date.isoformat()} to slot for {week_until}"
                    )
                    if opened:
                        data[week_number] += 1
                    else:
                        data[week_number] -= 1


def calculate_milestone_progress(name):
    query = " ".join((
        "repo:surfly/it",
        f"milestone:{name}",
    ))
    issues = search_issues(query)
    opened = 0
    closed = 0
    for item in issues:
        if item["state"] == "open":
            opened += 1
        elif item["state"] == "closed":
            closed += 1
        else:
            logging.warning(f"Unhandled issue state {item['state']} {item['html_url']}")
    return closed / (opened + closed)


def get_issues_overview():
    query = " ".join((
        "repo:surfly/it",
        f"created:>={(datetime.now().date() - timedelta(days=7)).isoformat()}",
    ))
    issues = search_issues(query)
    data = {
        "internal": 0,
    }
    for item in issues:
        counted = False
        if item["labels"]:
            for label in item["labels"]:
                if label["name"].startswith("client:"):
                    c_name = label["name"].replace("client:", "")
                    data.setdefault(c_name, 0)
                    data[c_name] += 1
                    counted = True
            if not counted:
                data["internal"] += 1
        else:
            data["internal"] += 1
    return data


def generate_report_page():
    with open("report.j2") as f:
        t = Template(f.read())

    # Create HTML overview
    with open("report.html", "w") as f:
        f.write(t.render(
            created_at=datetime.now().strftime("%-d %B, %Y"),
            capacity_report_file=CAPACITY_REPORT_FILE,
            milestone_progress_report_file=MILESTONE_PROGRESS_REPORT_FILE,
            new_issues_report_file=NEW_ISSUES_REPORT_FILE,
        ))
