#!/usr/bin/python3
import json
import re

import numpy as np
import pandas as pd


def extract_fields_from_metadata(meta_file):
    with open(meta_file, "r") as file:
        data = json.load(file)

    subproject = data.get("Auxiliary Metadata", {}).get("subproject", {}).get("@value", "")
    phs_identifier = data.get("Data File Parent Studies", [{}])[0].get("PHS Identifier", {}).get("@value", "")
    project_num = data.get("Data File Parent Studies", [{}])[0].get("Study Identifier", {}).get("@value", "")
    related_resources = data.get("Data File Related Resources", [{}])
    publications = [related_resource.get("Related Resource Identifier", {}).get("@value", "") for related_resource in related_resources]

    return subproject, phs_identifier, project_num, publications


def extract_radx_id(file_path):
    # Regular expression to match patterns like rad_*_*-*
    pattern = r"rad_[A-Za-z0-9]+_[A-Za-z0-9]+-[A-Za-z0-9]+"

    # Extract the first match
    match = re.search(pattern, file_path)
    if match:
        return match.group()

    return ""


def assign_data_element_tier(df, tier1_dict, tier2_dict):
    tier1 = pd.read_csv(tier1_dict, usecols=["Id"])
    tier1_ids = set(tier1["Id"].to_list())
    tier2 = pd.read_csv(tier2_dict, usecols=["Id"])
    tier2_ids = set(tier2["Id"].to_list())

    # Define conditions
    conditions = [
        df["Id"].isin(tier1_ids),  # Check if ID is in tier 1
        df["Id"].isin(tier2_ids),  # Check if ID is in tier 2
    ]

    # Define corresponding tier values
    choices = ["tier1", "tier2"]

    # Assign tiers based on conditions
    df["tier"] = np.select(conditions, choices, default="tier3")

    return df