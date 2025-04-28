"""__summary_: semantic_tag_utility.tools.api_client
    This module provides utility functions for interacting with a semantic tag API. 
    It includes functions to retrieve projects, commits, and elements, as well as 
    download the latest elements from the API.
    Functions:
        get_projects(api_url):
            Retrieves a list of projects from the API, sorted by creation date in descending order.
        get_commits(projectId, api_url):
            Retrieves a list of commits for a specific project from the API, sorted by creation date in descending order.
        get_elements(projectId, commitId, api_url):
            Retrieves the elements associated with a specific commit of a project from the API.
        download_latest_elements(api_url):
            Downloads the elements of the latest commit of the most recently created project 
            and saves them to a JSON-LD file.
    Dependencies:
        - datetime: For handling and formatting date and time.
        - json: For parsing and serializing JSON data.
        - os.path: For handling file paths.
        - requests: For making HTTP requests to the API.

    Returns:
        _type_: _description_
"""

import datetime
import json
import os.path

import requests


def get_projects(api_url):
    payload = {}
    headers = {"Accept": "application/ld+json"}

    process_list = []

    try:
        response = requests.request(
            "GET", f"{api_url}projects", headers=headers, data=payload
        )
        projects = json.loads(response.text)
        for project in projects:
            created = datetime.datetime.fromisoformat(project["created"])
            pid = project["@id"]
            process_list.append((created, pid))

        process_list.sort(reverse=True)

    except Exception as ex:
        print(ex)

    return process_list


def get_commits(projectId, api_url):
    payload = {}
    headers = {"Accept": "application/ld+json"}

    process_list = []

    try:
        response = requests.request(
            "GET",
            f"{api_url}projects/{projectId}/commits",
            headers=headers,
            data=payload,
        )
        commits = json.loads(response.text)

        for commit in commits:
            created = datetime.datetime.fromisoformat(commit["created"])
            process_list.append((created, projectId, commit["@id"]))

        process_list.sort(reverse=True)

    except Exception as ex:
        print(ex)

    return process_list


def get_elements(projectId, commitId, api_url):
    payload = {}
    headers = {"Accept": "application/ld+json"}

    elements = {}

    try:
        req_url = f"{api_url}projects/{projectId}/commits/{commitId}/elements"
        response = requests.request(
            "GET",
            req_url,
            headers=headers,
            data=payload,
        )
        elements = json.loads(response.text)

    except Exception as ex:
        print(ex)

    return elements


def download_latest_elements(api_url):
    projects = get_projects(api_url)
    latest_date, latest_project_id = projects[0]
    print(latest_date.isoformat())
    commits = get_commits(latest_project_id, api_url)
    latest_commit = commits[0][2]
    elements = get_elements(latest_project_id, latest_commit, api_url)
    with open("elements.jsonld", "w") as f:
        json.dump(elements, f, indent=2)

    base = f"http://projects/{latest_project_id}/commits/{latest_commit}/elements/"
    return os.path.abspath("elements.jsonld"), base
