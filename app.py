from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

import pandas as pd
import networkx as nx
import os
import random
import pickle

root_path = os.getcwd()
salad_flavor_data = pd.read_pickle(os.path.join(root_path, 'data/salad_flavor_data.pickle'))
# stir_fry_flavor_data = pd.read_pickle(os.path.join(root_path, 'data/stir_fry_flavor_data.pickle'))
stir_fry_flavor_data = pd.read_pickle(os.path.join(root_path, 'data/stir_fry_flavor_data_with_umbrella.pickle'))

@app.route('/')
def root():
    return redirect(url_for('stir_fry_index'))

@app.route('/salad')
def salad_index():
    return render_template('salad-index.html')

@app.route('/get-salad-ingredients', methods=['GET'])
def get_salad_ingredients():
    salad_ingredients = [
        {
            col_name: row[col_name]
        for col_name in salad_flavor_data.columns.tolist()}
    for i, row in salad_flavor_data.iterrows()]
    # print(salad_flavor_data.columns.tolist())
    return jsonify(salad_ingredients)

@app.route('/generate-salad', methods=['POST'])
def generate_salad():
    # print('GENERATING SALAD')
    content = request.get_json()
    locked_names = content['locked']
    present_names = content['present']

    salad_data = salad_flavor_data[salad_flavor_data['name'].isin(present_names)].copy()
    salad_data.reset_index(inplace=True)

    locked = salad_data[salad_data['name'].isin(locked_names)]
    locked_greens = locked[locked['salad_green'] == 'y']
    locked_extras = locked[locked['salad_extra'] == 'y']
    locked_dressing_oils = locked[locked['salad_dressing_oil'] == 'y']
    locked_dressing_vinegars = locked[locked['salad_dressing_vinegar'] == 'y']
    locked_dressing_salts = locked[locked['salad_dressing_salt'] == 'y']
    locked_dressing_peppers = locked[locked['salad_dressing_pepper'] == 'y']

    the_rest = salad_data[~salad_data['name'].isin(locked_names)]
    the_rest_greens = the_rest[the_rest['salad_green'] == 'y']
    the_rest_extras = the_rest[the_rest['salad_extra'] == 'y']
    the_rest_dressing_oils = the_rest[the_rest['salad_dressing_oil'] == 'y']
    the_rest_dressing_vinegars = the_rest[the_rest['salad_dressing_vinegar'] == 'y']
    the_rest_dressing_salts = the_rest[the_rest['salad_dressing_salt'] == 'y']
    the_rest_dressing_peppers = the_rest[the_rest['salad_dressing_pepper'] == 'y']

    n_gen_greens_min = max(2-len(locked_greens), 0)
    n_gen_greens_max = max(3-len(locked_greens), 0)

    n_gen_extras_min = max(2-len(locked_extras), 0)
    n_gen_extras_max = max(4-len(locked_extras), 0)

    n_iterations = len(present_names)*3
    keep_iterating = True

    n_attempts_before_deciding = 10
    n_attempts_before_giving_up = 5

    scoring_method = 'tbd'
    top_score = 0
    for iteration in range(n_iterations):
        # n_subgraphs = 2
        connection_attempt = 1
        while True: # keep shuffling until you get a well connected graph

            # don't try to select fewer than 0, and don't try to select more than there are ingredients left
            n_gen_greens = min(random.randrange(n_gen_greens_min, n_gen_greens_max+1), len(the_rest_greens))
            n_gen_extras = min(random.randrange(n_gen_extras_min, n_gen_extras_max+1), len(the_rest_extras))
            n_gen_dressing_oils = min(max(1-len(locked_dressing_oils), 0), len(the_rest_dressing_oils))
            n_gen_dressing_vinegars = min(max(1-len(locked_dressing_vinegars), 0), len(the_rest_dressing_vinegars))
            n_gen_dressing_salts = min(max(1-len(locked_dressing_salts), 0), len(the_rest_dressing_salts))
            n_gen_dressing_peppers = min(max(1-len(locked_dressing_peppers), 0), len(the_rest_dressing_peppers))

            selected_greens = locked_greens.append(the_rest_greens.sample(n_gen_greens))
            selected_extras = locked_extras.append(the_rest_extras.sample(n_gen_extras))
            selected_dressing_oils = locked_dressing_oils.append(the_rest_dressing_oils.sample(n_gen_dressing_oils))
            selected_dressing_vinegars = locked_dressing_vinegars.append(the_rest_dressing_vinegars.sample(n_gen_dressing_vinegars))
            selected_dressing_salts = locked_dressing_salts.append(the_rest_dressing_salts.sample(n_gen_dressing_salts))
            selected_dressing_peppers = locked_dressing_peppers.append(the_rest_dressing_peppers.sample(n_gen_dressing_peppers))
            selected_ingredients = selected_greens.append(selected_extras).append(selected_dressing_oils).append(selected_dressing_vinegars).append(selected_dressing_salts).append(selected_dressing_peppers)
            selected_names = selected_ingredients['name'].tolist()

            lower_category_pairs = []
            lower_direct_pairs = []
            upper_category_pairs = []
            upper_direct_pairs = []
            lower_clashing_pairs = []
            upper_clashing_pairs = []

            # finicky but pretty fast
            for i, col_name in enumerate(selected_names):
                for j, row_name in enumerate(selected_names[i+1:]):
                    connection = selected_ingredients[col_name].tolist()[i+1+j] # this is what is finicky
                    if connection == 'c':
                        lower_category_pairs.append((col_name, row_name,))
                    elif connection == 'd':
                        lower_direct_pairs.append((col_name, row_name,))
                    elif connection == 'C':
                        upper_category_pairs.append((col_name, row_name,))
                    elif connection == 'D':
                        upper_direct_pairs.append((col_name, row_name,))
                    elif connection == 'n':
                        lower_clashing_pairs.append((col_name, row_name,))
                    elif connection == 'N':
                        upper_clashing_pairs.append((col_name, row_name,))
            lower_pairs = lower_category_pairs + lower_direct_pairs
            upper_pairs = upper_category_pairs + upper_direct_pairs
            all_pairs = lower_pairs + upper_pairs
            all_clashing_pairs = lower_clashing_pairs + upper_clashing_pairs

            selected_g = nx.Graph()
            selected_g.add_nodes_from(selected_names)
            selected_g.add_edges_from(lower_category_pairs, length=2)
            selected_g.add_edges_from(lower_direct_pairs, length=1.5)
            selected_g.add_edges_from(upper_category_pairs, length=1.2)
            selected_g.add_edges_from(upper_direct_pairs, length=1)
            connected_components = list(nx.connected_components(selected_g))

            if scoring_method == 'tbd':
                if len(connected_components) == 1:
                    # print('Scoring method set to "connected"')
                    scoring_method = 'connected'
                    break
                elif connection_attempt >= n_attempts_before_deciding:
                    print('Scoring method set to "disconnected"')
                    scoring_method = 'disconnected'
                    break
            elif scoring_method == 'connected':
                if len(connected_components) == 1:
                    break
                elif connection_attempt >= n_attempts_before_giving_up:
                    print('Giving up')
                    keep_iterating = False
                    break
            elif scoring_method == 'disconnected':
                # print('SCORING METHOD DISCONNECTED')
                break

            connection_attempt += 1

        # print('DONE WITH CONNECTION LOOP HOPEFULLY')
        if not keep_iterating:
            break # Just go with the best iteration so far (rather than slogging through disconnected graphs)

        score = 0

        if scoring_method == 'connected':
            # CONNECTED PAIRING BONUS ============================================================================================
            # ranges from roughly (0 to 1) * 3, tho could be a lil over or under that range
            average_shortest_path_length = nx.average_shortest_path_length(selected_g, weight='weight')
            # print('AVERAGE SHORTEST PATH LENGTH', average_shortest_path_length)
            average_shortest_path_score = 1 / average_shortest_path_length * 2.5 - 1.1
            # print('AVERAGE SHORTEST PATH SCORE', average_shortest_path_score)
            score += average_shortest_path_score * 3
        else:
            # DISCONNECTED PAIRING BONUS ============================================================================================
            # not really sure how this sranges. hopefully (0 - 1) * 3? Hard to test.
            largest_cc = max(connected_components, key=len)
            # print('CONNECTED COMPONENTS', connected_components)
            # print('LARGEST CC', largest_cc)
            largest_subgraph = selected_g.subgraph(largest_cc) # .copy()?
            largest_subgraph_g = nx.Graph(largest_subgraph)
            average_shortest_path_length = nx.average_shortest_path_length(largest_subgraph_g, weight='weight')
            average_shortest_path_score = 1 / average_shortest_path_length * 2.5 - 1.1
            # print('DISCONNECTED AVERAGE SHORTEST PATH SCORE', average_shortest_path_score)
            score += average_shortest_path_score * 3

    # important but easy to avoid, so not weighted too heavily
    # CLASH PENALTY ====================================================================================================
        # ranges from roughly (0 to 1) * -1.5
        all_clashing_pairs_score = len(all_clashing_pairs)
        score += all_clashing_pairs_score * -1.5

    # FLAVOR BALANCE BONUS =============================================================================================
        # ranges from roughly (0 to 1) * 1
        n_sweet_lower = (selected_ingredients['sweet'] == 'y').sum()
        n_sweet_upper = (selected_ingredients['sweet'] == 'Y').sum()
        n_salty_lower = (selected_ingredients['salty'] == 'y').sum()
        n_salty_upper = (selected_ingredients['salty'] == 'Y').sum()
        n_sour_lower = (selected_ingredients['sour'] == 'y').sum()
        n_sour_upper = (selected_ingredients['sour'] == 'Y').sum()
        n_savory_lower = (selected_ingredients['savory'] == 'y').sum()
        n_savory_upper = (selected_ingredients['savory'] == 'Y').sum()
        n_bitter_lower = (selected_ingredients['bitter'] == 'y').sum()
        n_bitter_upper = (selected_ingredients['bitter'] == 'Y').sum()
        n_spicy_lower = (selected_ingredients['spicy'] == 'y').sum()
        n_spicy_upper = (selected_ingredients['spicy'] == 'Y').sum()

        # # each varies from roughly .5 to 1
        # sweet_score = (n_sweet_lower/2 + n_sweet_upper)/5
        # salty_score = (n_salty_lower/2 + n_salty_upper)*2/5
        # sour_score = (n_sour_lower/2 + n_sour_upper)*2/5
        # savory_score = (n_savory_lower/2 + n_savory_upper)*3/5
        # bitter_score = (n_bitter_lower/2 + n_bitter_upper)*3/5
        # spicy_score = (n_spicy_lower/2 + n_spicy_upper)*2/5
        #
        # flavor_balance_score = 5 / (1 + abs(1-sweet_score) + abs(1-salty_score) + abs(1-sour_score) + abs(1-savory_score) + abs(1-spicy_score)) - 1.2
        # score += flavor_balance_score

        sweet_score = min(n_sweet_lower/2 + n_sweet_upper, 1)
        salty_score = min(n_salty_lower/2 + n_salty_upper, 1)
        sour_score = min(n_sour_lower/2 + n_sour_upper, 1)
        savory_score = min(n_savory_lower/2 + n_savory_upper, 1)
        bitter_score = min(n_bitter_lower/2 + n_bitter_upper, 1)
        spicy_score = min(n_spicy_lower/2 + n_spicy_upper, 1)

        flavor_score = 0
        flavor_score += sweet_score*3 # rly want something sweet in there
        flavor_score += salty_score*.5 # can always use salt
        flavor_score += sour_score*2 # like me some sour
        flavor_score += savory_score*2 # like me some savory
        flavor_score += bitter_score # idk
        flavor_score += spicy_score*.5 # can be nice I guess?
        flavor_score = flavor_score / 2 - 3.5

        # print('FLAVOR SCORE', flavor_score)
        score += flavor_score

    # TEXTURE BALANCE BONUS ============================================================================================
        # ranges from roughly (0 to 1) * .75
        n_crunchy_lower = (selected_ingredients['salad_crunchy'] == 'y').sum()
        n_crunchy_upper = (selected_ingredients['salad_crunchy'] == 'Y').sum()
        n_chewy_lower = (selected_ingredients['salad_chewy'] == 'y').sum()
        n_chewy_upper = (selected_ingredients['salad_chewy'] == 'Y').sum()
        n_juicy_lower = (selected_ingredients['salad_juicy'] == 'y').sum()
        n_juicy_upper = (selected_ingredients['salad_juicy'] == 'Y').sum()

        # # each ranges from roughly 0 to 1
        # crunchy_score = (n_crunchy_lower/2 + n_crunchy_upper)/3
        # chewy_score = (n_chewy_lower/2 + n_chewy_upper)
        # juicy_score = (n_juicy_lower/2 + n_juicy_upper)/3
        #
        # texture_balance_score = 5 / (1 + abs(1-crunchy_score) + abs(1-chewy_score) + abs(1-juicy_score)) - 1.25
        # score += texture_balance_score * .75

        crunchy_score = min(n_crunchy_lower/2 + n_crunchy_upper, 1)
        chewy_score = min(n_chewy_lower/2 + n_chewy_upper, 1)
        juicy_score = min(n_juicy_lower/2 + n_juicy_upper, 1)

        texture_score = 0
        texture_score += crunchy_score # not hard to get
        texture_score += chewy_score # nice but not essential
        texture_score += juicy_score*2 # really into juicy in a salad
        texture_score = texture_score / 3.5 - .1

        # print('TEXTURE SCORE', texture_score)
        score += texture_score * .75

    # # will bias toward larger salads, slightly
    # # seems like it's hard to balance food groups on top of everything else. pity the scores aren't more independent
    # # FOOD GROUP BALANCE BONUS =========================================================================================
    #     # ranges from roughly (0 to 1) * 2
    #     n_fruit = (selected_ingredients['fruit'] == 'y').sum()
    #     n_veg = (selected_ingredients['veg'] == 'y').sum()
    #     n_protein = (selected_ingredients['protein'] == 'y').sum()
    #
    #     # /2 for steep diminishing returns (?)
    #     fruit_score = (n_fruit/2)**.5
    #     veg_score = (n_veg/2)**.5
    #     protein_score = (n_protein/2)**.5 #(0->0, 1->1, 4->2, 9->3)
    #     food_group_balance_score = (3*fruit_score + veg_score + 2*protein_score) * .22 - .33
    #     score += food_group_balance_score * 2

        # FOOD GROUP BONUS ====================================================
        if 'y' in selected_ingredients['fruit'].values:
            fruit_score = .33
        else:
            fruit_score = 0
        if 'y' in selected_ingredients['veg'].values:
            veg_score = .33
        else:
            veg_score = 0
        if 'y' in selected_ingredients['protein'].values:
            protein_score = .33
        else:
            protein_score = 0
        food_group_score = fruit_score + veg_score + protein_score
        score += food_group_score * 2

        if score > top_score:
            top_selected_ingredients = selected_ingredients
            top_pairing_bonus = average_shortest_path_score * 3
            top_clash_penalty = all_clashing_pairs_score * -1.5
            top_flavor_bonus = flavor_score
            top_texture_bonus = texture_score * .75
            top_food_group_bonus = food_group_score * 2
            top_score = score

    data = {
        'present_names': present_names,
        'selected_names': top_selected_ingredients['name'].tolist(),
        'locked_names': locked_names,
        'generated_names': top_selected_ingredients['name'][~top_selected_ingredients['name'].isin(locked_names)].tolist(),
        'pairing_bonus': top_pairing_bonus,
        'clash_penalty': top_clash_penalty,
        'flavor_bonus': top_flavor_bonus,
        'texture_bonus': top_texture_bonus,
        'food_group_bonus': top_food_group_bonus,
        'score': top_score
    }
    return jsonify(data)

