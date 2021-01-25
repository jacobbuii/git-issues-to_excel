from gi2xl.utils.xlsx_utils import jsons_to_excel
from gi2xl.utils.curl_utils import read_all_pages


def main(repo_url, username=None, auth_token=None):
    if username is None:
        username = input("Enter git username:")
    if auth_token is None:
        auth_token = input("Enter git authentication token:")
    json_list = read_all_pages(repo_url, username, auth_token)
    jsons_to_excel(json_list, sepby="rows")
