# This file can download the rarity data from website rarity.tools
# There is a hidden API - "https://projects.rarity.tools/static/staticdata/<project_name>.json" that we can use to download rarity data in seconds.
# However the data is in raw format, we need to recalculate the scoring using the algorithm below.

# Without Traits Normalization, Rarity tools use a formula of Rarity Score = 1 / (Counts Of Traits X Total Number Of Tokens)

# With Traits Normalization, Rarity tools use a formula of Rarity Score = (Constant Number / ( Number Of Traits Type  X  Number Of Category In That Trait Types ) ) / (Counts Of Traits X Total Number Of Tokens)
# The Constant Number is 100,000 Divide by Total Number Of Tokens.
# The number 100,000 is an arbitrary number chosen by Rarity tools I guess. I found these number by reverse engineering a few different Samples

# The calculation will give the exact Rarity Score shown in Rarity tools with a few exceptions
# There are some NFT projects that Rarity tools added Thematic Match / Matching Sets
# Due to those data irregularity, This script WILL NOT account for theses matches (So the scoring for projects with these Thematic Matches might differ)
# Revision: 1.0
# Date: Nov 17, 2021
# by @NFT131 #9693 (Discord Username)
# email: nft131@gmail.com
# If you need any clarification, email me. We can discuss more


def download(
    project_name: str = "vogu", starting_count_y: int = 1, normalize_trait: int = 1
) -> None:
    # The variable "starting_count_y" is usually 1, but in Rare case, the count has to start at 2, due to irregular data structure used by Rarity tools
    # Leave "normalize_trait" as default value 1, unless you want to turn it off. (Not recommended to turn it off, as normalize_trait will give better accuracy)
    import csv
    import requests
    import time
    from pprint import pprint

    from utils import config

    start_time = time.time()

    print("Project : " + str(project_name))

    # Saves the rarity data into the Folder "rarity_data" provided
    metadata_attributes_csv_file_name = f"{config.ATTRIBUTES_FOLDER}/{project_name}.csv"

    # Saves the rarity data into the Folder "rarity_data" provided
    metadata_scoring_csv_file_name = (
        f"{config.RARITY_FOLDER}/{project_name}_raritytools.csv"
    )

    warning_flag = False

    url = "https://projects.rarity.tools/static/staticdata/" + project_name + ".json"

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    }

    response = requests.request("GET", url, headers=headers)
    response_data = response.json()
    all_traits = response_data["basePropDefs"]
    number_of_traits_types = len(all_traits) - 1
    nft_metadata = response_data["items"]
    metadata_scoring = {}
    metadata_to_save = {}
    total_tokens_len = len(nft_metadata)
    constant_number = (
        1000000 / total_tokens_len
    )  # This constant number is used to normalize the scoring, I found it by reverse engineering a few samples
    rarity_table = {}

    # cut off the last element, if it is an empty array (cause problems with the script)
    last_element_of_metadata = nft_metadata[0][len(nft_metadata[0]) - 1]
    if (
        isinstance(last_element_of_metadata, list)
        and len(last_element_of_metadata) == 0
    ):
        trailing_count_to_cut = 1
    else:
        trailing_count_to_cut = 0
    nft_metadata_len = len(nft_metadata[0]) - trailing_count_to_cut

    # Looping through each token, and decode the metadata stored by rarity tools
    # They use Numbers to represent the data, which makes the file size smaller to download
    for x in range(0, total_tokens_len):

        token_id = str(nft_metadata[x][0])
        metadata_to_save.update({token_id: {"nft_traits": []}})

        metadata_scoring.update(
            {
                token_id: {
                    "TOKEN_ID": token_id,
                    "TOKEN_NAME": project_name + " #" + str(token_id),
                }
            }
        )
        token_rarity_score = 0
        this_token_trait = []
        each_trait_score = {}

        # Looping through each Metadata of the token, and calculating rarity scores
        for y in range(starting_count_y, nft_metadata_len):
            # There is a chance that Thematic Match info is stored as "derivedPropDefs" from the data query. Skipping this condition.
            # This happens while extracting "Wicked Craniums" project
            if y >= len(all_traits):
                warning_flag = True
                break

            this_trait_rarity_score = 0
            temp_scoring = 0
            # Some traits data is stored as List, so we have to loop it through
            if isinstance(nft_metadata[x][y], list):

                temp_scoring = 0
                if len(nft_metadata[x][y]) == 0:
                    if normalize_trait:
                        try:
                            number_of_category = len(all_traits[y]["pvs"])
                        except:
                            print(y)
                            pprint(all_traits[y])
                            input(
                                "Error Found on the count above. Press Any key to continue."
                            )

                        token_rarity_score = token_rarity_score + (
                            constant_number
                            / (number_of_traits_types * number_of_category)
                        ) / (all_traits[y]["pvs"][0][1] / total_tokens_len)
                        this_trait_rarity_score = (
                            constant_number
                            / (number_of_traits_types * number_of_category)
                        ) / (all_traits[y]["pvs"][0][1] / total_tokens_len)
                        temp_scoring += this_trait_rarity_score
                    else:
                        token_rarity_score = token_rarity_score + 1 / (
                            all_traits[y]["pvs"][0][1] / total_tokens_len
                        )
                        temp_scoring += this_trait_rarity_score
                else:
                    for each_theme in nft_metadata[x][y]:
                        if normalize_trait:

                            try:
                                number_of_category = len(all_traits[y]["pvs"])
                            except:
                                print(y)
                                pprint(all_traits[y])
                                input(
                                    "Error Found on the count above. Press Any key to continue."
                                )

                            token_rarity_score = token_rarity_score + (
                                constant_number
                                / (number_of_traits_types * number_of_category)
                            ) / (all_traits[y]["pvs"][each_theme][1] / total_tokens_len)
                            this_trait_rarity_score = (
                                constant_number
                                / (number_of_traits_types * number_of_category)
                            ) / (all_traits[y]["pvs"][each_theme][1] / total_tokens_len)
                            temp_scoring += this_trait_rarity_score
                        else:
                            token_rarity_score = token_rarity_score + 1 / (
                                all_traits[y]["pvs"][each_theme][1] / total_tokens_len
                            )
                            this_trait_rarity_score = 1 / (
                                all_traits[y]["pvs"][each_theme][1] / total_tokens_len
                            )
                            temp_scoring += this_trait_rarity_score
            else:
                if normalize_trait:
                    # Skip the traits that doesn't contain keys: pvs -> very unusual
                    # Was spotted once with byopills project
                    if all_traits[y].get("pvs", "empty") == "empty":
                        break
                    else:
                        number_of_category = len(all_traits[y]["pvs"])

                        token_rarity_score = token_rarity_score + (
                            constant_number
                            / (number_of_traits_types * number_of_category)
                        ) / (
                            all_traits[y]["pvs"][nft_metadata[x][y]][1]
                            / total_tokens_len
                        )
                        this_trait_rarity_score = (
                            constant_number
                            / (number_of_traits_types * number_of_category)
                        ) / (
                            all_traits[y]["pvs"][nft_metadata[x][y]][1]
                            / total_tokens_len
                        )

                else:
                    token_rarity_score = token_rarity_score + 1 / (
                        all_traits[y]["pvs"][nft_metadata[x][y]][1] / total_tokens_len
                    )
                    this_trait_rarity_score = 1 / (
                        all_traits[y]["pvs"][nft_metadata[x][y]][1] / total_tokens_len
                    )

            if isinstance(nft_metadata[x][y], list):

                for each_theme in nft_metadata[x][y]:
                    this_token_trait.append(
                        {
                            "node": {
                                "traitType": all_traits[y]["name"],
                                "value": all_traits[y]["pvs"][each_theme][0],
                            }
                        }
                    )

                each_trait_score.update({all_traits[y]["name"]: temp_scoring})
            else:
                this_token_trait.append(
                    {
                        "node": {
                            "traitType": all_traits[y]["name"],
                            "value": all_traits[y]["pvs"][nft_metadata[x][y]][0],
                        }
                    }
                )
                each_trait_score.update(
                    {all_traits[y]["name"]: this_trait_rarity_score}
                )

        rarity_table.update({str(token_id): float(token_rarity_score)})
        metadata_to_save[token_id].update({"nft_traits": this_token_trait})
        metadata_scoring[token_id].update(each_trait_score)

    # Sort all the rarity data base on the rarity scores (Descending Order)
    sorted_rarity_table = sorted(
        rarity_table.items(), key=lambda item: item[1], reverse=True
    )
    print("Number of Token : " + str(len(metadata_to_save)))

    rarity_table_upload = {}
    count = 1
    # Adding ranking to each of the token
    for each_item in range(0, len(sorted_rarity_table)):
        rarity_table_upload.update(
            {
                str(sorted_rarity_table[each_item][0]): {
                    "rank": count,
                    "rarity_score": float(sorted_rarity_table[each_item][1]),
                }
            }
        )
        metadata_to_save[str(sorted_rarity_table[each_item][0])].update(
            {"rank": count, "rarity_score": float(sorted_rarity_table[each_item][1])}
        )
        metadata_scoring[str(sorted_rarity_table[each_item][0])].update(
            {"RARITY_SCORE": float(sorted_rarity_table[each_item][1]), "Rank": count}
        )

        count = count + 1

    scoring_csv = []

    # Adding scoring of each traits to each of the token
    for each_token in metadata_scoring:
        this_row = []

        for each_col in metadata_scoring[each_token]:
            this_row.append(metadata_scoring[each_token][each_col])
        scoring_csv.append(this_row)

    sorted_scoring_csv = sorted(
        scoring_csv, key=lambda item: item[len(item) - 1], reverse=False
    )

    # Create Header
    header_row = []
    for each_col in metadata_scoring["1"]:
        header_row.append(each_col)

    # Save to csv file
    with open(metadata_scoring_csv_file_name, "w") as f:
        write = csv.writer(f)
        write.writerow(header_row)
        write.writerows(sorted_scoring_csv)

    save_raw_attributes_csv(
        collection=project_name,
        raw_attributes=metadata_to_save,
        file_path=metadata_attributes_csv_file_name,
    )

    if warning_flag:
        print(
            "============\nWARNING\n==============\nThe rarity data you are trying to extract might contain Thematic Match / Matching Sets that this script ignored. \nSo while you compare with Rarity Tools data, make sure Thematic Sets is turned off.\n\n"
        )

    print("--- %s seconds Taken to Download ---" % (time.time() - start_time))


def save_raw_attributes_csv(
    collection: str, raw_attributes: list, file_path: str
) -> None:
    import pandas as pd

    # List to store all tokens traits
    trait_data = []
    for token in raw_attributes:
        # empty dict to store this token traits
        token_raw = dict()
        token_raw["TOKEN_ID"] = token
        token_raw["TOKEN_NAME"] = f"{collection} #{str(token)}"

        for trait in raw_attributes[token]["nft_traits"]:
            if trait["node"]["traitType"] != "Trait Count":
                token_raw[trait["node"]["traitType"]] = trait["node"]["value"]

        trait_data.append(token_raw)

    # convert list to pandas dataframe and save to disk
    raw_attributes_csv = pd.DataFrame.from_records(trait_data)
    raw_attributes_csv.to_csv(file_path)
