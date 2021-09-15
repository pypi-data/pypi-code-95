# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

import json
import os


def get_credentials_from_file(amazon_cred_path: str = None) -> dict:
    amazon_cred_path = os.path.expanduser(amazon_cred_path or "~/accessKeys.csv")
    default_path = os.path.expanduser("~/.aws/credentials")
    testing_path = os.path.expanduser("~/.local/share/neon/aws.json")

    amazon_creds = dict()

    if os.path.isfile(testing_path):
        with open(testing_path, "r") as f:
            amazon_creds = json.load(f)
    elif os.path.isfile(amazon_cred_path):
        with open(amazon_cred_path, "r") as f:
            aws_id, aws_key = f.readlines()[1].rstrip('\n').split(',', 1)
            amazon_creds = {"aws_access_key_id": aws_id,
                            "aws_secret_access_key": aws_key}
    elif os.path.isfile(default_path):
        aws_id = None
        aws_key = None
        with open(default_path, "r") as f:
            for line in f.read().split("\n"):
                if line.startswith("aws_access_key_id"):
                    aws_id = line.split("=", 1)[1].strip()
                elif line.startswith("aws_secret_access_key"):
                    aws_key = line.split("=", 1)[1].strip()
        amazon_creds = {"aws_access_key_id": aws_id,
                        "aws_secret_access_key": aws_key}
    return amazon_creds
