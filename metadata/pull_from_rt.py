def download(project_name = "vogu", starting_count_y = 1, thematic_match = False, normalize_trait = 1):
    
    import csv
    import requests
    import time
    import json
    from pprint import pprint
    import os
    

    import datetime
    dt_now = datetime.datetime.utcnow()
    start_time = time.time()
    script_dir = os.path.dirname(__file__)
    script_dir += "/from_raritytools/{}".format(project_name)
    print("script dir: ", script_dir)
    
    
    if not os.path.exists(script_dir):
        os.makedirs(script_dir)
    
    metadata_file_name = os.path.join(script_dir,  project_name +"_metadata.json")
    metadata_scoring_file_name = os.path.join(script_dir,  project_name +"_scoring_metadata.json")
    metadata_scoring_csv_file_name = os.path.join(script_dir,  project_name +"_raritytools.csv")


    if normalize_trait:
        file_name = os.path.join(script_dir,  project_name +"_rarity_norm.json")
    else:
        file_name = os.path.join(script_dir,  project_name +"_rarity.json")

    url = "https://projects.rarity.tools/static/staticdata/"+ project_name + ".json"

    
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    
    project_variance = {"vogu" : { "trailing_metadata" : 2,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : True,
                                    "itemToAvoid" : None
                                    }, 
                        "world-of-women-nft" : { "trailing_metadata" : 1,
                                                'thematic_key' : "basePropDefs",
                                                "isList" : False,
                                                "itemToAvoid" : None
                                                },   
                        "thewickedcraniums" : { "trailing_metadata" : 1,
                                                'thematic_key' : "derivedPropDefs",
                                                "isList" : False,
                                                "itemToAvoid" : None
                                                },
                        "veefriends" : { "trailing_metadata" : 1,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : False,
                                    "itemToAvoid" : 8
                                    },

                        "byopills": { "trailing_metadata" : 1,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : False,
                                    "itemToAvoid" : None
                                    },
                        "boredapeyachtclub" :{ "trailing_metadata" : 1,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : False,
                                    "itemToAvoid" : None
                                    },

                        "cool-cats-nft": { "trailing_metadata" : 1,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : False,
                                    "itemToAvoid" : None
                                    }
                        }
    
    if project_variance.get(project_name,"empty") == "empty":
        target_project =   { "trailing_metadata" : 0,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : False,
                                    "itemToAvoid" : None
                                    }
    else:
        target_project = project_variance[project_name]    

    matching_traits = 2
    
     
    response = requests.request("GET", url, headers=headers )
    response_data = response.json()
    all_traits = response_data[u'basePropDefs']
    number_of_traits_types = len(all_traits) - 1
    nft_metadata = response_data[u'items']

    metadata_scoring = {}
    metadata_to_save = {}
    

    if thematic_match:
        nft_metadata_len = len(nft_metadata[0]) - target_project[u'trailing_metadata'] + 1
        themematic_match_position = nft_metadata_len - 1
    else:
        nft_metadata_len = len(nft_metadata[0]) - target_project[u'trailing_metadata']

    total_tokens_len = len(nft_metadata)
    constant_number = 1000000 / total_tokens_len

    rarity_table = {}
    for x in range(0,total_tokens_len):
        token_id = str(nft_metadata[x][0])
        metadata_to_save.update({token_id: {u'nft_traits' : []}})

        metadata_scoring.update({token_id: {u'TOKEN_ID' : token_id, 
                                            u'TOKEN_NAME' : project_name + ' #' + str(token_id) }})
        token_rarity_score = 0
        token_ranking = 0
        this_token_trait = []
        each_trait_score = {}
        
        for y in range(starting_count_y,nft_metadata_len):
            this_trait_rarity_score = 0
            temp_scoring = 0
            if thematic_match and y == themematic_match_position:
                if target_project[u'isList']:
                    temp_scoring = 0
                    
                    for each_theme in nft_metadata[x][y]:
                        if normalize_trait:
                            number_of_category = len(all_traits[y][u'pvs'])
                            
                            token_rarity_score = token_rarity_score + (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                            this_trait_rarity_score = (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                            temp_scoring += this_trait_rarity_score
                        else:
                            token_rarity_score = token_rarity_score + 1/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                            this_trait_rarity_score = 1/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                            temp_scoring += this_trait_rarity_score

                elif target_project[u'thematic_key'] == "derivedPropDefs":
                        theme = nft_metadata[x][y][0]
                        matching_set = response_data[u'derivedPropDefs'][0][u'pvs']
                        for each_matching_set in matching_set:
                            if (theme == each_matching_set[0]):
                                token_rarity_score = token_rarity_score + 1/(each_matching_set[1]/total_tokens_len)
                                this_trait_rarity_score = 1/(each_matching_set[1]/total_tokens_len)

            else:
                if target_project[u'itemToAvoid'] == None:
                    if isinstance(nft_metadata[x][y], list):
                        temp_scoring = 0
                        if len(nft_metadata[x][y]) == 0:
                            if normalize_trait:
                                try:
                                    number_of_category = len(all_traits[y][u'pvs'])
                                except:
                                    print(y)
                                    print(all_traits[y])
                                    input("preessss")
                                
                                token_rarity_score = token_rarity_score + (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][0][1]/total_tokens_len)
                                this_trait_rarity_score = (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][0][1]/total_tokens_len)
                                temp_scoring += this_trait_rarity_score
                            else:
                                token_rarity_score = token_rarity_score + 1/(all_traits[y][u'pvs'][0][1]/total_tokens_len)
                                temp_scoring += this_trait_rarity_score
                        else:
                            for each_theme in nft_metadata[x][y]:
                                if normalize_trait:
                                    number_of_category = len(all_traits[y][u'pvs'])
                                    
                                    token_rarity_score = token_rarity_score + (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                                    this_trait_rarity_score = (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                                    temp_scoring += this_trait_rarity_score
                                else:
                                    token_rarity_score = token_rarity_score + 1/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                                    this_trait_rarity_score = 1/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                                    temp_scoring += this_trait_rarity_score
                    else:
                        if normalize_trait:
                            number_of_category = len(all_traits[y][u'pvs'])
                            
                            token_rarity_score = token_rarity_score + (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][nft_metadata[x][y]][1]/total_tokens_len)
                            this_trait_rarity_score = (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][nft_metadata[x][y]][1]/total_tokens_len)
                        else:
                            token_rarity_score = token_rarity_score + 1/(all_traits[y][u'pvs'][nft_metadata[x][y]][1]/total_tokens_len)
                            this_trait_rarity_score =  1/(all_traits[y][u'pvs'][nft_metadata[x][y]][1]/total_tokens_len)


                    

                elif y == target_project[u'itemToAvoid']:
                    token_rarity_score = token_rarity_score

            if isinstance(nft_metadata[x][y], list):
                
                for each_theme in nft_metadata[x][y]:
                    this_token_trait.append({u'node' : {u'traitType' : all_traits[y][u'name'], u'value' : all_traits[y][u'pvs'][each_theme][0]}})
                    
                each_trait_score.update({all_traits[y][u'name'] : temp_scoring})
            else:
                this_token_trait.append({u'node' : {u'traitType' : all_traits[y][u'name'], u'value' : all_traits[y][u'pvs'][nft_metadata[x][y]][0]}})
                each_trait_score.update({all_traits[y][u'name'] : this_trait_rarity_score})
        
        rarity_table.update({str(token_id) : float(token_rarity_score)})
        metadata_to_save[token_id].update({u'nft_traits' : this_token_trait})
        metadata_scoring[token_id].update(each_trait_score)
    
    sorted_rarity_table = sorted(rarity_table.items(), key = lambda item : item[1],reverse=True)
    
    rarity_table_upload = {}
    count = 1
    for each_item in range(0,len(sorted_rarity_table)):
        rarity_table_upload.update({str(sorted_rarity_table[each_item][0]) : {"rank" : count, "rarity_score" : float(sorted_rarity_table[each_item][1])}})
        metadata_to_save[str(sorted_rarity_table[each_item][0])].update({"rank" : count, "rarity_score" : float(sorted_rarity_table[each_item][1])})
        metadata_scoring[str(sorted_rarity_table[each_item][0])].update({ "RARITY_SCORE" : float(sorted_rarity_table[each_item][1]),"Rank" : count})

        count = count + 1


    scoring_csv = []

    

    for each_token in metadata_scoring:
        this_row = []
        for each_col in metadata_scoring[each_token]:
            this_row.append(metadata_scoring[each_token][each_col])
        scoring_csv.append(this_row)
    

    sorted_scoring_csv = sorted(scoring_csv, key = lambda item : item[len(item)-1],reverse=False)

    #Create Header
    header_row = []
    for each_col in metadata_scoring["1"]:
        header_row.append(each_col)
    
    

    
    with open(file_name, 'w') as fp:
        json.dump(rarity_table_upload, fp)
    
    pprint(metadata_to_save["131"])
    with open(metadata_file_name, 'w') as fp:
        json.dump(metadata_to_save, fp)


    with open(metadata_scoring_file_name, 'w') as fp:
        json.dump(metadata_scoring, fp)


    # text_file = open(metadata_scoring_csv_file_name, "w")
    # text_file.write(scoring_csv)
    # text_file.close()
    with open(metadata_scoring_csv_file_name, 'w') as f: 
        write = csv.writer(f) 
        write.writerow(header_row) 
        write.writerows(sorted_scoring_csv) 
        
    
    print("--- %s seconds TO Load ---" % (time.time() - start_time))




