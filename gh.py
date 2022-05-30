
import logging
import os

import requests

# mrt's access token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORGANIZATION = "surfly"
REPO = "it"
PER_PAGE = 100


def log_response(method, response):
    logging.warning(
        "  -- requested %s %s %s %s" % (
            method,
            response.url,
            response.status_code,
            "remaining: %s" % response.headers["X-RateLimit-Remaining"]
        )
    )
    if not response.ok:
        logging.info(response.content)


def _gh_request(method, *args, **kwargs):
    """
    Make the request to github api. Automatically authenticates the request and
    handles pagination
    """
    updated = set_request_defaults(**kwargs)
    response = getattr(requests, method)(*args, **updated)
    log_response(method, response)
    if response.status_code == 204:
        return
    data = response.json()["items"]
    while "next" in response.links.keys():
        args_list = list(args)
        args_list[0] = response.links["next"]["url"]
        # They are already included in next_url
        if "params" in updated:
            del updated["params"]
        response = getattr(requests, method)(*args_list, **updated)
        log_response(method, response)
        data.extend(response.json()["items"])
    return data


def set_request_defaults(**kwargs):
    updated = kwargs.copy()
    updated.setdefault(
        "headers",
        {"accept": "application/vnd.github.inertia-preview+json"}
    )
    updated.setdefault("params", {})
    updated["auth"] = ("", GITHUB_TOKEN)
    updated["params"].update({"per_page": PER_PAGE})
    return updated


def search_issues(query):
    return _gh_request(
        "get",
        "https://api.github.com/search/issues",
        headers={"accept": "application/vnd.github.v3+json"},
        params={
            "q": query,
        }
    )
