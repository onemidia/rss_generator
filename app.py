import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Configurações de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuração da SECRET_KEY para evitar erro de sessão
app.secret_key = os.getenv("SECRET_KEY", "minha_chave_secreta")

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def txt_para_rss(arquivo_txt, arquivo_xml, titulo_feed, link_feed, descricao_feed):
    """Converte um arquivo TXT para um feed RSS."""
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
    print(f"Arquivo RSS gerado em: {os.path.abspath(arquivo_xml)}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Página inicial para upload de arquivos TXT."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("Nenhum arquivo enviado!")
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash("Nenhum arquivo selecionado!")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Gera o feed RSS atualizado
            rss_path = os.path.join(app.config['UPLOAD_FOLDER'], 'feed.xml')
            txt_para_rss(file_path, rss_path, 'Carnes Nobres', 'https://seusite.com/feed', 'Lista de Carnes Nobres e seus preços.')

            flash("Arquivo recebido e feed RSS atualizado!")
            return redirect(url_for('upload_file'))

    return render_template('index.html')

@app.route('/feed.xml')
def serve_rss_feed():
    """Servir o feed RSS sem cache, mesmo com parâmetros na URL."""
    response = make_response(send_from_directory(app.config['UPLOAD_FOLDER'], "feed.xml"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=10000)