@app.route('/stir-fry')
def stir_fry_index():
    return render_template('stir-fry-index.html')

@app.route('/get-stir-fry-ingredients', methods=['GET'])
def get_stir_fry_ingredients():
    stir_fry_ingredients = [
        {
            col_name: row[col_name]
        for col_name in stir_fry_flavor_data.columns.tolist()}
    for i, row in stir_fry_flavor_data.iterrows()]
    return jsonify(stir_fry_ingredients)

@app.route('/generate-stir-fry', methods=['POST'])
def generate_stir_fry():
# TODO: account for if connected subgraph is impossible
    content = request.get_json()
    locked_names = content['locked']
    present_names = content['present']

    stir_fry_data = stir_fry_flavor_data[stir_fry_flavor_data['name'].isin(present_names)].copy()
    # stir_fry_data.reset_index(inplace=True)

    locked = stir_fry_data[stir_fry_data['name'].isin(locked_names)]
    locked_fat_oils = locked[locked['stir_fry_fat_oil'] == 'y']
    locked_salts = locked[locked['stir_fry_salt'] == 'y']
    locked_other_flavorings = locked[(locked['stir_fry_flavoring'] == 'y') & (locked['stir_fry_salt'] != 'y')]
    locked_foodstuffs = locked[(locked['stir_fry_fat_oil'] != 'y') & (locked['stir_fry_salt'] != 'y') & (locked['stir_fry_flavoring'] != 'y')]

    the_rest = stir_fry_data[~stir_fry_data['name'].isin(locked['name'])]
    the_rest_fat_oils = the_rest[the_rest['stir_fry_fat_oil'] == 'y']
    the_rest_salts = the_rest[the_rest['stir_fry_salt'] == 'y']
    the_rest_other_flavorings = the_rest[(the_rest['stir_fry_flavoring'] == 'y') & (the_rest['stir_fry_salt'] != 'y')]
    the_rest_foodstuffs = the_rest[(the_rest['stir_fry_fat_oil'] != 'y') & (the_rest['stir_fry_salt'] != 'y') & (the_rest['stir_fry_flavoring'] != 'y')]

    n_gen_salts = max(1 - len(locked_salts), 0)
    n_gen_fat_oils = max(1 - len(locked_fat_oils), 0)
    n_gen_other_flavorings_min = max(1 - len(locked_other_flavorings), 0)
    n_gen_other_flavorings_max = max(3 - len(locked_other_flavorings), 0)
    n_gen_foodstuffs_min = max(3 - len(locked_foodstuffs), 0)
    n_gen_foodstuffs_max = max(7 - len(locked_foodstuffs), 0)

    n_iterations = len(present_names)*3
    # n_iterations = 100
    keep_iterating = True

    n_attempts_before_deciding = 10
    n_attempts_before_giving_up = 5

    scoring_method = 'tbd'
    top_score = 0

    for iteration in range(n_iterations):
        # print('ITERATION START')
        # n_subgraphs = 2
        connection_attempt = 1
        while True:
            # print('TRYING TO CONNECT')
            n_gen_other_flavorings = min(random.randrange(n_gen_other_flavorings_min, n_gen_other_flavorings_max+1), len(the_rest_other_flavorings))
            n_gen_foodstuffs = min(random.randrange(n_gen_foodstuffs_min, n_gen_foodstuffs_max+1), len(the_rest_foodstuffs))

            selected_salts = locked_salts.append(the_rest_salts.sample(n_gen_salts))
            selected_fat_oils = locked_fat_oils.append(the_rest_fat_oils.sample(n_gen_fat_oils))
            selected_other_flavorings = locked_other_flavorings.append(the_rest_other_flavorings.sample(n_gen_other_flavorings))
            selected_foodstuffs = locked_foodstuffs.append(the_rest_foodstuffs.sample(n_gen_foodstuffs))
            selected_ingredients = selected_salts.append(selected_fat_oils).append(selected_other_flavorings).append(selected_foodstuffs)
            selected_names = selected_ingredients['name'].values.tolist()
            # print('SELECTED NAMES', selected_names)

            # lower_category_pairs = []
            # lower_direct_pairs = []
            # upper_category_pairs = []
            # upper_direct_pairs = []
            #
            # # finicky but pretty fast
            # for i, col_name in enumerate(selected_names):
            #     for j, row_name in enumerate(selected_names[i+1:]):
            #         connection = selected_ingredients[col_name].tolist()[i+1+j] # this is what is finicky
            #         print('CONNECTION', connection)
            #         if connection == 'c':
            #             lower_category_pairs.append((col_name, row_name,))
            #         elif connection == 'd':
            #             lower_direct_pairs.append((col_name, row_name,))
            #         elif connection == 'C':
            #             upper_category_pairs.append((col_name, row_name,))
            #         elif connection == 'D':
            #             upper_direct_pairs.append((col_name, row_name,))
            # lower_pairs = lower_category_pairs + lower_direct_pairs
            # upper_pairs = upper_category_pairs + upper_direct_pairs
            # all_pairs = lower_pairs + upper_pairs
            # print('ALL PAIRS', all_pairs)
            # selected_g = nx.Graph()
            # selected_g.add_nodes_from(selected_names)
            # selected_g.add_edges_from(lower_category_pairs, length=2)
            # selected_g.add_edges_from(lower_direct_pairs, length=1.5)
            # selected_g.add_edges_from(upper_category_pairs, length=1.2)
            # selected_g.add_edges_from(upper_direct_pairs, length=1)
            # connected_components = list(nx.connected_components(selected_g))

            connections = []
            weighted_edges = []

            for i_1, name_1 in enumerate(selected_names[:-1]):
                # print('NAME 1', name_1)
                for i_2, name_2 in enumerate(selected_names[i_1+1:], i_1+1):
                    # print('NAME 2', name_2)
                    # print('STIR FRY FLAVOR DATA INDEX', stir_fry_flavor_data.index)
                    # print('SELECTED INGREDIENTS NAME 1', selected_ingredients[name_1], type(selected_ingredients[name_1]), list(selected_ingredients[name_1]))
                    connection = selected_ingredients[name_1][name_2]
                    if connection[0] != '_':
                        if connection[0] == 'c':
                            pairs_with_demerit = .8
                        elif connection[0] == 'd':
                            pairs_with_demerit = .6666
                        elif connection[0] == 'C':
                            pairs_with_demerit = .5333
                        elif connection[0] == 'D':
                            pairs_with_demerit = .4
                        else:
                            print('OH NO! BAD PAIRING VALUE.')

                        if connection[1] == '_':
                            strength_demerit = .2
                        elif connection[1] == 's':
                            strength_demerit = .15
                        elif connection[1] == 'S':
                            strength_demerit = .1
                        else:
                            print('OH NO! BAD STRENGTH VALUE.')


                        connection_weight = pairs_with_demerit + strength_demerit
                        weighted_edges.append((name_1, name_2, connection_weight))
                        connections.append((name_1, name_2, connection))

            selected_g = nx.Graph()
            selected_g.add_nodes_from(selected_names)
            selected_g.add_weighted_edges_from(weighted_edges)
            connected_components = list(nx.connected_components(selected_g))

            if scoring_method == 'tbd':
                if len(connected_components) == 1:
                    # print('Scoring method set to "connected"')
                    scoring_method = 'connected'
                    break
                elif connection_attempt >= n_attempts_before_deciding:
                    print('Scoring method set to "disconnected"')
                    scoring_method = 'disconnected'
                    break
            elif scoring_method == 'connected':
                if len(connected_components) == 1:
                    break
                elif connection_attempt >= n_attempts_before_giving_up:
                    print('Giving up')
                    keep_iterating = False
                    break
            elif scoring_method == 'disconnected':
                # print('SCORING METHOD DISCONNECTED')
                break

            connection_attempt += 1

        # print('DONE WITH CONNECTION LOOP HOPEFULLY')
        if not keep_iterating:
            break # Just go with the best iteration so far (rather than slogging through disconnected graphs)

        score = 0

    # TODO test to normalize these scores (done, I think?)
        if scoring_method == 'connected':
            # CONNECTED PAIRING BONUS ============================================================================================
            # ranges from roughly (0 to 1) * 3, tho could be a lil over or under that range
            average_shortest_path_length = nx.average_shortest_path_length(selected_g, weight='weight')
            # print('AVERAGE SHORTEST PATH LENGTH', average_shortest_path_length)
            average_shortest_path_score = 1 / average_shortest_path_length * 2 - 1.3
            # print('AVERAGE SHORTEST PATH SCORE', average_shortest_path_score)
            score += average_shortest_path_score * 3
        else:
            # DISCONNECTED PAIRING BONUS ============================================================================================
            # not really sure how this sranges. hopefully (0 - 1) * 3? Hard to test.
            largest_cc = max(connected_components, key=len)
            # print('CONNECTED COMPONENTS', connected_components)
            # print('LARGEST CC', largest_cc)
            largest_subgraph = selected_g.subgraph(largest_cc) # .copy()?
            largest_subgraph_g = nx.Graph(largest_subgraph)
            average_shortest_path_length = nx.average_shortest_path_length(largest_subgraph_g, weight='weight')
            average_shortest_path_score = 1 / average_shortest_path_length * 2 - 1.3
            # print('DISCONNECTED AVERAGE SHORTEST PATH SCORE', average_shortest_path_score)
            score += average_shortest_path_score * 3

    # FLAVOR BALANCE BONUS =============================================================================================
    # ranges from roughly (0 to 1) * 1 (could be a lil over/under)
        n_sweet_lower = (selected_ingredients['sweet'] == 'y').sum()
        n_sweet_upper = (selected_ingredients['sweet'] == 'Y').sum()
        n_salty_lower = (selected_ingredients['salty'] == 'y').sum()
        n_salty_upper = (selected_ingredients['salty'] == 'Y').sum()
        n_sour_lower = (selected_ingredients['sour'] == 'y').sum()
        n_sour_upper = (selected_ingredients['sour'] == 'Y').sum()
        n_savory_lower = (selected_ingredients['savory'] == 'y').sum()
        n_savory_upper = (selected_ingredients['savory'] == 'Y').sum()
        n_bitter_lower = (selected_ingredients['bitter'] == 'y').sum()
        n_bitter_upper = (selected_ingredients['bitter'] == 'Y').sum()
        n_spicy_lower = (selected_ingredients['spicy'] == 'y').sum()
        n_spicy_upper = (selected_ingredients['spicy'] == 'Y').sum()

        sweet_score = min(n_sweet_lower/2 + n_sweet_upper, 1)
        salty_score = min(n_salty_lower/2 + n_salty_upper, 1)
        sour_score = min(n_sour_lower/2 + n_sour_upper, 1)
        savory_score = min(n_savory_lower/2 + n_savory_upper, 1)
        bitter_score = min(n_bitter_lower/2 + n_bitter_upper, 1)
        spicy_score = min(n_spicy_lower/2 + n_spicy_upper, 1)

        flavor_score = 0
        flavor_score += sweet_score*3 # rly want something sweet in there
        flavor_score += salty_score*.5 # can always use salt
        flavor_score += sour_score*2 # like me some sour
        flavor_score += savory_score*3 # LOVE me some savory
        flavor_score += bitter_score # idk
        flavor_score += spicy_score*2 # can be nice
        flavor_score = flavor_score * .15 - .75

        # print('FLAVOR BALANCE SCORE', flavor_balance_score)
        score += flavor_score

        # FOOD GROUPS BONUS ==========================================================================================
        if 'y' in selected_ingredients['stir_fry_protein'].values:
            protein_score = .5
        else:
            protein_score = 0

        if 'y' in selected_ingredients['stir_fry_fruit'].values:
            fruit_score = .5
        else:
            fruit_score = 0

        food_group_score = protein_score + fruit_score
        # print('PROTEIN FRUIT', protein_score, fruit_score)
        score += food_group_score


        if score > top_score:
            top_selected_ingredients = selected_ingredients
            top_pairing_bonus = average_shortest_path_score
            top_flavor_bonus = flavor_score
            top_food_group_bonus = food_group_score
            top_score = score
        # print()

    # print('PAIRING BONUS', top_pairing_bonus)
    # print('FLAVOR BALANCE BONUS', top_flavor_bonus)
    # print('FOOD GROUP BONUS', top_food_group_bonus)
    # print('SCORE', top_score)
    data = {
        'present_names': present_names,
        'selected_names': top_selected_ingredients['name'].tolist(),
        'locked_names': locked_names,
        'generated_names': top_selected_ingredients['name'][~top_selected_ingredients['name'].isin(locked_names)].tolist(),
        'pairing_bonus': top_pairing_bonus,
        'flavor_bonus': top_flavor_bonus,
        'food_group_bonus': top_food_group_bonus,
        'score': top_score
    }
    # print(data)
    return(jsonify(data))