def build_rarity_and_traits_adv(project_name = "vogu", starting_count_y = 1, thematic_match = False, normalize_trait = 1):
    import timeit
    import csv
    import requests
    import time
    start_time = time.time()
    import json
    from pprint import pprint
    import os
    script_dir = os.path.dirname(__file__)

    import datetime
    dt_now = datetime.datetime.utcnow()

    

    metadata_file_name = os.path.join(script_dir,  project_name +"_metadata.json")

    metadata_scoring_file_name = os.path.join(script_dir,  project_name +"_scoring_metadata.json")
    metadata_scoring_csv_file_name = os.path.join(script_dir,  project_name +"_raritytools.csv")


    if normalize_trait:
        file_name = os.path.join(script_dir,  project_name +"_rarity_norm.json")
    else:
        file_name = os.path.join(script_dir,  project_name +"_rarity.json")

    url = "https://projects.rarity.tools/static/staticdata/"+ project_name + ".json"

    
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }

    
    project_variance = {"vogu" : { "trailing_metadata" : 2,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : True,
                                    "itemToAvoid" : None
                                    }, 
                        "world-of-women-nft" : { "trailing_metadata" : 1,
                                                'thematic_key' : "basePropDefs",
                                                "isList" : False,
                                                "itemToAvoid" : None
                                                },   
                        "thewickedcraniums" : { "trailing_metadata" : 1,
                                                'thematic_key' : "derivedPropDefs",
                                                "isList" : False,
                                                "itemToAvoid" : None
                                                },
                        "veefriends" : { "trailing_metadata" : 1,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : False,
                                    "itemToAvoid" : 8
                                    },

                        "byopills": { "trailing_metadata" : 1,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : False,
                                    "itemToAvoid" : None
                                    },
                        "boredapeyachtclub" :{ "trailing_metadata" : 1,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : False,
                                    "itemToAvoid" : None
                                    },

                        "cool-cats-nft": { "trailing_metadata" : 1,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : False,
                                    "itemToAvoid" : None
                                    }
                        }
    
    if project_variance.get(project_name,"empty") == "empty":
        target_project =   { "trailing_metadata" : 0,
                                    'thematic_key' : "basePropDefs",
                                    "isList" : False,
                                    "itemToAvoid" : None
                                    }
    else:
        target_project = project_variance[project_name]    

    matching_traits = 2
    
     
    response = requests.request("GET", url, headers=headers )
    response_data = response.json()
    all_traits = response_data[u'basePropDefs']
    number_of_traits_types = len(all_traits) - 1
    nft_metadata = response_data[u'items']

    metadata_scoring = {}
    metadata_to_save = {}
    

    if thematic_match:
        nft_metadata_len = len(nft_metadata[0]) - target_project[u'trailing_metadata'] + 1
        themematic_match_position = nft_metadata_len - 1

    else:
        nft_metadata_len = len(nft_metadata[0]) - target_project[u'trailing_metadata']


    total_tokens_len = len(nft_metadata)
    constant_number = 1000000 / total_tokens_len

    rarity_table = {}
    for x in range(0,total_tokens_len):
        token_id = str(nft_metadata[x][0])
        metadata_to_save.update({token_id: {u'nft_traits' : []}})

        metadata_scoring.update({token_id: {u'TOKEN_ID' : token_id, 
                                            u'TOKEN_NAME' : project_name + ' #' + str(token_id) }})
        token_rarity_score = 0
        token_ranking = 0
        this_token_trait = []
        each_trait_score = {}
        
        for y in range(starting_count_y,nft_metadata_len):
            this_trait_rarity_score = 0
            temp_scoring = 0
            if thematic_match and y == themematic_match_position:
                #all_sets = []
                if target_project[u'isList']:
                    temp_scoring = 0
                    
                    for each_theme in nft_metadata[x][y]:
                        if normalize_trait:
                            number_of_category = len(all_traits[y][u'pvs'])
                            
                            token_rarity_score = token_rarity_score + (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                            this_trait_rarity_score = (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                            temp_scoring += this_trait_rarity_score
                        else:
                            token_rarity_score = token_rarity_score + 1/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                            this_trait_rarity_score = 1/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                            temp_scoring += this_trait_rarity_score

                elif target_project[u'thematic_key'] == "derivedPropDefs":
                        theme = nft_metadata[x][y][0]
                        matching_set = response_data[u'derivedPropDefs'][0][u'pvs']
                        for each_matching_set in matching_set:
                            if (theme == each_matching_set[0]):
                                
                                token_rarity_score = token_rarity_score + 1/(each_matching_set[1]/total_tokens_len)
                                this_trait_rarity_score = 1/(each_matching_set[1]/total_tokens_len)

            else:
                if target_project[u'itemToAvoid'] == None:
                    if isinstance(nft_metadata[x][y], list):
                        temp_scoring = 0
                        if len(nft_metadata[x][y]) == 0:
                            if normalize_trait:
                                
                                number_of_category = len(all_traits[y][u'pvs'])
                                
                                
                                token_rarity_score = token_rarity_score + (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][0][1]/total_tokens_len)
                                this_trait_rarity_score = (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][0][1]/total_tokens_len)
                                temp_scoring += this_trait_rarity_score
                            else:
                                token_rarity_score = token_rarity_score + 1/(all_traits[y][u'pvs'][0][1]/total_tokens_len)
                                temp_scoring += this_trait_rarity_score
                        else:
                            for each_theme in nft_metadata[x][y]:
                                if normalize_trait:
                                    number_of_category = len(all_traits[y][u'pvs'])
                                    
                                    token_rarity_score = token_rarity_score + (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                                    this_trait_rarity_score = (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                                    temp_scoring += this_trait_rarity_score
                                else:
                                    token_rarity_score = token_rarity_score + 1/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                                    this_trait_rarity_score = 1/(all_traits[y][u'pvs'][each_theme][1]/total_tokens_len)
                                    temp_scoring += this_trait_rarity_score
                    else:
                        if normalize_trait:
                            number_of_category = len(all_traits[y][u'pvs'])
                            
                            token_rarity_score = token_rarity_score + (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][nft_metadata[x][y]][1]/total_tokens_len)
                            this_trait_rarity_score = (constant_number/(number_of_traits_types * number_of_category))/(all_traits[y][u'pvs'][nft_metadata[x][y]][1]/total_tokens_len)
                        else:
                            token_rarity_score = token_rarity_score + 1/(all_traits[y][u'pvs'][nft_metadata[x][y]][1]/total_tokens_len)
                            this_trait_rarity_score =  1/(all_traits[y][u'pvs'][nft_metadata[x][y]][1]/total_tokens_len)


                    

                elif y == target_project[u'itemToAvoid']:
                    token_rarity_score = token_rarity_score

            if isinstance(nft_metadata[x][y], list):
                
                for each_theme in nft_metadata[x][y]:
                    this_token_trait.append({u'node' : {u'traitType' : all_traits[y][u'name'], u'value' : all_traits[y][u'pvs'][each_theme][0]}})
                    
                each_trait_score.update({all_traits[y][u'name'] : temp_scoring})
            else:
                this_token_trait.append({u'node' : {u'traitType' : all_traits[y][u'name'], u'value' : all_traits[y][u'pvs'][nft_metadata[x][y]][0]}})
                each_trait_score.update({all_traits[y][u'name'] : this_trait_rarity_score})
        

        rarity_table.update({str(token_id) : float(token_rarity_score)})
        metadata_to_save[token_id].update({u'nft_traits' : this_token_trait})
        metadata_scoring[token_id].update(each_trait_score)
    
    sorted_rarity_table = sorted(rarity_table.items(), key = lambda item : item[1],reverse=True)


    
    rarity_table_upload = {}
    count = 1
    for each_item in range(0,len(sorted_rarity_table)):
        rarity_table_upload.update({str(sorted_rarity_table[each_item][0]) : {"rank" : count, "rarity_score" : float(sorted_rarity_table[each_item][1])}})
        metadata_to_save[str(sorted_rarity_table[each_item][0])].update({"rank" : count, "rarity_score" : float(sorted_rarity_table[each_item][1])})
        metadata_scoring[str(sorted_rarity_table[each_item][0])].update({ "RARITY_SCORE" : float(sorted_rarity_table[each_item][1]),"Rank" : count})

        count = count + 1


    scoring_csv = []

    

    for each_token in metadata_scoring:
        this_row = []
        for each_col in metadata_scoring[each_token]:
            this_row.append(metadata_scoring[each_token][each_col])
        scoring_csv.append(this_row)
    

    sorted_scoring_csv = sorted(scoring_csv, key = lambda item : item[len(item)-1],reverse=False)

    #Create Header
    header_row = []
    for each_col in metadata_scoring["1"]:
        header_row.append(each_col)
    
        
    with open(file_name, 'w') as fp:
        json.dump(rarity_table_upload, fp)
    
    pprint(metadata_to_save["131"])
    with open(metadata_file_name, 'w') as fp:
        json.dump(metadata_to_save, fp)


    with open(metadata_scoring_file_name, 'w') as fp:
        json.dump(metadata_scoring, fp)

    with open(metadata_scoring_csv_file_name, 'w') as f: 
        write = csv.writer(f) 
        write.writerow(header_row) 
        write.writerows(sorted_scoring_csv) 
        
    
    print("--- %s seconds TO Load ---" % (time.time() - start_time))

