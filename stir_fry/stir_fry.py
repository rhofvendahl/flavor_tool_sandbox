# print(__main__)

# from __main__ import app

from flask import Flask, render_template, request, jsonify, redirect, url_for, Blueprint
stir_fry_blueprint  = Blueprint('stir_fry_blueprint', __name__, template_folder='templates')

import pandas as pd
import networkx as nx
import os
import random
import pickle
import time

root_path = os.getcwd()
stir_fry_flavor_data = pd.read_pickle(os.path.join(root_path, 'data/stir_fry_flavor_data_with_umbrella.pickle'))

@stir_fry_blueprint.route('/stir-fry')
def stir_fry_index():
    return render_template('stir-fry-index.html')

@stir_fry_blueprint.route('/get-stir-fry-ingredients', methods=['GET'])
def get_stir_fry_ingredients():
    stir_fry_ingredients = [
        {
            col_name: row[col_name]
        for col_name in stir_fry_flavor_data.columns.tolist()}
    for i, row in stir_fry_flavor_data.iterrows()]
    return jsonify(stir_fry_ingredients)

@stir_fry_blueprint.route('/generate-stir-fry', methods=['POST'])
def generate_stir_fry():
    n_salts = 1
    n_fat_oils = 1
    n_other_flavorings_min = 1
    n_other_flavorings_max = 3
    n_foodstuffs_min = 4
    n_foodstuffs_max = 7

    content = request.get_json()
    locked_names = content['locked']
    present_names = content['present']

    if len(present_names) < 7:
        data = {
            'outcome': 'failure',
            'message': "You'll need to add a few more ingredients before you can generate a recipe.",
        }
        return(jsonify(data))

    stir_fry_data = stir_fry_flavor_data[stir_fry_flavor_data['name'].isin(present_names)].copy()
    present_fat_oils = stir_fry_data[stir_fry_data['stir_fry_fat_oil'] == 'y']
    present_salts = stir_fry_data[stir_fry_data['stir_fry_salt'] == 'y']
    present_other_flavorings = stir_fry_data[(stir_fry_data['stir_fry_flavoring'] == 'y') & (stir_fry_data['stir_fry_salt'] != 'y')]
    present_foodstuffs = stir_fry_data[(stir_fry_data['stir_fry_fat_oil'] != 'y') & (stir_fry_data['stir_fry_salt'] != 'y') & (stir_fry_data['stir_fry_flavoring'] != 'y')] # why am I selecting not salt? already selecting not flavoring. don't wanna mess tho..
    present_fat_oils_set = set(present_fat_oils['name'])
    present_salts_set = set(present_salts['name'])
    present_other_flavorings_set = set(present_other_flavorings['name'])
    present_foodstuffs_set = set(present_foodstuffs['name'])

    locked = stir_fry_data[stir_fry_data['name'].isin(locked_names)]
    locked_fat_oils = locked[locked['stir_fry_fat_oil'] == 'y']
    locked_salts = locked[locked['stir_fry_salt'] == 'y']
    locked_other_flavorings = locked[(locked['stir_fry_flavoring'] == 'y') & (locked['stir_fry_salt'] != 'y')]
    locked_foodstuffs = locked[(locked['stir_fry_fat_oil'] != 'y') & (locked['stir_fry_salt'] != 'y') & (locked['stir_fry_flavoring'] != 'y')]

    unlocked = stir_fry_data[~stir_fry_data['name'].isin(locked['name'])]
    unlocked_fat_oils = unlocked[unlocked['stir_fry_fat_oil'] == 'y']
    unlocked_salts = unlocked[unlocked['stir_fry_salt'] == 'y']
    unlocked_other_flavorings = unlocked[(unlocked['stir_fry_flavoring'] == 'y') & (unlocked['stir_fry_salt'] != 'y')]
    unlocked_foodstuffs = unlocked[(unlocked['stir_fry_fat_oil'] != 'y') & (unlocked['stir_fry_salt'] != 'y') & (unlocked['stir_fry_flavoring'] != 'y')]

    n_additional_salts_needed = max(n_salts - len(locked_salts), 0)
    n_additional_salts_actual = min(n_additional_salts_needed, len(unlocked_salts))
    n_total_salts_actual = n_additional_salts_actual + len(locked_salts)

    n_additional_fat_oils_needed = max(n_fat_oils - len(locked_fat_oils), 0)
    n_additional_fat_oils_actual = min(n_additional_fat_oils_needed, len(unlocked_fat_oils))
    n_total_fat_oils_actual = n_additional_fat_oils_actual + len(locked_fat_oils)

    n_additional_other_flavorings_needed_min = max(n_other_flavorings_min - len(locked_other_flavorings), 0)
    n_additional_other_flavorings_actual_min = min(n_additional_other_flavorings_needed_min, len(unlocked_other_flavorings))
    n_total_other_flavorings_actual_min = n_additional_other_flavorings_actual_min + len(locked_other_flavorings)

    n_additional_other_flavorings_needed_max = max(n_other_flavorings_max - len(locked_other_flavorings), 0) # yikes, I had this as min..
    n_additional_other_flavorings_actual_max = min(n_additional_other_flavorings_needed_max, len(unlocked_other_flavorings))
    n_total_other_flavorings_actual_max = n_additional_other_flavorings_actual_max + len(locked_other_flavorings)

    n_additional_foodstuffs_needed_min = max(n_foodstuffs_min - len(locked_foodstuffs), 0)
    n_additional_foodstuffs_actual_min = min(n_additional_foodstuffs_needed_min, len(unlocked_foodstuffs))
    n_total_foodstuffs_actual_min = n_additional_foodstuffs_actual_min + len(locked_foodstuffs)

    n_additional_foodstuffs_needed_max = max(n_foodstuffs_max - len(locked_foodstuffs), 0)
    n_additional_foodstuffs_actual_max = min(n_additional_foodstuffs_needed_max, len(unlocked_foodstuffs))
    n_total_foodstuffs_actual_max = n_additional_foodstuffs_actual_max + len(locked_foodstuffs)

    n_iterations = 175
    top_score = None

    n = 0
    start = time.time()
    for iteration in range(n_iterations):
        if time.time() - start > 15:
            print("OOPS! Time's up. " + str(n) + ' iterations completed.')
            break
        n += 1

        n_additional_other_flavorings_actual = random.randrange(n_additional_other_flavorings_actual_min, n_additional_other_flavorings_actual_max+1)
        n_additional_foodstuffs_actual = random.randrange(n_additional_foodstuffs_actual_min, n_additional_foodstuffs_actual_max+1)

        if len(locked) > 0:
            maybe_neighbors_so_far_list = []
            for ingredient_name in locked['name'].tolist():
                maybe_neighbors_so_far_list += locked['upper_names'][ingredient_name]

            valid_neighbor_counts = dict()
            for neighbor in maybe_neighbors_so_far_list:
                if not neighbor in locked['name'].tolist():
                    valid_neighbor_counts[neighbor] = valid_neighbor_counts.get(neighbor, 0) + 1
            selected_ingredients = locked

        elif len(present_other_flavorings) > 1 and len(present_foodstuffs) > 1:
            seed = present_other_flavorings.append(present_foodstuffs).sample(1)
            maybe_neighbors_so_far_list = seed['upper_names'].iloc[0]
            valid_neighbor_counts = {neighbor: 1 for neighbor in seed['upper_names'].iloc[0]}
            selected_ingredients = locked.append(seed)
            if seed['stir_fry_flavoring'].iloc[0] == 'y':
                n_additional_other_flavorings_actual -= 1
            else:
                n_additional_foodstuffs_actual -= 1
        elif len(present_foodstuffs) > 1: # paranoid
            print('No other flavorings? weird.')
            seed = present_foodstuffs.sample(1)
            maybe_neighbors_so_far_list = seed['upper_names'].iloc[0]
            valid_neighbor_counts = {neighbor: 1 for neighbor in seed['upper_names'].iloc[0]}
            selected_ingredients = locked.append(seed)
            n_additional_foodstuffs_actual -= 1
        else: # very paranoid
            print('Yikes! No flavorings OR foodstuffs.')
            continue

        selected_names_so_far = selected_ingredients['name'].tolist()
        # print('valid neighbor counts', valid_neighbor_counts)
        if n_additional_salts_actual > 0:
            additional_salts_pool = unlocked_salts[~unlocked_salts['name'].isin(selected_names_so_far)]
            additional_salts_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_salts_pool['name']]
            selected_ingredients = selected_ingredients.append(additional_salts_pool.sample(n_additional_salts_actual, weights='neighbor_counts_xtreme'))
        if n_additional_fat_oils_actual > 0:
            additional_fat_oils_pool = unlocked_fat_oils[~unlocked_fat_oils['name'].isin(selected_names_so_far)]
            additional_fat_oils_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_fat_oils_pool['name']]
            selected_ingredients = selected_ingredients.append(additional_fat_oils_pool.sample(n_additional_fat_oils_actual, weights='neighbor_counts_xtreme'))
        if n_additional_other_flavorings_actual > 0:
            additional_other_flavorings_pool = unlocked_other_flavorings[~unlocked_other_flavorings['name'].isin(selected_names_so_far)]
            additional_other_flavorings_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_other_flavorings_pool['name']]
            selected_ingredients = selected_ingredients.append(additional_other_flavorings_pool.sample(n_additional_other_flavorings_actual, weights='neighbor_counts_xtreme'))
        if n_additional_foodstuffs_actual > 0:
            additional_foodstuffs_pool = unlocked_foodstuffs[~unlocked_foodstuffs['name'].isin(selected_names_so_far)]
            additional_foodstuffs_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_foodstuffs_pool['name']]
            selected_ingredients = selected_ingredients.append(additional_foodstuffs_pool.sample(n_additional_foodstuffs_actual, weights='neighbor_counts_xtreme'))

        selected_names = selected_ingredients['name'].tolist()

        selected_g = nx.Graph()
        selected_g.add_nodes_from(selected_names)

        for i_1, name_1 in enumerate(selected_names[:-1]):
            for i_2, name_2 in enumerate(selected_names[i_1+1:], i_1+1):
                connection = selected_ingredients[name_1][name_2]

                # Weights super guess-y
                if connection[0] == 'c':
                    selected_g.add_edge(name_1, name_2, length=1, weight=.3) # prev .8
                elif connection[0] == 'd':
                    # pairs_with_demerit = .5 # prev .6666
                    selected_g.add_edge(name_1, name_2, length=.7, weight=.6) # prev .8
                elif connection[0] == 'C':
                    # pairs_with_demerit = .4 # prev .5333
                    selected_g.add_edge(name_1, name_2, length=.6, weight=.7) # prev .8
                elif connection[0] == 'D':
                    # pairs_with_demerit = .3 # prev. .4
                    selected_g.add_edge(name_1, name_2, length=.3, weight=1) # prev .8

        # Try again, friend
        if not nx.is_connected(selected_g):
            print(str(iteration)+': NOT CONNECTED; SKIPPING TO NEXT ITERATION')
            continue

        score = 0

        # CONNECTED PAIRING BONUS ==============================================
        # I want this to be VERY important. I feel this holds a lot of the strength of recipe,
        # and also encompasses strength-ness and locked-ness
        # ranges from roughly (0 to 1) * 3, tho could be a lil over or under that range
        average_shortest_path_length = nx.average_shortest_path_length(selected_g, weight='length')
        pairing_score = 1 / average_shortest_path_length * 1.4 - 1 # good enough (for small, large pools)
        # print('PAIRING SCORE', pairing_score)
        score += pairing_score * 4

        # Used for both strength and locked bonus:
        node_degrees = list(selected_g.degree(weight='weight'))
        average_degree = sum([node_degree[1] for node_degree in node_degrees]) / len(node_degrees)

        # STRENGTH BONUS =======================================================
        strength_above_average = 0
        for node_degree in node_degrees:
            if selected_ingredients['strong'][node_degree[0]] == 'Y':
                strength_above_average += (node_degree[1] - average_degree)
            elif selected_ingredients['strong'][node_degree[0]] == 'y':
                strength_above_average += (node_degree[1] - average_degree) * .5
        strength_score = strength_above_average * .2 + .5 # reasonable for small and full pools
        # print('STRENGTH SCORE', strength_score)
        score += strength_score

        if len(locked) > 0:
            # LOCKED BONUS =========================================================
            locked_above_average = 0
            for node_degree in node_degrees:
                if node_degree[0] in locked_names:
                    locked_above_average += node_degree[1] - average_degree
            locked_score = locked_above_average * .2 + .5 # close enough (has to cover few locked, lotta locked, small pool, big pool - yeesh.)
            # print('LOCKED SCORE', locked_score)
            score += locked_score * 2
        else:
            locked_score = 0
        score += locked_score

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
        n_protein = (selected_ingredients['stir_fry_protein'] == 'y').sum()
        n_fruit = (selected_ingredients['stir_fry_fruit'] == 'y').sum()
        n_grain = (selected_ingredients['stir_fry_grain'] == 'y').sum()
        n_leafy = (selected_ingredients['veg_leafy'] == 'y').sum()

        food_group_score = .5

        if n_protein in range(1, 3):
            food_group_score += .25
        if n_protein == 3:
            food_group_score -= .25
        if n_protein > 3:
            food_group_score -= .5

        if n_fruit == 1:
            food_group_score += .25
        if n_fruit > 2:
            food_group_score -= .5

        if n_grain > 1:
            food_group_score -= .25
        if n_grain > 2:
            food_group_score -= .5

        if n_leafy > 1:
            food_group_score -= .25
        if n_leafy > 2:
            food_group_score -= .5

        # if 'y' in selected_ingredients['stir_fry_protein'].sum():
        #     protein_score = .5
        # else:
        #     protein_score = 0
        #
        # if 'y' in selected_ingredients['stir_fry_fruit'].values:
        #     fruit_score = .5
        # else:
        #     fruit_score = 0

        # food_group_score = protein_score + fruit_score
        # print('FOOD GROUP SCORE', food_group_score)
        score += food_group_score

        # print('score', score)
        # print()
        if top_score == None or score > top_score:
            top_selected_ingredients = selected_ingredients
            top_pairing_score = pairing_score
            top_strength_score = strength_score
            top_locked_score = locked_score
            top_flavor_score = flavor_score
            top_food_group_score = food_group_score
            top_score = score

    if top_score:
        data = {
            'outcome': 'success',
            'data': {
                'present_names': present_names,
                'locked_names': locked_names,
                'generated_names': top_selected_ingredients['name'][~top_selected_ingredients['name'].isin(locked_names)].tolist(),
                'pairing_bonus': top_pairing_score,
                'strength_bonus': top_strength_score,
                'locked_bonus': top_locked_score,
                'flavor_bonus': top_flavor_score,
                'food_group_bonus': top_food_group_score,
                'score': top_score,
                'selected_names': top_selected_ingredients['name'].tolist(),
            },
        }
    else:
        data = {
            'outcome': 'failure',
            'message': "Darn! The generator isn't coming up with anything for these ingredients.",
        }
    return(jsonify(data))

