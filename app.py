import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime
import xml.etree.ElementTree as ET

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def txt_para_rss(arquivo_txt, arquivo_xml, titulo_feed, link_feed, descricao_feed):
    """(Código de conversão txt para rss, como antes)"""
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")

    ET.SubElement(channel, "title").text = titulo_feed
    ET.SubElement(channel, "link").text = link_feed
    ET.SubElement(channel, "description").text = descricao_feed
    ET.SubElement(channel, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

    with open(arquivo_txt, "r") as f:
        for linha in f:
            dados = linha.strip().split(";")
            if len(dados) >= 4:
                codigo, produto, preco, unidade = dados[:4]

                item = ET.SubElement(channel, "item")
                ET.SubElement(item, "title").text = produto
                ET.SubElement(item, "link").text = f"https://seusite.com/produtos/{codigo}"
                ET.SubElement(item, "description").text = f"{produto} - R${preco}/{unidade}"
                ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
                ET.SubElement(item, "guid").text = codigo

    tree = ET.ElementTree(root)
    tree.write(arquivo_xml, encoding="utf-8", xml_declaration=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            txt_para_rss(file_path, 'feed.xml', 'Carnes Nobres', 'https://seusite.com/feed', 'Lista de Carnes Nobres e seus preços.')
            return 'Arquivo TXT recebido e feed RSS atualizado!'
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)