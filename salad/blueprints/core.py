# TODO resolve "clashing" thing

from flask import Flask, render_template, request, jsonify, redirect, url_for, Blueprint
blueprint  = Blueprint('salad_core', __name__, template_folder='salad/templates')

import pandas as pd
import networkx as nx
import os
import random
import pickle
import time

root_path = os.getcwd()
salad_flavor_data = pd.read_pickle(os.path.join(root_path, 'data/salad_flavor_data.pickle'))
# stir_fry_flavor_data = pd.read_pickle(os.path.join(root_path, 'data/stir_fry_flavor_data.pickle'))

@blueprint.route('/salad')
def salad_index():
    return render_template('index.html')

@blueprint.route('/get-salad-ingredients', methods=['GET'])
def get_salad_ingredients():
    salad_ingredients = [
        {
            col_name: row[col_name]
        for col_name in salad_flavor_data.columns.tolist()}
    for i, row in salad_flavor_data.iterrows()]
    # print(salad_flavor_data.columns.tolist())
    return jsonify(salad_ingredients)

@blueprint.route('/generate-salad', methods=['POST'])
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

    unlocked = salad_data[~salad_data['name'].isin(locked_names)]
    unlocked_greens = unlocked[unlocked['salad_green'] == 'y']
    unlocked_extras = unlocked[unlocked['salad_extra'] == 'y']
    unlocked_dressing_oils = unlocked[unlocked['salad_dressing_oil'] == 'y']
    unlocked_dressing_vinegars = unlocked[unlocked['salad_dressing_vinegar'] == 'y']
    unlocked_dressing_salts = unlocked[unlocked['salad_dressing_salt'] == 'y']
    unlocked_dressing_peppers = unlocked[unlocked['salad_dressing_pepper'] == 'y']

    n_gen_greens_min = max(2-len(locked_greens), 0)
    n_gen_greens_max = max(3-len(locked_greens), 0)

    n_gen_extras_min = max(2-len(locked_extras), 0)
    n_gen_extras_max = max(4-len(locked_extras), 0)

    # *3: times out at 30s with all ingredients
    # *2: 25s with all ingredients
    # *1: 10-15s with all ingredients
    n_iterations = 300
    keep_iterating = True

    n_attempts_before_deciding = 10
    n_attempts_before_giving_up = 5

    scoring_method = 'tbd'
    top_score = None

    for iteration in range(n_iterations):
        # n_subgraphs = 2
        connection_attempt = 1
        while True: # keep shuffling until you get a well connected graph

            # don't try to select fewer than 0, and don't try to select more than there are ingredients left
            n_gen_greens = min(random.randrange(n_gen_greens_min, n_gen_greens_max+1), len(unlocked_greens))
            n_gen_extras = min(random.randrange(n_gen_extras_min, n_gen_extras_max+1), len(unlocked_extras))
            n_gen_dressing_oils = min(max(1-len(locked_dressing_oils), 0), len(unlocked_dressing_oils))
            n_gen_dressing_vinegars = min(max(1-len(locked_dressing_vinegars), 0), len(unlocked_dressing_vinegars))
            n_gen_dressing_salts = min(max(1-len(locked_dressing_salts), 0), len(unlocked_dressing_salts))
            n_gen_dressing_peppers = min(max(1-len(locked_dressing_peppers), 0), len(unlocked_dressing_peppers))

            selected_greens = locked_greens.append(unlocked_greens.sample(n_gen_greens))
            selected_extras = locked_extras.append(unlocked_extras.sample(n_gen_extras))
            selected_dressing_oils = locked_dressing_oils.append(unlocked_dressing_oils.sample(n_gen_dressing_oils))
            selected_dressing_vinegars = locked_dressing_vinegars.append(unlocked_dressing_vinegars.sample(n_gen_dressing_vinegars))
            selected_dressing_salts = locked_dressing_salts.append(unlocked_dressing_salts.sample(n_gen_dressing_salts))
            selected_dressing_peppers = locked_dressing_peppers.append(unlocked_dressing_peppers.sample(n_gen_dressing_peppers))
            selected_ingredients = selected_greens.append(selected_extras).append(selected_dressing_oils).append(selected_dressing_vinegars).append(selected_dressing_salts).append(selected_dressing_peppers)
            selected_names = selected_ingredients['name'].tolist()

            # lower_category_pairs = []
            # lower_direct_pairs = []
            # upper_category_pairs = []
            # upper_direct_pairs = []
            # lower_clashing_pairs = []
            # upper_clashing_pairs = []
            #
            # # finicky but pretty fast
            # for i, col_name in enumerate(selected_names):
            #     for j, row_name in enumerate(selected_names[i+1:]):
            #         connection = selected_ingredients[col_name].tolist()[i+1+j] # this is what is finicky
            #         if connection == 'c':
            #             lower_category_pairs.append((col_name, row_name,))
            #         elif connection == 'd':
            #             lower_direct_pairs.append((col_name, row_name,))
            #         elif connection == 'C':
            #             upper_category_pairs.append((col_name, row_name,))
            #         elif connection == 'D':
            #             upper_direct_pairs.append((col_name, row_name,))
            #         elif connection == 'n':
            #             lower_clashing_pairs.append((col_name, row_name,))
            #         elif connection == 'N':
            #             upper_clashing_pairs.append((col_name, row_name,))
            # lower_pairs = lower_category_pairs + lower_direct_pairs
            # upper_pairs = upper_category_pairs + upper_direct_pairs
            # all_pairs = lower_pairs + upper_pairs
            # all_clashing_pairs = lower_clashing_pairs + upper_clashing_pairs
            #
            # selected_g = nx.Graph()
            # selected_g.add_nodes_from(selected_names)
            # selected_g.add_edges_from(lower_category_pairs, length=2)
            # selected_g.add_edges_from(lower_direct_pairs, length=1.5)
            # selected_g.add_edges_from(upper_category_pairs, length=1.2)
            # selected_g.add_edges_from(upper_direct_pairs, length=1)

            connections = []
            weighted_edges = []

            # finicky but pretty fast
            for i, col_name in enumerate(selected_names):
                for j, row_name in enumerate(selected_names[i+1:]):
                    connection = selected_ingredients[col_name].tolist()[i+1+j] # this is what is finicky
                    if connection in 'cdCD': # can't remember if 'no connection' values are '_', so using this workaround
                        if connection == 'c':
                            pairs_with_demerit = .7 # prev .8
                        elif connection == 'd':
                            pairs_with_demerit = .6 # prev .6666
                        elif connection == 'C':
                            pairs_with_demerit = .5 # prev .5333
                        elif connection == 'D':
                            pairs_with_demerit = .4 # prev. .4
                        else:
                            print('OH NO! BAD PAIRING VALUE.')
                        #
                        # if connection[1] == '_':
                        #     strength_demerit = .2
                        # elif connection[1] == 's':
                        #     strength_demerit = .15
                        # elif connection[1] == 'S':
                        #     strength_demerit = .1
                        # else:
                        #     print('OH NO! BAD STRENGTH VALUE.')

                        # # idea is that if 1+ names are locked, their connections will weigh score down less
                        # if col_name in locked_names and row_name in locked_names:
                        #     locked_demerit = .1 # should actually be the same for every iteration, given that locked don't change
                        # elif col_name in locked_names or row_name in locked_names:
                        #     locked_demerit = .2
                        # else:
                        #     locked_demerit = .3

                        # connection_weight = pairs_with_demerit + strength_demerit + locked_demerit
                        connection_weight = pairs_with_demerit
                        weighted_edges.append((col_name, row_name, connection_weight))
                        connections.append((col_name, row_name, connection))

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

        if scoring_method == 'connected':
            # CONNECTED PAIRING BONUS ============================================================================================
            # ranges from roughly (0 to 1) * 3, tho could be a lil over or under that range
            average_shortest_path_length = nx.average_shortest_path_length(selected_g, weight='weight')
            # print('AVERAGE SHORTEST PATH LENGTH', average_shortest_path_length)
            average_shortest_path_score = 1 / average_shortest_path_length * 2.5 - 1.1
            # print('AVERAGE SHORTEST PATH SCORE', average_shortest_path_score)
            score += average_shortest_path_score * 5
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
            score += average_shortest_path_score * 5

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

        if top_score == None or score > top_score:
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