# BLACK MAGIC SETUP ============================================================
# # Darn, this pollutes namespace for salad... ugh. Is it fast enough to include inside? Should I prepend "stir_fry_"?
# salt_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_salt'] == 'y']['name'])
# fat_oil_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_fat_oil'] == 'y']['name'])
# other_flavoring_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_flavoring'] == 'y']['name']) - salt_set
# foodstuff_set = set(stir_fry_flavor_data['name']) - salt_set - fat_oil_set - other_flavoring_set
# mushroom_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_mushroom'] == 'y']['name'])
# bean_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_protein_bean'] == 'y'])
# grain_set = set(stir_fry_flavor_data[stir_fry_flavor_data['stir_fry_grain'] == 'y'])

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

# not used?
# with open(os.path.join(root_path, 'data/stir_fry_shortest_path_lengths.pickle'), 'rb') as handle:
#     stir_fry_shortest_path_lengths = pickle.load(handle)

def get_sort_key(length_tuple):
    return length_tuple[1]

def n_possible_edges(n_nodes):
    return int((n_nodes*(n_nodes-1)) / 2)

def get_first_name_in_set(sorted_tuples, food_set):
    for sorted_tuple in sorted_tuples:
        if sorted_tuple[0] in food_set:
            return sorted_tuple[0]

