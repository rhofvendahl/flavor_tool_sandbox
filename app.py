# TODO resolve "clashing" thing in salad

from flask import Flask, render_template, request, jsonify, redirect, url_for
import salad.routes
import stir_fry.routes

# Importing these adds to main "routes". An alternative would be importing in __init__.py.
import stir_fry.routes_generate_fun
import stir_fry.routes_generate_reliable

app = Flask(
    __name__,
    # static_folder='static',
    # static_url_path='/static'
)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.register_blueprint(salad.routes.blueprint)
app.register_blueprint(stir_fry.routes.blueprint)
# app.register_blueprint(stir_fry.routes_generate.blueprint)
# app.register_blueprint(stir_fry.routes_generate_black_magic.blueprint)

print(salad.routes.blueprint.__dict__)
print()
print(stir_fry.routes.blueprint.__dict__)

@app.route('/')
def root():
    return redirect(url_for('stir_fry.index'))

@app.before_request
def force_https():
    if 'www.flavortool.com' in request.url and not request.is_secure:
        return redirect(request.url.replace('http://', 'https://'))

if __name__ == "__main__":
    app.run()
