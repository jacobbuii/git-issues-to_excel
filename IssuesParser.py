import pathlib
import subprocess

import pandas as pd


def parse_header(header):
    """
    Parses the header to get the link to the next page of issues, checks this
    isn't the last page.

    Args:
        header (str): header as string.

    Returns:
        str: link to the next page to parse
    """

    header_list = header.split("\n")
    links_line = [line for line in header_list if "Link: " in line][0]

    links = links_line.replace("Link: ", "").split(",")
    first_link, last_link = [link.split(";")[0] for link in links]

    first_link_formatted = first_link.lstrip("<").rstrip(">")
    last_link_formatted = last_link.lstrip(" <").rstrip(">")

    return first_link_formatted, last_link_formatted


def split_header(curl_output):
    """
    Splits the header and the json output from a curl call.

    Args:
        curl_output (str): output from curl call.

    Returns:
        tuple: tuple of strings in the order (header, json_content).
    """

    # json content starts at the first open square bracket
    json_start_idx = curl_output.find("[")

    return curl_output[:json_start_idx], curl_output[json_start_idx:]


def get_issues_json(curl_url):
    """
    Calls curl via subprocess and writes the curl output to a json file.

    Args:
        curl_url (str): Link to the url to use as curl argument.

    Returns:
        pathlib.Path: filepath to json file containing output from curl call.
    """

    p = subprocess.Popen(["curl", "-i", curl_url], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    stdout, stderr = p.communicate()

    return split_header(stdout.decode("utf-8"))


def read_all_pages(repo_url):
    """
    Loops through all pages of a git repo's issues page.

    Args:
        repo_url (str): url of a git repo's issue page in the format:
            https://api.github.com/repos/org/repo/issues

    Returns:
        list: list of the json outputs as str for each page of issues.

    """

    first_header, first_json = get_issues_json(repo_url)
    next_page, last_page = parse_header(first_header)

    json_list = [first_json]
    while next_page != last_page:
        next_header, next_json = get_issues_json(next_page)
        json_list.append(next_json)
        next_page = parse_header(next_header)[0]

    return json_list
