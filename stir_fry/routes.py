# TODO load ingredients from pickle, or something

from flask import Flask, render_template, request, jsonify, redirect, url_for, Blueprint
blueprint  = Blueprint('stir_fry', __name__, url_prefix='/stir-fry', template_folder='templates', static_folder='static/stir_fry')

import pandas as pd
import networkx as nx
import os
import random
import pickle
import time

root_path = os.getcwd()
stir_fry_flavor_data = pd.read_pickle(os.path.join(root_path, 'data/stir_fry_flavor_data_with_umbrella.pickle'))

@blueprint.route('/')
def index():
    return render_template('stir_fry/index.html')

@blueprint.route('/get-ingredients', methods=['GET'])
def get_ingredients():
    ingredients = [
        {
            col_name: row[col_name]
        for col_name in stir_fry_flavor_data.columns.tolist()}
    for i, row in stir_fry_flavor_data.iterrows()]
    return jsonify(ingredients)