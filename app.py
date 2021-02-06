from flask import Flask, render_template, request, jsonify, redirect, url_for
from salad.salad import salad_blueprint
from stir_fry.stir_fry import stir_fry_blueprint

app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.register_blueprint(salad_blueprint)
app.register_blueprint(stir_fry_blueprint)

@app.route('/')
def root():
    return redirect(url_for('stir_fry_blueprint.stir_fry_index'))

@app.before_request
def force_https():
    if 'www.flavortool.com' in request.url and not request.is_secure:
        return redirect(request.url.replace('http://', 'https://'))

if __name__ == "__main__":
    app.run()
