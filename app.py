import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Definição da chave secreta para usar flash messages
app.secret_key = os.getenv("SECRET_KEY", "minha_chave_secreta")

# Diretório de uploads temporários
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/uploads")  # No Render, usar /tmp para persistência temporária
FEED_PATH = os.path.join(UPLOAD_FOLDER, "feed.xml")  # Caminho correto do feed RSS

# Criar a pasta de uploads, se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def txt_para_rss(arquivo_txt, arquivo_xml, titulo_feed, link_feed, descricao_feed):
    """Converte um arquivo TXT em um feed RSS"""
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
    print(f"Arquivo RSS gerado em: {arquivo_xml}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("Nenhum arquivo enviado.")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("Nenhum arquivo selecionado.")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Gerar o feed RSS
            txt_para_rss(file_path, FEED_PATH, 'Carnes Nobres', 'https://seusite.com/feed.xml', 'Lista de Carnes Nobres e seus preços.')

            flash("Arquivo recebido e feed RSS atualizado!")
            return redirect(url_for('upload_file'))

    return render_template('index.html')

@app.route('/feed.xml')
def serve_rss_feed():
    """Servir o feed RSS"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], "feed.xml")

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))  # Usando a variável de ambiente PORT
