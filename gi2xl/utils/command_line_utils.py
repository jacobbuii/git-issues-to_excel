import sys


def parse_args(command_line_args):
    """
    Parses the command line arguments, expected in the order: repo_url,
    username and git authorisation token.

    Args:
        command_line_args (list): list of command line arguments, should
        contain the following: repo_url (required), username (optional),
        authorisation token (optional).

    Returns:
        tuple: parsed command line args, optional args are set to None if not
        provided.
    """

    # TODO: use argsparse?
    if len(command_line_args) == 3:
        repo_url, username, auth_token = command_line_args
    elif len(command_line_args) == 1:
        repo_url = command_line_args
        username, auth_token = [None, None]
    else:
        print("Error! repo_url not provided!")
        sys.exit(1)

    # adds max per page option to reduce calls to git api
    if "?" not in repo_url:
        repo_url += "?per_page=100"
    else:
        repo_url += "&per_page=100"

    return repo_url, username, auth_token
