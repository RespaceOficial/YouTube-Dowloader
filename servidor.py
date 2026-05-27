import os
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app) 

@app.route('/')
def site():
    return send_file('index.html')

@app.route('/download', methods=['POST'])
def baixar_video():
    dados = request.json
    link = dados.get('link')
    qualidade = dados.get('format')

    if not link:
        return jsonify({"erro": "Link vazio!"}), 400

    print(f"[*] Baixando na nuvem... Link: {link}")

    # Cria uma pasta temporária (assim não sujamos o servidor que vai nos hospedar)
    temp_dir = tempfile.gettempdir()
    
    ydl_opts = {
        'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
        'quiet': True
    }

    if qualidade == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif qualidade == '1080p':
        ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    elif qualidade == '720p':
        ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    elif qualidade == '480p':
        ydl_opts['format'] = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Puxa as infos para saber o nome exato do arquivo que o yt-dlp gerou
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            
            # Ajuste caso seja mp3 (o yt-dlp converte no final, mudando a extensão)
            if qualidade == 'mp3':
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        print(f"[*] Enviando arquivo para o usuário: {filename}")
        
        # O Pulo do Gato: Envia o arquivo como anexo pela rede!
        return send_file(filename, as_attachment=True)
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

