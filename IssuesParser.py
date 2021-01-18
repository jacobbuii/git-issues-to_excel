import pathlib
import subprocess

import pandas as pd


def remove_header(curl_output):
    """
    Splits the header and the json output from a curl call.

    Args:
        curl_output (str): output from curl call.

    Returns:

    """


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

    json_content, header = split_header(stdout)
