from flask import Flask, render_template, redirect, request
from flask import logging as flog

import logging
import requests
from datetime import datetime

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    pink = "\x1b[0;35m"
    reset = "\x1b[0m"
    # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    # date = "%H:%M:%S"
    title = '%(asctime)s ' + pink + '| %(name)-5s' + reset
    format = ' :: %(levelname)-8s :: %(message)s'
    FORMATS = {
        logging.DEBUG: title + grey + format + reset,
        logging.INFO: title + blue + format + reset,
        logging.WARNING: title + yellow + format + reset,
        logging.ERROR: title + red + format + reset,
        logging.CRITICAL: title + bold_red + format + reset
    }

    def format(self, record):
        date = "%H:%M:%S"
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=date)
        return formatter.format(record)

class Roupa:

    @staticmethod
    def download_image(url, o) -> None:
        open(o, 'wb').write(requests.get(url))

    def __init__(self, href: str, titulo: str, valor: str, desc: str, parcela: str, imgs: list[str], colecao: str = None) -> None:
        self.href = href
        self.titulo = titulo
        self.valor = valor
        self.desc = desc
        self.colecao = colecao
        self.parcela = parcela
        self.imgs = imgs
    
    def save_str(self) -> str:
        to_s = f"""Roupa: {self.titulo}
Link: {self.href}
Valor: {self.valor}
Resumo: {self.desc}
Parcela: {self.parcela}
Imagens: {self.imgs}

"""
        return to_s
    
    def __repr__(self) -> str:
        return f'Roupa({self.titulo}, {self.valor}, {self.colecao})'

    @staticmethod
    def from_doc(doc: str) -> dict:
        import ast

        res = {}
        lines = doc.splitlines()
        for line in lines:
            if line.startswith("Imagens"):
                res['Imagens'] = ast.literal_eval(line.split(": ")[1])
                continue

            key, value = line.split(': ', 1)
            res[key] = value
        
        # print(res)
        return res
    
    @staticmethod
    def from_dict(dic):
        return Roupa(dic['Link'],
                     dic['Roupa'],
                     dic['Valor'],
                     dic['Resumo'],
                     dic['Parcela'],
                     dic['Imagens'])

app = Flask(__name__, static_folder='static')

app.logger.setLevel(0)
flog.default_handler.setFormatter(CustomFormatter())
app.logger.setLevel(logging.INFO)

@app.route("/", methods=['GET'])
def index() -> str:
    return render_template('index.html')

@app.route("/gerar", methods=['GET', 'POST'])
async def gerar() -> str:
    from App.RAG import pre_selecao, avaliar
    # from App.RAG import roupinha

    # if 1:
    if request.method == 'POST':
        query = request.form['query']
        roupas = pre_selecao(query)
        roupas = await avaliar(roupas, query)
        # roupas = [roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha, roupinha]
        print(roupas)
        return render_template('gerar.html', estado="carregando", roupas=roupas)

    return redirect('/')