# BLACK MAGIC SETUP ============================================================
salt_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_salt'] == 'y']['name'])
fat_oil_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_fat_oil'] == 'y']['name'])
other_flavoring_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_flavoring'] == 'y']['name']) - salt_set
foodstuff_set = set(stir_fry_flavor_data['name']) - salt_set - fat_oil_set - other_flavoring_set
mushroom_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_mushroom'] == 'y']['name'])
bean_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_protein_bean'] == 'y'])
grain_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_grain'] == 'y'])

n_salts = 1
n_fat_oils = 1
n_other_flavorings_min = 1
n_other_flavorings_max = 3
n_foodstuffs_min = 3
n_foodstuffs_max = 7
# n_mushrooms_min = 0
mushrooms_cap = 1 # possible to have more than this, if there are locked mushrooms (I don't update sets after locked/gen is established)
n_beans_max = 1
n_grains_max = 1
# n_beans_min = 0
# n_beans_max = 2
# n_grains_min = 0
# n_grains_max = 2

reasonable_clique_upper = pd.read_pickle(os.path.join(root_path, 'data/stir_fry_reasonable_clique_upper.pickle'))

average_score_for_length = dict(reasonable_clique_upper.groupby('reasonable_length')['score'].mean())
def get_average_score(length):
    if length >= 2:
        return average_score_for_length[length]
    else:
        return 0

