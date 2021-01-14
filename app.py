from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.before_request
def force_https():
    if 'www.flavortool.com' in request.url and not request.is_secure:
        return redirect(request.url.replace('http://', 'https://'))

import salad

import stir_fry

if __name__ == "__main__":
    app.run()
