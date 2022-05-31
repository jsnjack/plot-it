import logging
from datetime import datetime, timedelta
from typing import Any, Iterator

from gh import search_issues


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


def generate_diff(team: str, timeslots: Iterator[datetime.date]) -> Iterator[int]:
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


def assign_issues_to_timeslots(data: Iterator[int], timeslots: Iterator[datetime.date], issues: Iterator[Any], opened: Any):
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
