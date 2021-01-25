import json
import pathlib
import re
import subprocess
import sys

import pandas as pd


def parse_header(header):
    """
    Parses the header to get the link to the next page of issues, checks this
    isn't the last page.

    Args:
        header (str): header as string.
    Returns:
        tuple/str: link to the next page and last page to parse or just the
            next page.

    """

    formatting = re.compile("[\ \<\>]")

    header_list = header.split("\n")
    links_line = [line for line in header_list if "Link: " in line][0]

    # remove formatting and link separator from line
    links = links_line.replace("Link: ", "").split(",")
    links = [formatting.sub("", link) for link in links]

    # initialise return values
    prev_link, next_link, last_link = [None, None, None]

    # occurs for links after the first
    if len(links) == 4:
        prev_link, next_link, last_link, first_link = [
            link.split(";")[0] for link in links
        ]
    # occurs for the first link
    elif len(links) == 2:
        next_link, last_link = [link.split(";")[0] for link in links]
    # handles unexpected number of links, indicates an error in the header
    else:
        print("Error! unexpected number of links")
        sys.exit(1)

    return prev_link, next_link, last_link


def split_header(curl_output):
    """
    Splits the header and the json output from a curl call.

    Args:
        curl_output (str): output from curl call.

    Returns:
        tuple: tuple of header string and json.
    """

    # json content starts at the first open square bracket
    json_start_idx = curl_output.find("[")
    # convert string to json
    actual_json = json.loads(curl_output[json_start_idx:])

    return curl_output[:json_start_idx], actual_json


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
        print("appending json for page: {}".format(next_page))
        # gets the urls for the next page
        next_page = parse_header(next_header)[1]

    return json_list


def jsons_to_excel(list_of_jsons, sepby="sheets", filename=None):
    """

    Args:
        list_of_jsons (list): A list of jsons to write to a spreadsheet
        sepby (str): "sheets" or "rows", sheets writes each json to a separate
            excel sheet while rows writes each json to the next row.
        filename (str): name of excel file to write, defaults to write in the
            format <repo>_issues.xlsx

    Returns:
        pathlib.Path: filepath to excel file containing jsons
    """

    if filename is None:
        reponame = list_of_jsons[0][0]["url"].split("/")[-3]
        filename = "{}_issues.xlsx".format(reponame)

    with pd.ExcelWriter(filename) as writer:
        if sepby == "sheets":
            for i, json_issue in enumerate(list_of_jsons, 1):
                sheet_name = "page {}".format(i)
                df = tidy_df(pd.DataFrame(json_issue))
                df.to_excel(writer, sheet_name=sheet_name, engine='xlsxwriter')
        elif sepby == "rows":
            df = tidy_df(pd.DataFrame(list_of_jsons[0]))
            for json_issue in list_of_jsons[1:]:
                df = df.append(tidy_df(pd.DataFrame(json_issue)),
                               ignore_index=True)
            df.to_excel(writer, sheet_name="all issues", engine='xlsxwriter')
        else:
            print("Invalid sepby option!")
            sys.exit(1)


def tidy_df(df, columns_to_keep=None):
    """
    Removes useless columns and tidies the dataframe.

    Args:
        df (pd.DataFrame): data frame to tidy.
        columns_to_keep (list): list of column names to keep, will remove all
            others.

    Returns:
        pd.DataFrame: tidied data frame.
    """

    if columns_to_keep is None:
        columns_to_keep = [
            "html_url", "number", "title", "created_at", "updated_at",
            "closed_at", "body", "labels"
        ]

    columns_to_drop = [col for col in df.columns if col not in columns_to_keep]

    if "labels" in columns_to_keep:
        df.labels = df.labels.apply(lambda x: get_label_name_from_dict(x))

    return df.drop(columns_to_drop, axis=1)


def get_label_name_from_dict(labels_dict_list):
    """
    Parses the labels dict and returns just the names of the labels.

    Args:
        labels_dict_list (list): list of dictionaries

    Returns:
        str: name of each label separated by commas.
    """

    label_names = [a_dict["name"] for a_dict in labels_dict_list]

    return ",".join(label_names)


# todo tidy up this hook
def main(repo_url, username=None, auth_token=None):
    if username is None:
        username = input("Enter git username:")
    if auth_token is None:
        auth_token = input("Enter git authentication token:")
    json_list = read_all_pages(repo_url, username, auth_token)
    jsons_to_excel(json_list, sepby="rows")


if __name__ == "__main__":
    command_line_args = sys.argv[1:]
    if len(command_line_args) == 2:
        username, auth_token = command_line_args
    else:
        username, auth_token = [None, None]
    main('https://api.github.com/repos/pandas-dev/pandas/issues?labels=Bug&per_page=100',
         username, auth_token)
