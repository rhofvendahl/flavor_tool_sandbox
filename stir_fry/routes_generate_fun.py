from stir_fry.routes import *

@blueprint.route('/generate-fun', methods=['POST'])
def generate_fun():
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
    # present_fat_oils = stir_fry_data[stir_fry_data['stir_fry_fat_oil'] == 'y']
    # present_salts = stir_fry_data[stir_fry_data['stir_fry_salt'] == 'y']
    present_other_flavorings = stir_fry_data[(stir_fry_data['stir_fry_flavoring'] == 'y') & (stir_fry_data['stir_fry_salt'] != 'y')]
    present_foodstuffs = stir_fry_data[(stir_fry_data['stir_fry_fat_oil'] != 'y') & (stir_fry_data['stir_fry_salt'] != 'y') & (stir_fry_data['stir_fry_flavoring'] != 'y')] # why am I selecting not salt? already selecting not flavoring. don't wanna mess tho..
    # present_fat_oils_set = set(present_fat_oils['name'])
    # present_salts_set = set(present_salts['name'])
    # present_other_flavorings_set = set(present_other_flavorings['name'])
    # present_foodstuffs_set = set(present_foodstuffs['name'])

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
    # n_total_salts_actual = n_additional_salts_actual + len(locked_salts)

    n_additional_fat_oils_needed = max(n_fat_oils - len(locked_fat_oils), 0)
    n_additional_fat_oils_actual = min(n_additional_fat_oils_needed, len(unlocked_fat_oils))
    # n_total_fat_oils_actual = n_additional_fat_oils_actual + len(locked_fat_oils)

    n_additional_other_flavorings_needed_min = max(n_other_flavorings_min - len(locked_other_flavorings), 0)
    n_additional_other_flavorings_actual_min = min(n_additional_other_flavorings_needed_min, len(unlocked_other_flavorings))
    # n_total_other_flavorings_actual_min = n_additional_other_flavorings_actual_min + len(locked_other_flavorings)

    n_additional_other_flavorings_needed_max = max(n_other_flavorings_max - len(locked_other_flavorings), 0) # yikes, I had this as min..
    n_additional_other_flavorings_actual_max = min(n_additional_other_flavorings_needed_max, len(unlocked_other_flavorings))
    # n_total_other_flavorings_actual_max = n_additional_other_flavorings_actual_max + len(locked_other_flavorings)

    n_additional_foodstuffs_needed_min = max(n_foodstuffs_min - len(locked_foodstuffs), 0)
    n_additional_foodstuffs_actual_min = min(n_additional_foodstuffs_needed_min, len(unlocked_foodstuffs))
    # n_total_foodstuffs_actual_min = n_additional_foodstuffs_actual_min + len(locked_foodstuffs)

    n_additional_foodstuffs_needed_max = max(n_foodstuffs_max - len(locked_foodstuffs), 0)
    n_additional_foodstuffs_actual_max = min(n_additional_foodstuffs_needed_max, len(unlocked_foodstuffs))
    # n_total_foodstuffs_actual_max = n_additional_foodstuffs_actual_max + len(locked_foodstuffs)

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