@stir_fry_blueprint.route('/generate-stir-fry-black-magic', methods=['POST'])
def generate_stir_fry_black_magic():
    n_salts = 1
    n_fat_oils = 1
    n_other_flavorings_min = 1
    n_other_flavorings_max = 3
    n_foodstuffs_min = 4
    n_foodstuffs_max = 7
    mushrooms_cap = 1 # possible to have more than this, if there are locked mushrooms (I don't update sets after locked/gen is established)
    n_beans_max = 1
    n_grains_max = 1

    content = request.get_json()
    locked_names = content['locked']
    present_names = content['present']

    if len(present_names) < 7:
        data = {
            'outcome': 'failure',
            'message': "You'll need to add a few more ingredients before you can generate a recipe.",
        }
        return(jsonify(data))

    present = stir_fry_flavor_data[stir_fry_flavor_data['name'].isin(present_names)].copy()
    present_set = set(present_names)
    present_strong_set = set(present[present['strong'].isin(['Y', 'y'])]['name'])
    not_present_set = set(stir_fry_flavor_data['name']) - present_set
    present_fat_oils = present[present['stir_fry_fat_oil'] == 'y']
    present_salts = present[present['stir_fry_salt'] == 'y']
    present_other_flavorings = present[(present['stir_fry_flavoring'] == 'y') & (present['stir_fry_salt'] != 'y')]
    present_foodstuffs = present[(present['stir_fry_fat_oil'] != 'y') & (present['stir_fry_salt'] != 'y') & (present['stir_fry_flavoring'] != 'y')] # why am I selecting not salt? already selecting not flavoring. don't wanna mess tho..
    present_fat_oils_set = set(present_fat_oils['name'])
    present_salts_set = set(present_salts['name'])
    present_other_flavorings_set = set(present_other_flavorings['name'])
    present_foodstuffs_set = set(present_foodstuffs['name'])

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

    unlocked = present[~present['name'].isin(locked['name'])]
    unlocked_set = present_set - locked_set
    unlocked_fat_oils = unlocked[unlocked['stir_fry_fat_oil'] == 'y']
    unlocked_salts = unlocked[unlocked['stir_fry_salt'] == 'y']
    unlocked_other_flavorings = unlocked[(unlocked['stir_fry_flavoring'] == 'y') & (unlocked['stir_fry_salt'] != 'y')]
    unlocked_foodstuffs = unlocked[(unlocked['stir_fry_fat_oil'] != 'y') & (unlocked['stir_fry_salt'] != 'y') & (unlocked['stir_fry_flavoring'] != 'y')]
    unlocked_fat_oils_set = set(unlocked_fat_oils['name'])
    unlocked_salts_set = set(unlocked_salts['name'])
    unlocked_other_flavorings_set = set(unlocked_other_flavorings['name'])
    unlocked_foodstuffs_set = set(unlocked_foodstuffs['name'])

    n_additional_salts_needed = max(n_salts - len(locked_salts), 0)
    n_additional_salts_actual = min(n_additional_salts_needed, len(unlocked_salts))
    n_total_salts_actual = n_additional_salts_actual + len(locked_salts)

    n_additional_fat_oils_needed = max(n_fat_oils - len(locked_fat_oils), 0)
    n_additional_fat_oils_actual = min(n_additional_fat_oils_needed, len(unlocked_fat_oils))
    n_total_fat_oils_actual = n_additional_fat_oils_actual + len(locked_fat_oils)

    n_additional_other_flavorings_needed_min = max(n_other_flavorings_min - len(locked_other_flavorings), 0)
    n_additional_other_flavorings_actual_min = min(n_additional_other_flavorings_needed_min, len(unlocked_other_flavorings))
    n_total_other_flavorings_actual_min = n_additional_other_flavorings_actual_min + len(locked_other_flavorings)

    n_additional_other_flavorings_needed_max = max(n_other_flavorings_max - len(locked_other_flavorings), 0) # yikes, I had this as min..
    n_additional_other_flavorings_actual_max = min(n_additional_other_flavorings_needed_max, len(unlocked_other_flavorings))
    n_total_other_flavorings_actual_max = n_additional_other_flavorings_actual_max + len(locked_other_flavorings)

    n_additional_foodstuffs_needed_min = max(n_foodstuffs_min - len(locked_foodstuffs), 0)
    n_additional_foodstuffs_actual_min = min(n_additional_foodstuffs_needed_min, len(unlocked_foodstuffs))
    n_total_foodstuffs_actual_min = n_additional_foodstuffs_actual_min + len(locked_foodstuffs)

    n_additional_foodstuffs_needed_max = max(n_foodstuffs_max - len(locked_foodstuffs), 0)
    n_additional_foodstuffs_actual_max = min(n_additional_foodstuffs_needed_max, len(unlocked_foodstuffs))
    n_total_foodstuffs_actual_max = n_additional_foodstuffs_actual_max + len(locked_foodstuffs)

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
        n_salts_to_remove = max(n_salts_so_far - n_total_salts_actual, 0)
        salts_to_remove_from_set = updated_salts_set - locked_salts_set
        more_salts_to_remove_set = set(random.sample(salts_to_remove_from_set, n_salts_to_remove))

        n_fat_oils_so_far = len(updated_fat_oils_set.union(locked_fat_oils_set))
        n_fat_oils_to_remove = max(n_fat_oils_so_far - n_total_fat_oils_actual, 0)
        fat_oils_to_remove_from_set = updated_fat_oils_set - locked_fat_oils_set
        more_fat_oils_to_remove_set = set(random.sample(fat_oils_to_remove_from_set, n_fat_oils_to_remove))

        n_other_flavorings_so_far = len(updated_other_flavorings_set.union(locked_other_flavorings_set))
        n_other_flavorings_to_remove = max(n_other_flavorings_so_far - n_total_other_flavorings_actual_max, 0) # is this right?
        other_flavorings_to_remove_from_set = updated_other_flavorings_set - locked_other_flavorings_set
        more_other_flavorings_to_remove_set = set(random.sample(salts_to_remove_from_set, n_salts_to_remove))

        n_foodstuffs_so_far = len(updated_foodstuffs_set.union(locked_foodstuffs_set))
        n_foodstuffs_to_remove = max(n_foodstuffs_so_far - n_total_foodstuffs_actual_max, 0) # is this right? thinks so - it's keeping foodstuffs from above max
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
    ok_cliques['ok_strong_set'] = ok_data.apply(lambda x: x[6])
    ok_cliques['ok_n_other_flavorings'] = ok_data.apply(lambda x: x[7])
    ok_cliques['ok_n_foodstuffs'] = ok_data.apply(lambda x: x[8])

    ok_cliques = ok_cliques[ok_cliques['ok_list'].apply(lambda x: len(x) >= 2)]
    ok_cliques = ok_cliques.sort_values('ok_score', ascending=False)

    top_score = None
    n_iterations = 200

    n = 0
    start = time.time()
    for iteration in range(n_iterations):
        if time.time() - start > 15:
            print("OOPS! Time's up. " + str(n) + ' iterations completed.')
            break
        n += 1

        n_total_other_flavorings_actual = random.randrange(n_total_other_flavorings_actual_min, n_total_other_flavorings_actual_max+1)
        n_total_foodstuffs_actual = random.randrange(n_total_foodstuffs_actual_min, n_total_foodstuffs_actual_max+1)

        n_additional_other_flavorings_actual = n_total_other_flavorings_actual - len(locked_other_flavorings)
        n_additional_foodstuffs_actual = n_total_foodstuffs_actual - len(locked_foodstuffs)

        final_cliques = ok_cliques[(ok_cliques['ok_n_other_flavorings'] <= n_additional_other_flavorings_actual) & (ok_cliques['ok_n_foodstuffs'] <= n_additional_foodstuffs_actual)]

        if len(final_cliques) > 0: # BLACK MAGIC
            # print('LET\'S DO MAGIC!')
            clique = final_cliques.sample(1, weights='ok_score_xtreme').iloc[0] # using xtreme to skew sample toward top

            try:
                clique_ingredients = present.loc[clique['ok_list']]
            except:
                print('MAJOR PROBLEM! Likely cause: clique_data contains not-present ingredients.')
                clique_ingredients = stir_fry_flavor_data.loc[clique['ok_list']]

            salts_so_far_set = clique['ok_set'].intersection(present_salts_set).union(locked_salts_set)
            fat_oils_so_far_set = clique['ok_set'].intersection(present_fat_oils_set).union(locked_fat_oils_set)
            other_flavorings_so_far_set = clique['ok_set'].intersection(present_other_flavorings_set).union(locked_other_flavorings_set)
            foodstuffs_so_far_set = clique['ok_set'].intersection(present_foodstuffs_set).union(locked_foodstuffs_set)
            ingredients_so_far_set = clique['ok_set'].union(locked_set)

            n_additional_non_clique_salts = n_total_salts_actual - len(salts_so_far_set) # pretty sure there shouldn't be more salts so far than salts actual
            n_additional_non_clique_fat_oils = n_total_fat_oils_actual - len(fat_oils_so_far_set) # pretty sure there shouldn't be more salts so far than salts actual
            n_additional_non_clique_other_flavorings = n_total_other_flavorings_actual - len(other_flavorings_so_far_set)
            n_additional_non_clique_foodstuffs = n_total_foodstuffs_actual - len(foodstuffs_so_far_set)

            # I want some way to note how many so_far ingredients neighbor is next to
            # lessee. if a neighbor is next to a LOT of so far ingredients, it should appear a bunch, cause I'm iterating through so far set
            maybe_neighbors_so_far_list = []
            for ingredient in ingredients_so_far_set:
                maybe_neighbors_so_far_list += stir_fry_flavor_data['upper_names'][ingredient]

            valid_neighbor_counts = dict()
            for neighbor in maybe_neighbors_so_far_list:
                if not neighbor in ingredients_so_far_set:
                    valid_neighbor_counts[neighbor] = valid_neighbor_counts.get(neighbor, 0) + 1

            selected_ingredients = present[present['name'].isin(ingredients_so_far_set)]
            # print('valid neighbor counts', valid_neighbor_counts)

            # the idea is that with a low weight, non-neighbors will only be selected after neighbors
            # counts are squared to exaggerate the preference for an ingredient being neighbor to many selected ingredients
            if n_additional_non_clique_salts > 0:
                additional_salts_pool = present_salts[~present_salts['name'].isin(salts_so_far_set)]
                additional_salts_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_salts_pool['name']]
                additional_salts = additional_salts_pool.sample(n_additional_non_clique_salts, weights='neighbor_counts_xtreme')
                selected_ingredients = selected_ingredients.append(additional_salts)

            if n_additional_non_clique_fat_oils > 0:
                additional_fat_oils_pool = present_fat_oils[~present_fat_oils['name'].isin(fat_oils_so_far_set)]
                additional_fat_oils_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_fat_oils_pool['name']]
                additional_fat_oils = additional_fat_oils_pool.sample(n_additional_non_clique_fat_oils, weights='neighbor_counts_xtreme')
                selected_ingredients = selected_ingredients.append(additional_fat_oils)

            if n_additional_non_clique_other_flavorings > 0:
                additional_other_flavorings_pool = present_other_flavorings[~present_other_flavorings['name'].isin(other_flavorings_so_far_set)]
                additional_other_flavorings_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_other_flavorings_pool['name']]
                additional_other_flavorings = additional_other_flavorings_pool.sample(n_additional_non_clique_other_flavorings, weights='neighbor_counts_xtreme')
                selected_ingredients = selected_ingredients.append(additional_other_flavorings)

            if n_additional_non_clique_foodstuffs > 0:
                additional_foodstuffs_pool = present_foodstuffs[~present_foodstuffs['name'].isin(foodstuffs_so_far_set)]
                additional_foodstuffs_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_foodstuffs_pool['name']]
                additional_foodstuffs = additional_foodstuffs_pool.sample(n_additional_non_clique_foodstuffs, weights='neighbor_counts_xtreme')
                selected_ingredients = selected_ingredients.append(additional_foodstuffs)

        else: # REGULAR
            # print('REGULAR IT IS.')
            if len(locked) > 0:
                # print('some locked', locked['name'].iloc[0])
                # print('locked upper names', locked['upper_names'].iloc[0])
                maybe_neighbors_so_far_list = []
                for ingredient_name in locked['name'].tolist():
                    maybe_neighbors_so_far_list += locked['upper_names'][ingredient_name]

                valid_neighbor_counts = dict()
                for neighbor in maybe_neighbors_so_far_list:
                    # print('neighbor', type(neighbor))
                    # print('locked', type(locked))
                    # print('neighbor in locked', neighbor in locked)
                    if not neighbor in locked['name'].tolist():
                        # print('not in locked')
                        valid_neighbor_counts[neighbor] = valid_neighbor_counts.get(neighbor, 0) + 1
                selected_ingredients = locked
            elif len(present_other_flavorings) > 1 and len(present_foodstuffs) > 1:
                seed = present_other_flavorings.append(present_foodstuffs).sample(1)
                maybe_neighbors_so_far_list = seed['upper_names'].iloc[0]
                valid_neighbor_counts = {neighbor: 1 for neighbor in seed['upper_names'].iloc[0]}
                selected_ingredients = locked.append(seed)
                if seed['stir_fry_flavoring'].iloc[0] == 'y':
                    n_additional_other_flavorings_actual -= 1
                else:
                    n_additional_foodstuffs_actual -= 1
            elif len(present_foodstuffs) > 1: # paranoid
                print('No other flavorings? weird.')
                seed = present_foodstuffs.sample(1)
                maybe_neighbors_so_far_list = seed['upper_names'].iloc[0]
                valid_neighbor_counts = {neighbor: 1 for neighbor in seed['upper_names'].iloc[0]}
                selected_ingredients = locked.append(seed)
                n_additional_foodstuffs_actual -= 1
            else: # very paranoid
                print('Yikes! No flavorings OR foodstuffs.')
                continue

            selected_names_so_far = selected_ingredients['name'].tolist()
            # print('valid neighbor counts', valid_neighbor_counts)
            if n_additional_salts_actual > 0:
                additional_salts_pool = unlocked_salts[~unlocked_salts['name'].isin(selected_names_so_far)]
                additional_salts_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_salts_pool['name']]
                selected_ingredients = selected_ingredients.append(additional_salts_pool.sample(n_additional_salts_actual, weights='neighbor_counts_xtreme'))
            if n_additional_fat_oils_actual > 0:
                additional_fat_oils_pool = unlocked_fat_oils[~unlocked_fat_oils['name'].isin(selected_names_so_far)]
                additional_fat_oils_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_fat_oils_pool['name']]
                selected_ingredients = selected_ingredients.append(additional_fat_oils_pool.sample(n_additional_fat_oils_actual, weights='neighbor_counts_xtreme'))
            if n_additional_other_flavorings_actual > 0:
                additional_other_flavorings_pool = unlocked_other_flavorings[~unlocked_other_flavorings['name'].isin(selected_names_so_far)]
                additional_other_flavorings_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_other_flavorings_pool['name']]
                selected_ingredients = selected_ingredients.append(additional_other_flavorings_pool.sample(n_additional_other_flavorings_actual, weights='neighbor_counts_xtreme'))
            if n_additional_foodstuffs_actual > 0:
                additional_foodstuffs_pool = unlocked_foodstuffs[~unlocked_foodstuffs['name'].isin(selected_names_so_far)]
                additional_foodstuffs_pool['neighbor_counts_xtreme'] = [valid_neighbor_counts.get(name, .1)**2 for name in additional_foodstuffs_pool['name']]
                selected_ingredients = selected_ingredients.append(additional_foodstuffs_pool.sample(n_additional_foodstuffs_actual, weights='neighbor_counts_xtreme'))

        selected_names = selected_ingredients['name'].tolist()

        selected_g = nx.Graph()
        selected_g.add_nodes_from(selected_names)

        for i_1, name_1 in enumerate(selected_names[:-1]):
            for i_2, name_2 in enumerate(selected_names[i_1+1:], i_1+1):
                connection = selected_ingredients[name_1][name_2]

                # Weights super guess-y
                if connection[0] == 'c':
                    selected_g.add_edge(name_1, name_2, length=1, weight=.3) # prev .8
                elif connection[0] == 'd':
                    # pairs_with_demerit = .5 # prev .6666
                    selected_g.add_edge(name_1, name_2, length=.7, weight=.6) # prev .8
                elif connection[0] == 'C':
                    # pairs_with_demerit = .4 # prev .5333
                    selected_g.add_edge(name_1, name_2, length=.6, weight=.7) # prev .8
                elif connection[0] == 'D':
                    # pairs_with_demerit = .3 # prev. .4
                    selected_g.add_edge(name_1, name_2, length=.3, weight=1) # prev .8

        # Try again, friend
        if not nx.is_connected(selected_g):
            print(str(iteration)+': NOT CONNECTED; SKIPPING TO NEXT ITERATION')
            continue

        score = 0

        # CONNECTED PAIRING BONUS ==============================================
        # I want this to be VERY important. I feel this holds a lot of the strength of recipe,
        # and also encompasses strength-ness and locked-ness
        # ranges from roughly (0 to 1) * 5, tho could be a lil over or under that range
        average_shortest_path_length = nx.average_shortest_path_length(selected_g, weight='length')
        # average_shortest_path_score = 1 / average_shortest_path_length * 1.2 - 1.1 # normalizes full house
        pairing_score = 1 / average_shortest_path_length * 1.5 - 1.3 # normalizes small pool (& doesn't do bad w full house)
        score += pairing_score * 3
        # print('AVERAGE SHORTEST PATH SCORE', average_shortest_path_score)

        # Used for both strength and locked bonus:
        node_degrees = list(selected_g.degree(weight='weight'))
        average_degree = sum([node_degree[1] for node_degree in node_degrees]) / len(node_degrees)

        # STRENGTH BONUS =======================================================
        strength_above_average = 0
        for node_degree in node_degrees:
            if selected_ingredients['strong'][node_degree[0]] == 'Y':
                strength_above_average += (node_degree[1] - average_degree)
            elif selected_ingredients['strong'][node_degree[0]] == 'y':
                strength_above_average += (node_degree[1] - average_degree) * .5
        strength_score = strength_above_average * .2 + .5 # reasonable for small and full pools
        # print('STRENGTH SCORE', strength_score)
        score += strength_score

        if len(locked) > 0:
            # LOCKED BONUS =========================================================
            locked_above_average = 0
            for node_degree in node_degrees:
                if node_degree[0] in locked_names:
                    # print(node_degree[1])
                    locked_above_average += node_degree[1] - average_degree
            locked_score = locked_above_average * .3 + 1 # close enough (has to cover few locked, lotta locked, small pool, big pool - yeesh.)
            # print('LOCKED SCORE', locked_score)
        else:
            locked_score = 0
        score += locked_score * 2
        # FLAVOR BALANCE BONUS =================================================
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
        flavor_score = flavor_score * .2 - 1.3 # yields reasonable scores w full or small pool

        score += flavor_score * 2
        # print('FLAVOR SCORE', flavor_score)

        # FOOD GROUPS BONUS ==========================================================================================
        # if 'y' in selected_ingredients['stir_fry_protein'].values:
        #     protein_score = .5
        # else:
        #     protein_score = 0
        #
        # if 'y' in selected_ingredients['stir_fry_fruit'].values:
        #     fruit_score = .5
        # else:
        #     fruit_score = 0
        #
        # food_group_score = protein_score + fruit_score
        n_protein = (selected_ingredients['stir_fry_protein'] == 'y').sum()
        n_fruit = (selected_ingredients['stir_fry_fruit'] == 'y').sum()
        n_grain = (selected_ingredients['stir_fry_grain'] == 'y').sum()
        n_leafy = (selected_ingredients['veg_leafy'] == 'y').sum()

        food_group_score = .5

        if n_protein in range(1, 3):
            food_group_score += .25
        if n_protein == 3:
            food_group_score -= .25
        if n_protein > 3:
            food_group_score -= .5

        if n_fruit == 1:
            food_group_score += .25
        if n_fruit > 2:
            food_group_score -= .5

        if n_grain > 1:
            food_group_score -= .25
        if n_grain > 2:
            food_group_score -= .5

        if n_leafy > 1:
            food_group_score -= .25
        if n_leafy > 2:
            food_group_score -= .5

        score += food_group_score
        # print('FOOD GROUP SCORE', food_group_score)

        # print()
        if top_score == None or score > top_score:
            top_selected_ingredients = selected_ingredients
            top_pairing_score = pairing_score
            top_strength_score = strength_score
            top_locked_score = locked_score
            top_flavor_score = flavor_score
            top_food_group_score = food_group_score
            top_score = score

    if top_score:
        data = {
            'outcome': 'success',
            'data': {
                'present_names': present_names,
                'locked_names': locked_names,
                'generated_names': top_selected_ingredients['name'][~top_selected_ingredients['name'].isin(locked_names)].tolist(),
                'pairing_bonus': top_pairing_score,
                'strength_bonus': top_strength_score,
                'locked_bonus': top_locked_score,
                'flavor_bonus': top_flavor_score,
                'food_group_bonus': top_food_group_score,
                'score': top_score,
                'selected_names': top_selected_ingredients['name'].tolist(),
            },
        }
    else:
        data = {
            'outcome': 'failure',
            'message': "Darn! The generator isn't coming up with anything for these ingredients.",
        }
    return(jsonify(data))