def get_weak_score(strong):
    if strong == 'Y':
        return 1
    elif strong == 'y':
        return 3
    else:
        return 9
# ALTERS SHARED DATA
stir_fry_flavor_data['weak_score'] = stir_fry_flavor_data['strong'].apply(get_weak_score)

with open(os.path.join(root_path, 'data/stir_fry_shortest_path_lengths.pickle'), 'rb') as handle:
    stir_fry_shortest_path_lengths = pickle.load(handle)

def get_sort_key(length_tuple):
    return length_tuple[1]

def n_possible_edges(n_nodes):
    return int((n_nodes*(n_nodes-1)) / 2)

def get_first_name_in_set(sorted_tuples, food_set):
    for sorted_tuple in sorted_tuples:
        if sorted_tuple[0] in food_set:
            return sorted_tuple[0]

@app.route('/generate-stir-fry-black-magic', methods=['POST'])
def generate_stir_fry_black_magic():
# TODO: account for if connected subgraph is impossible
    content = request.get_json()
    locked_names = content['locked']
    present_names = content['present']

    # stir_fry_data = stir_fry_flavor_data[stir_fry_flavor_data['name'].isin(present_names)].copy()
    # n_present = len(present_names)
    present = stir_fry_flavor_data[stir_fry_flavor_data['name'].isin(present_names)].copy()
    present_set = set(present_names)
    present_strong_set = set(present[present['strong'].isin(['Y', 'y'])]['name'])
    not_present_set = set(stir_fry_flavor_data['name']) - present_set
    # present_shortest_path_lengths = {key: stir_fry_shortest_path_lengths[key] for key in stir_fry_shortest_path_lengths if key in present_set}

    # n_locked = len(locked_names)
    locked = present[present['name'].isin(locked_names)]
    locked_set = set(locked_names)
    locked_fat_oils = locked[locked['stir_fry_fat_oil'] == 'y']
    locked_salts = locked[locked['stir_fry_salt'] == 'y']
    locked_other_flavorings = locked[(locked['stir_fry_flavoring'] == 'y') & (locked['stir_fry_salt'] != 'y')]
    locked_foodstuffs = locked[(locked['stir_fry_fat_oil'] != 'y') & (locked['stir_fry_salt'] != 'y') & (locked['stir_fry_flavoring'] != 'y')]
    locked_fat_oils_set = set(locked_fat_oils['name'])
    locked_salts_set = set(locked_salts['name'])
    locked_other_flavorings_set = set(locked_other_flavorings['name'])
    locked_foodstuffs_set = set(locked_foodstuffs['name'])

    the_rest = present[~present['name'].isin(locked['name'])]
    the_rest_set = present_set - locked_set
    the_rest_fat_oils = the_rest[the_rest['stir_fry_fat_oil'] == 'y']
    the_rest_salts = the_rest[the_rest['stir_fry_salt'] == 'y']
    the_rest_other_flavorings = the_rest[(the_rest['stir_fry_flavoring'] == 'y') & (the_rest['stir_fry_salt'] != 'y')]
    the_rest_foodstuffs = the_rest[(the_rest['stir_fry_fat_oil'] != 'y') & (the_rest['stir_fry_salt'] != 'y') & (the_rest['stir_fry_flavoring'] != 'y')]
    the_rest_fat_oils_set = set(the_rest_fat_oils['name'])
    the_rest_salts_set = set(the_rest_salts['name'])
    the_rest_other_flavorings_set = set(the_rest_other_flavorings['name'])
    the_rest_foodstuffs_set = set(the_rest_foodstuffs['name'])

    # Are these being used?
    # the_rest_weak = present[~present['strong'].isin(['y', 'Y'])]
    # the_rest_weak_set = set(the_rest_weak['name'])
    # the_rest_weak_fat_oils = the_rest_weak[the_rest_weak['stir_fry_fat_oil'] == 'y']
    # the_rest_weak_salts = the_rest_weak[the_rest_weak['stir_fry_salt'] == 'y']
    # the_rest_weak_other_flavorings = the_rest_weak[(the_rest_weak['stir_fry_flavoring'] == 'y') & (the_rest_weak['stir_fry_salt'] != 'y')]
    # the_rest_weak_foodstuffs = the_rest_weak[(the_rest_weak['stir_fry_fat_oil'] != 'y') & (the_rest_weak['stir_fry_salt'] != 'y') & (the_rest_weak['stir_fry_flavoring'] != 'y')]

    n_gen_salts = max(n_salts - len(locked_salts), 0)
    n_gen_fat_oils = max(n_fat_oils - len(locked_fat_oils), 0)
    n_gen_other_flavorings_min = max(n_other_flavorings_min - len(locked_other_flavorings), 0)
    n_gen_other_flavorings_max = max(n_other_flavorings_max - len(locked_other_flavorings), 0) # yikes, I had this as min..
    n_gen_foodstuffs_min = max(n_foodstuffs_min - len(locked_foodstuffs), 0)
    n_gen_foodstuffs_max = max(n_foodstuffs_max - len(locked_foodstuffs), 0)

    n_salts_actual = max(n_salts, len(locked_salts))
    n_fat_oils_actual = max(n_fat_oils, len(locked_fat_oils))

    # not totally sure thesse are right (that both min and max are compared to locked)
    n_other_flavorings_min_actual = max(n_other_flavorings_min, len(locked_other_flavorings))
    n_other_flavorings_max_actual = max(n_other_flavorings_max, len(locked_other_flavorings))
    n_foodstuffs_min_actual = max(n_foodstuffs_min, len(locked_foodstuffs))
    n_foodstuffs_max_actual = max(n_foodstuffs_max, len(locked_foodstuffs))

    ok_cliques = reasonable_clique_upper[:1000].copy()

    # Requires local vars, so can't place this outside (?)
    def get_ok_data(row):
        updated_set = row['reasonable_set'] - not_present_set
        updated_salts_set = row['reasonable_salts_set'] - not_present_set
        updated_fat_oils_set = row['reasonable_fat_oils_set'] - not_present_set
        updated_other_flavorings_set = row['reasonable_other_flavorings_set'] - not_present_set
        updated_foodstuffs_set = row['reasonable_foodstuffs_set'] - not_present_set

        updated_n_salts = len(updated_salts_set)
        updated_n_fat_oils = len(updated_fat_oils_set)
        updated_n_other_flavorings = len(updated_other_flavorings_set)
        updated_n_foodstuffs = len(updated_foodstuffs_set)

        n_salts_so_far = len(updated_salts_set.union(locked_salts_set))
        n_salts_to_remove = max(n_salts_so_far - n_salts_actual, 0)
        salts_to_remove_from_set = updated_salts_set - locked_salts_set
        more_salts_to_remove_set = set(random.sample(salts_to_remove_from_set, n_salts_to_remove))

        n_fat_oils_so_far = len(updated_fat_oils_set.union(locked_fat_oils_set))
        n_fat_oils_to_remove = max(n_fat_oils_so_far - n_fat_oils_actual, 0)
        fat_oils_to_remove_from_set = updated_fat_oils_set - locked_fat_oils_set
        more_fat_oils_to_remove_set = set(random.sample(fat_oils_to_remove_from_set, n_fat_oils_to_remove))

        n_other_flavorings_so_far = len(updated_other_flavorings_set.union(locked_other_flavorings_set))
        n_other_flavorings_to_remove = max(n_other_flavorings_so_far - n_other_flavorings_max_actual, 0) # is this right?
        other_flavorings_to_remove_from_set = updated_other_flavorings_set - locked_other_flavorings_set
        more_other_flavorings_to_remove_set = set(random.sample(salts_to_remove_from_set, n_salts_to_remove))

        n_foodstuffs_so_far = len(updated_foodstuffs_set.union(locked_foodstuffs_set))
        n_foodstuffs_to_remove = max(n_foodstuffs_so_far - n_foodstuffs_max_actual, 0) # is this right? thinks so - it's keeping foodstuffs from above max
        foodstuffs_to_remove_from_set = updated_foodstuffs_set - locked_foodstuffs_set
        more_foodstuffs_to_remove_set = set(random.sample(foodstuffs_to_remove_from_set, n_foodstuffs_to_remove))

        ok_other_flavorings_set = updated_other_flavorings_set - more_other_flavorings_to_remove_set
        ok_foodstuffs_set = updated_foodstuffs_set - more_foodstuffs_to_remove_set

        ok_set = updated_set # not bothering w copy, for (negligible) speed reasons
        ok_set -= more_salts_to_remove_set
        ok_set -= more_fat_oils_to_remove_set
        ok_set -= more_other_flavorings_to_remove_set
        ok_set -= more_foodstuffs_to_remove_set

        ok_list = list(ok_set)
        ok_length = len(ok_list)
        ok_n_locked = len(ok_set.intersection(locked_set))
        ok_n_other_flavorings = len(ok_other_flavorings_set)
        ok_n_foodstuffs = len(ok_foodstuffs_set)

        old_score_bonus_factor = row['score']/get_average_score(row['reasonable_length']) # how above/below avg score was previously
        ok_score = get_average_score(ok_length)*old_score_bonus_factor
        ok_score_xtreme = ok_score**2 # skew scores way upward, for use as weights

        ok_strong_set = ok_set.intersection(present_strong_set)

        return (
            ok_set,
            ok_list,
            ok_length,
            ok_score,
            ok_score_xtreme,
            ok_n_locked,
            # ok_score_lockified,
            # ok_score_lockified_xtreme,
            ok_strong_set,
            ok_n_other_flavorings,
            ok_n_foodstuffs,
        )
    ok_data = ok_cliques.apply(get_ok_data, axis=1)

    ok_cliques['ok_set'] = ok_data.apply(lambda x: x[0])
    ok_cliques['ok_list'] = ok_data.apply(lambda x: x[1])
    ok_cliques['ok_length'] = ok_data.apply(lambda x: x[2])
    ok_cliques['ok_score'] = ok_data.apply(lambda x: x[3])
    ok_cliques['ok_score_xtreme'] = ok_data.apply(lambda x: x[4])
    ok_cliques['ok_n_locked'] = ok_data.apply(lambda x: x[5])
    # ok_cliques['ok_score_lockified'] = ok_data.apply(lambda x: x[6])
    # ok_cliques['ok_score_lockified_xtreme'] = ok_data.apply(lambda x: x[7])
    ok_cliques['ok_strong_set'] = ok_data.apply(lambda x: x[6])
    ok_cliques['ok_n_other_flavorings'] = ok_data.apply(lambda x: x[7])
    ok_cliques['ok_n_foodstuffs'] = ok_data.apply(lambda x: x[8])

    ok_cliques = ok_cliques[ok_cliques['ok_list'].apply(lambda x: len(x) >= 2)]
    ok_cliques = ok_cliques.sort_values('ok_score', ascending=False)

    n_iterations = len(present_names)*2
    # n_iterations = 100
    keep_iterating = True

    n_attempts_before_deciding = 10
    n_attempts_before_giving_up = 5

    scoring_method = 'tbd'
    top_score = 0

    for iteration in range(n_iterations):
        connection_attempt = 1
        while True:
            n_other_flavorings_actual = random.randrange(n_other_flavorings_min_actual, n_other_flavorings_max_actual+1)
            n_foodstuffs_actual = random.randrange(n_foodstuffs_min_actual, n_foodstuffs_max_actual+1)

            n_gen_other_flavorings_actual = n_other_flavorings_actual - len(locked_other_flavorings)
            n_gen_foodstuffs_actual = n_foodstuffs_actual - len(locked_foodstuffs)

            final_cliques = ok_cliques[(ok_cliques['ok_n_other_flavorings'] <= n_gen_other_flavorings_actual) & (ok_cliques['ok_n_foodstuffs'] <= n_gen_foodstuffs_actual)]

            if len(final_cliques) > 0:
                clique = final_cliques.sample(1, weights='ok_score_xtreme').iloc[0] # to skew sample toward top
            else:
                clique = final_cliques.sample(0)

            try:
                clique_ingredients = present.loc[clique['ok_list']]
            except:
                print('MAJOR PROBLEM! Likely cause: clique_data contains not-present ingredients.')
                clique_ingredients = stir_fry_flavor_data.loc[clique['ok_list']]

            salts_so_far_set = clique['ok_set'].intersection(salt_set).union(locked_salts_set)
            fat_oils_so_far_set = clique['ok_set'].intersection(fat_oil_set).union(locked_fat_oils_set)
            other_flavorings_so_far_set = clique['ok_set'].intersection(other_flavoring_set).union(locked_other_flavorings_set)
            foodstuffs_so_far_set = clique['ok_set'].intersection(foodstuff_set).union(locked_foodstuffs_set)
            ingredients_so_far_set = clique['ok_set'].union(locked_set)

            n_additional_salts = n_salts_actual - len(salts_so_far_set) # pretty sure there shouldn't be more salts so far than salts actual
            n_additional_fat_oils = n_fat_oils_actual - len(fat_oils_so_far_set) # pretty sure there shouldn't be more salts so far than salts actual
            n_additional_other_flavorings = max(n_other_flavorings_actual - len(other_flavorings_so_far_set), 0) # pretty sure there shouldn't be more salts so far than salts actual
            n_additional_foodstuffs = max(n_foodstuffs_actual - len(foodstuffs_so_far_set), 0) # pretty sure there shouldn't be more salts so far than salts actual

            additional_salts = the_rest_salts[~the_rest_salts['name'].isin(clique_ingredients['name'])].sample(n_additional_salts, weights='weak_score')
            additional_fat_oils = the_rest_fat_oils[~the_rest_fat_oils['name'].isin(clique_ingredients['name'])].sample(n_additional_fat_oils, weights='weak_score')
            additional_other_flavorings = the_rest_other_flavorings[~the_rest_other_flavorings['name'].isin(clique_ingredients['name'])].sample(n_additional_other_flavorings, weights='weak_score')
            additional_foodstuffs = the_rest_foodstuffs[~the_rest_foodstuffs['name'].isin(clique_ingredients['name'])].sample(n_additional_foodstuffs, weights='weak_score')

            ingredients_so_far = present[present['name'].isin(ingredients_so_far_set)]

            selected_ingredients = ingredients_so_far.append(additional_salts).append(additional_fat_oils).append(additional_other_flavorings).append(additional_foodstuffs)
            selected_names = selected_ingredients['name'].values.tolist()

            connections = []
            weighted_edges = []

            for i_1, name_1 in enumerate(selected_names[:-1]):
                for i_2, name_2 in enumerate(selected_names[i_1+1:], i_1+1):
                    connection = selected_ingredients[name_1][name_2]
                    if connection[0] != '_':
                        if connection[0] == 'c':
                            pairs_with_demerit = .8
                        elif connection[0] == 'd':
                            pairs_with_demerit = .6666
                        elif connection[0] == 'C':
                            pairs_with_demerit = .5333
                        elif connection[0] == 'D':
                            pairs_with_demerit = .4
                        else:
                            print('OH NO! BAD PAIRING VALUE.')

                        if connection[1] == '_':
                            strength_demerit = .2
                        elif connection[1] == 's':
                            strength_demerit = .15
                        elif connection[1] == 'S':
                            strength_demerit = .1
                        else:
                            print('OH NO! BAD STRENGTH VALUE.')


                        connection_weight = pairs_with_demerit + strength_demerit
                        weighted_edges.append((name_1, name_2, connection_weight))
                        connections.append((name_1, name_2, connection))

            selected_g = nx.Graph()
            selected_g.add_nodes_from(selected_names)
            selected_g.add_weighted_edges_from(weighted_edges)
            connected_components = list(nx.connected_components(selected_g))

            if scoring_method == 'tbd':
                if len(connected_components) == 1:
                    # print('Scoring method set to "connected"')
                    scoring_method = 'connected'
                    break
                elif connection_attempt >= n_attempts_before_deciding:
                    print('Scoring method set to "disconnected"')
                    scoring_method = 'disconnected'
                    break
            elif scoring_method == 'connected':
                if len(connected_components) == 1:
                    break
                elif connection_attempt >= n_attempts_before_giving_up:
                    print('Giving up')
                    keep_iterating = False
                    break
            elif scoring_method == 'disconnected':
                break

            connection_attempt += 1

        if not keep_iterating:
            break # Just go with the best iteration so far (rather than slogging through disconnected graphs)

        score = 0

        if scoring_method == 'connected':
            # CONNECTED PAIRING BONUS ============================================================================================
            # ranges from roughly (0 to 1) * 3, tho could be a lil over or under that range
            average_shortest_path_length = nx.average_shortest_path_length(selected_g, weight='weight')
            average_shortest_path_score = 1 / average_shortest_path_length * 1.5 - 1.25
            # print('AVERAGE SHORTEST PATH SCORE', average_shortest_path_score)
            score += average_shortest_path_score * 3
        else:
            # DISCONNECTED PAIRING BONUS ============================================================================================
            # not really sure how this sranges. hopefully (0 - 1) * 3? Hard to test.
            largest_cc = max(connected_components, key=len)
            largest_subgraph = selected_g.subgraph(largest_cc) # .copy()?
            largest_subgraph_g = nx.Graph(largest_subgraph)

            average_shortest_path_length = nx.average_shortest_path_length(largest_subgraph_g, weight='weight')
            average_shortest_path_score = 1 / average_shortest_path_length * 1.5 - 1.25
            # print('DISCONNECTED AVERAGE SHORTEST PATH SCORE', average_shortest_path_score)
            score += average_shortest_path_score * 3

        # FLAVOR BALANCE BONUS =============================================================================================
        # ranges from roughly (0 to 1) * 1 (could be a lil over/under)
        n_sweet_lower = (selected_ingredients['sweet'] == 'y').sum()
        n_sweet_upper = (selected_ingredients['sweet'] == 'Y').sum()
        n_salty_lower = (selected_ingredients['salty'] == 'y').sum()
        n_salty_upper = (selected_ingredients['salty'] == 'Y').sum()
        n_sour_lower = (selected_ingredients['sour'] == 'y').sum()
        n_sour_upper = (selected_ingredients['sour'] == 'Y').sum()
        n_savory_lower = (selected_ingredients['savory'] == 'y').sum()
        n_savory_upper = (selected_ingredients['savory'] == 'Y').sum()
        n_bitter_lower = (selected_ingredients['bitter'] == 'y').sum()
        n_bitter_upper = (selected_ingredients['bitter'] == 'Y').sum()
        n_spicy_lower = (selected_ingredients['spicy'] == 'y').sum()
        n_spicy_upper = (selected_ingredients['spicy'] == 'Y').sum()

        sweet_score = min(n_sweet_lower/2 + n_sweet_upper, 1)
        salty_score = min(n_salty_lower/2 + n_salty_upper, 1)
        sour_score = min(n_sour_lower/2 + n_sour_upper, 1)
        savory_score = min(n_savory_lower/2 + n_savory_upper, 1)
        bitter_score = min(n_bitter_lower/2 + n_bitter_upper, 1)
        spicy_score = min(n_spicy_lower/2 + n_spicy_upper, 1)

        flavor_score = 0
        flavor_score += sweet_score*3 # rly want something sweet in there
        flavor_score += salty_score*.5 # can always use salt
        flavor_score += sour_score*2 # like me some sour
        flavor_score += savory_score*3 # LOVE me some savory
        flavor_score += bitter_score # idk
        flavor_score += spicy_score*2 # can be nice
        flavor_score = flavor_score * .15 - .75

        # print('FLAVOR BALANCE SCORE', flavor_score)
        score += flavor_score

        # FOOD GROUPS BONUS ==========================================================================================
        if 'y' in selected_ingredients['stir_fry_protein'].values:
            protein_score = .5
        else:
            protein_score = 0

        if 'y' in selected_ingredients['stir_fry_fruit'].values:
            fruit_score = .5
        else:
            fruit_score = 0

        food_group_score = protein_score + fruit_score
    #     print('PROTEIN FRUIT', protein_score, fruit_score)
        score += food_group_score

        if score > top_score:
            top_average_shortest_path_score = average_shortest_path_score
            top_flavor_score = flavor_score
            top_food_group_score = food_group_score
            top_score = score
            top_selected_ingredients = selected_ingredients

    # print('PAIRING BONUS', top_average_shortest_path_score)
    # print('FLAVOR BALANCE BONUS', top_flavor_score)
    # print('FOOD GROUP BONUS', top_food_group_score)
    # print('SCORE', top_score)
    data = {
        'present_names': present_names,
        'locked_names': locked_names,
        'generated_names': top_selected_ingredients['name'][~top_selected_ingredients['name'].isin(locked_names)].tolist(),
        'pairing_bonus': top_average_shortest_path_score,
        'flavor_bonus': top_flavor_score,
        'food_group_bonus': top_food_group_score,
        'score': top_score,
        'selected_names': top_selected_ingredients['name'].tolist(),
    }
    # print('SELECTED NAMES', data['selected_names'])
    return(jsonify(data))

if __name__ == "__main__":
    app.run()
