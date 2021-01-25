import json
import re
import sys


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
