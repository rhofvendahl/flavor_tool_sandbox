from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import pandas as pd
import os

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_salad_ingredients')
def parse():
    # salad_data_requested = request.args.get('salad')
    # stir_fry_data_requested = request.args.get('stir_fry')

    root_path = os.getcwd()
    salad_flavor_data = pd.read_pickle(os.path.join(root_path, 'data/salad_flavor_data.pickle'))
    salad_ingredients = [
        {
            col_name: row[col_name]
        for col_name in salad_flavor_data.columns.tolist()}
    for i, row in salad_flavor_data.iterrows()]
    # for name in salad_flavor_data[salad_flavor_data['veg'] == 'y']['name']:
    #     print(name)
    return jsonify(salad_ingredients)

if __name__ == "__main__":
    app.run()
