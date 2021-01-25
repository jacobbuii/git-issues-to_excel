import pathlib
import subprocess

from gi2xl.utils.json_utils import parse_header, split_header


def get_issues_json(curl_url, username, auth_token=None):
    """
    Calls curl via subprocess and returns the header and json content.

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

    # call curl to get the issues from git
    p = subprocess.Popen(curl_command, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    # read stdout which will contain curl output
    stdout, stderr = p.communicate()

    # return decoded stdout
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

    # reads the first page
    first_header, first_json = get_issues_json(repo_url, username, auth_token)
    print("parsing json for page: {}".format(repo_url))
    # gets the second and last page from the first header
    prev_page, next_page, last_page = parse_header(first_header)

    # initialises lists for use in loop
    json_list = [first_json]
    parsed_pages = []

    # loops through all pages
    while next_page not in parsed_pages:
        # todo: add a check to see if the rate limit has been exceeded
        # gets the json for the next_page
        next_header, next_json = get_issues_json(
            next_page, username, auth_token
        )
        json_list.append(next_json)
        # makes a note of the pages which have been parsed
        parsed_pages.append(next_page)
        print("parsing json for page: {}".format(next_page))
        # gets the urls for the next page
        next_page = parse_header(next_header)[1]

    return json_list
