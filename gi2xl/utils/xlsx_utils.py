import sys

import pandas as pd


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
