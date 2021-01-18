import pathlib
import subprocess

import pandas as pd


def parse_header(header, get_last_link=False):
    """
    Parses the header to get the link to the next page of issues, checks this
    isn't the last page.

    Args:
        header (str): header as string.
        get_last_link (bool): flag to determine whether to get the last link or
            not.

    Returns:
        tuple/str: link to the next page and last page to parse or just the
            next page.

    """

    header_list = header.split("\n")
    links_line = [line for line in header_list if "Link: " in line][0]

    links = links_line.replace("Link: ", "").split(",")

    if get_last_link:
        first_link, last_link = [link.split(";")[0] for link in links]
        return first_link.lstrip("<").rstrip(">"), \
            last_link.lstrip(" <").rstrip(">")
    else:
        first_link = [link.split(";")[0] for link in links][0]
        return first_link.lstrip("<").rstrip(">")


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


def get_issues_json(curl_url, username, auth_token=None):
    """
    Calls curl via subprocess and writes the curl output to a json file.

    Args:
        curl_url (str): Link to the url to use as curl argument.
        username (str): github username.
        auth_token (str): github authentication token.

    Returns:
        pathlib.Path: filepath to json file containing output from curl call.
    """

    curl_command = ["curl", "-i", curl_url]

    # add authentication info if provided
    if auth_token is not None:
        curl_command.pop()
        curl_command += ["-u", "{}:{}".format(username, auth_token), curl_url]

    p = subprocess.Popen(curl_command, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    stdout, stderr = p.communicate()

    return split_header(stdout.decode("utf-8"))


def read_all_pages(repo_url, username, auth_token=None):
    """
    Loops through all pages of a git repo's issues page.

    Args:
        repo_url (str): url of a git repo's issue page in the format:
            https://api.github.com/repos/org/repo/issues
        username (str): github username.
        auth_token (str): github authentication token.

    Returns:
        list: list of the json outputs as str for each page of issues.

    """

    first_header, first_json = get_issues_json(repo_url, username, auth_token)
    next_page, last_page = parse_header(first_header, get_last_link=True)

    json_list = [first_json]
    while next_page != last_page:
        next_header, next_json = get_issues_json(
            next_page, username, auth_token)
        json_list.append(next_json)
        next_page = parse_header(next_header)

    return json_list
