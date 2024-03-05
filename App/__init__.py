from flask import Flask, render_template, redirect, request
from flask import logging as flog

import logging
from log import CustomFormatter

from App.RAG import do_search

app = Flask(__name__, static_folder='static')

app.logger.setLevel(0)
flog.default_handler.setFormatter(CustomFormatter())
app.logger.setLevel(logging.INFO)

@app.route("/", methods=['GET'])
def index() -> str:
    return render_template('index.html')

@app.route("/gerar", methods=['GET', 'POST'])
def gerar() -> str:

    if request.method == 'POST':
        query = request.form['query']
        roupas = do_search(query)
        print(roupas)
        return render_template('gerar.html', estado="carregando", roupas=roupas)

    return redirect('/')