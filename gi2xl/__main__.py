import sys

from gi2xl.get_issues import main
from gi2xl.utils.command_line_utils import parse_args

if __name__ == "__main__":
    command_line_args = sys.argv[1:]

    repo_url, username, auth_token = parse_args(command_line_args)

    main(repo_url, username, auth_token)
