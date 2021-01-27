# git_issues_to_excel
Python code to read git issues via curl and convert them to an excel file.

Works in Linux and Windows as long as git is installed.

Command line usage:
`python -m gi2xl <git_api_issues_url> <git_username> <git_authentication_token>`

See https://docs.github.com/en/rest/reference/issues for more on the github issues 
API syntax and url usage.

See https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
for information on generating a personal git authentication token.

Examples:

Get all open issues with the label `00 - Bug` from numpy:

`python -m gi2xl "https://api.github.com/repos/numpy/numpy/issues?labels=00+-+Bug" <git_username> <git_authentication_token>`

Get all closed issues with the label `00 - Bug` from numpy:

`python -m gi2xl "https://api.github.com/repos/numpy/numpy/issues?labels=00+-+Bug&state=closed" <git_username> <git_authentication_token>`
