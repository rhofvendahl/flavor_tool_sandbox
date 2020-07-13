from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

import pandas as pd
import networkx as nx
import os
import random

root_path = os.getcwd()
salad_flavor_data = pd.read_pickle(os.path.join(root_path, 'data/salad_flavor_data.pickle'))
stir_fry_flavor_data = pd.read_pickle(os.path.join(root_path, 'data/stir_fry_flavor_data.pickle'))

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

    n_iterations = len(present_names)*2
    top_score = 0
    for try_i in range(n_iterations):
        n_subgraphs = 2
        while n_subgraphs > 1: # keep shuffling until you get a well connected graph

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

            G = nx.Graph()
            G.add_nodes_from(selected_names)
            G.add_edges_from(lower_category_pairs, length=2)
            G.add_edges_from(lower_direct_pairs, length=1.5)
            G.add_edges_from(upper_category_pairs, length=1.2)
            G.add_edges_from(upper_direct_pairs, length=1)
            n_subgraphs = len(list(nx.connected_components(G)))

        score = 0

    # PAIRING BONUS ============================================================================================
        # ranges from roughly (0 to 1) * 3, tho could be a lil over or under that range
        average_shortest_path_length = nx.average_shortest_path_length(G, weight='length')
        average_shortest_path_score = 1 / average_shortest_path_length * 4 - 1
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

        # each varies from roughly .5 to 1
        sweet_score = (n_sweet_lower/2 + n_sweet_upper)/5
        salty_score = (n_salty_lower/2 + n_salty_upper)*2/5
        sour_score = (n_sour_lower/2 + n_sour_upper)*2/5
        savory_score = (n_savory_lower/2 + n_savory_upper)*3/5
        bitter_score = (n_bitter_lower/2 + n_bitter_upper)*3/5
        spicy_score = (n_spicy_lower/2 + n_spicy_upper)*2/5

        flavor_balance_score = 5 / (1 + abs(1-sweet_score) + abs(1-salty_score) + abs(1-sour_score) + abs(1-savory_score) + abs(1-spicy_score)) - 1.2
        score += flavor_balance_score

    # TEXTURE BALANCE BONUS ============================================================================================
        # ranges from roughly (0 to 1) * .75
        n_crunchy_lower = (selected_ingredients['salad_crunchy'] == 'y').sum()
        n_crunchy_upper = (selected_ingredients['salad_crunchy'] == 'Y').sum()
        n_chewy_lower = (selected_ingredients['salad_chewy'] == 'y').sum()
        n_chewy_upper = (selected_ingredients['salad_chewy'] == 'Y').sum()
        n_juicy_lower = (selected_ingredients['salad_juicy'] == 'y').sum()
        n_juicy_upper = (selected_ingredients['salad_juicy'] == 'Y').sum()

        # each ranges from roughly 0 to 1
        crunchy_score = (n_crunchy_lower/2 + n_crunchy_upper)/3
        chewy_score = (n_chewy_lower/2 + n_chewy_upper)
        juicy_score = (n_juicy_lower/2 + n_juicy_upper)/3

        texture_balance_score = 5 / (1 + abs(1-crunchy_score) + abs(1-chewy_score) + abs(1-juicy_score)) - 1.25
        score += texture_balance_score * .75

    # will bias toward larger salads, slightly
    # seems like it's hard to balance food groups on top of everything else. pity the scores aren't more independent
    # FOOD GROUP BALANCE BONUS =========================================================================================
        # ranges from roughly (0 to 1) * 2
        n_fruit = (selected_ingredients['fruit'] == 'y').sum()
        n_veg = (selected_ingredients['veg'] == 'y').sum()
        n_protein = (selected_ingredients['protein'] == 'y').sum()

        # /2 for steep diminishing returns (?)
        fruit_score = (n_fruit/2)**.5
        veg_score = (n_veg/2)**.5
        protein_score = (n_protein/2)**.5 #(0->0, 1->1, 4->2, 9->3)
        food_group_balance_score = (3*fruit_score + veg_score + 2*protein_score) * .22 - .33
        score += food_group_balance_score * 2

        if score > top_score:
            top_selected_ingredients = selected_ingredients
            top_pairing_bonus = average_shortest_path_score * 3
            top_clash_penalty = all_clashing_pairs_score * -1.5
            top_flavor_balance_bonus = flavor_balance_score
            top_texture_balance_bonus = texture_balance_score * .75
            top_food_group_balance_bonus = food_group_balance_score * 2
            top_score = score

    data = {
        'present_names': present_names,
        'selected_names': top_selected_ingredients['name'].tolist(),
        'locked_names': locked_names,
        'generated_names': top_selected_ingredients['name'][~top_selected_ingredients['name'].isin(locked_names)].tolist(),
        'pairing_bonus': top_pairing_bonus,
        'clash_penalty': top_clash_penalty,
        'flavor_balance_bonus': top_flavor_balance_bonus,
        'texture_balance_bonus': top_texture_balance_bonus,
        'food_group_balance_bonus': top_food_group_balance_bonus,
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
    stir_fry_data.reset_index(inplace=True)

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

    n_iterations = len(present_names)*2
    top_score = 0
    for try_i in range(n_iterations):
        n_subgraphs = 2
        while n_subgraphs > 1: # keep shuffling until you get a well connected graph
            n_gen_other_flavorings = min(random.randrange(n_gen_other_flavorings_min, n_gen_other_flavorings_max+1), len(the_rest_other_flavorings))
            n_gen_foodstuffs = min(random.randrange(n_gen_foodstuffs_min, n_gen_foodstuffs_max+1), len(the_rest_foodstuffs))

            selected_salts = locked_salts.append(the_rest_salts.sample(n_gen_salts))
            selected_fat_oils = locked_fat_oils.append(the_rest_fat_oils.sample(n_gen_fat_oils))
            selected_other_flavorings = locked_other_flavorings.append(the_rest_other_flavorings.sample(n_gen_other_flavorings))
            selected_foodstuffs = locked_foodstuffs.append(the_rest_foodstuffs.sample(n_gen_foodstuffs))
            selected_ingredients = selected_salts.append(selected_fat_oils).append(selected_other_flavorings).append(selected_foodstuffs)
            selected_names = selected_ingredients['name'].values.tolist()

            lower_category_pairs = []
            lower_direct_pairs = []
            upper_category_pairs = []
            upper_direct_pairs = []

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
            lower_pairs = lower_category_pairs + lower_direct_pairs
            upper_pairs = upper_category_pairs + upper_direct_pairs
            all_pairs = lower_pairs + upper_pairs
            G = nx.Graph()
            G.add_nodes_from(selected_names)
            G.add_edges_from(lower_category_pairs, length=2)
            G.add_edges_from(lower_direct_pairs, length=1.5)
            G.add_edges_from(upper_category_pairs, length=1.2)
            G.add_edges_from(upper_direct_pairs, length=1)
            n_subgraphs = len(list(nx.connected_components(G)))
        score = 0

    # PAIRING BONUS ============================================================================================
    # ranges from roughly (0 to 1) * 3, tho could be a lil over or under that range
        average_shortest_path_length = nx.average_shortest_path_length(G, weight='length')
        average_shortest_path_score = 1 / average_shortest_path_length * 4 - 1
    #     print(average_shortest_path_score)
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

        # each varies from roughly .5 to 1 (normalized to the average flavor score)
        sweet_score = (n_sweet_lower/2 + n_sweet_upper)/6
        salty_score = (n_salty_lower/2 + n_salty_upper)/4
        sour_score = (n_sour_lower/2 + n_sour_upper)/2.5
        savory_score = (n_savory_lower/2 + n_savory_upper)/3
        bitter_score = (n_bitter_lower/2 + n_bitter_upper)/3
        spicy_score = (n_spicy_lower/2 + n_spicy_upper)/3

        flavor_balance_score = 5 / (1 + abs(1-sweet_score) + abs(1-salty_score) + abs(1-sour_score) + abs(1-savory_score) + abs(1-spicy_score)) - .9
        score += flavor_balance_score

    # # will bias toward larger stir_frys, slightly
    # # PROTEIN BONUS =========================================================================================
    # # ranges from roughly (0 to 1) * .5 (mostly balanced on its own)
    #     n_protein = (selected_ingredients['stir_fry_protein'] == 'y').sum()
    #
    #     # /2 for steep diminishing returns (?)
    #     protein_score = (n_protein/2)**.5 * .75
    #     score += protein_score * .5

        if score > top_score:
            top_selected_ingredients = selected_ingredients
            top_pairing_bonus = average_shortest_path_score
            top_flavor_balance_bonus = flavor_balance_score
            # top_protein_bonus = protein_score
            top_score = score

    data = {
        'present_names': present_names,
        'selected_names': top_selected_ingredients['name'].tolist(),
        'locked_names': locked_names,
        'generated_names': top_selected_ingredients['name'][~top_selected_ingredients['name'].isin(locked_names)].tolist(),
        'pairing_bonus': top_pairing_bonus,
        'flavor_balance_bonus': top_flavor_balance_bonus,
        # 'protein_bonus': top_protein_bonus,
        'score': top_score
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run()
