"""Dependency-free browser interface for the Vega programming language."""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lexer import LexerError, tokenize
from src.parser import ParserError, parse
from src.transpiler import transpile

STARTER_SOURCE = 'sayisal sayim = 10\nyazdir sayim\n\nyazdir "Merhaba Vega!"\n'

PAGE = """<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Vega Studio</title>
<style>
:root{--paper:#f4f1ea;--ink:#252321;--muted:#746f68;--line:#ddd7cc;--accent:#c85b3d;--dark:#202629;--green:#172b2b}*{box-sizing:border-box}body{margin:0;min-height:100vh;background:var(--paper);color:var(--ink);font:14px Georgia,serif}header{display:flex;justify-content:space-between;align-items:end;gap:24px;padding:28px 5vw 18px}.eyebrow{margin:0 0 5px;color:var(--accent);font:700 12px Arial,sans-serif;letter-spacing:2px}h1{margin:0;font-size:clamp(26px,4vw,44px);line-height:1}.actions{display:flex;flex-wrap:wrap;gap:8px}button{border:1px solid var(--line);background:#fffdf8;color:var(--ink);padding:10px 14px;cursor:pointer;font:600 13px Arial,sans-serif}button:hover{border-color:var(--accent);color:var(--accent)}button.primary{border-color:var(--accent);background:var(--accent);color:white}main{display:grid;grid-template-columns:minmax(0,3fr) minmax(280px,2fr);gap:18px;padding:0 5vw 18px;min-height:calc(100vh - 150px)}.column{display:flex;min-height:0;flex-direction:column}.label{margin:0 0 8px;color:var(--muted);font:700 11px Arial,sans-serif;letter-spacing:1.5px}textarea,pre{margin:0;width:100%;flex:1;min-height:400px;border:0;resize:none;padding:20px;font:14px/1.65 "DejaVu Sans Mono",monospace}textarea{background:var(--dark);color:#f4eee4;outline:2px solid transparent}textarea:focus{outline-color:var(--accent)}pre{overflow:auto;white-space:pre-wrap;background:var(--green);color:#d8f1e4}.input{margin-top:12px;padding:14px;background:#20403c;color:#9ecbb4;font:700 11px Arial,sans-serif;letter-spacing:1px}input{display:block;width:100%;margin-top:7px;border:0;padding:10px;background:#2b514b;color:white;outline:0;font:14px Arial,sans-serif}footer{display:flex;justify-content:space-between;padding:0 5vw 20px;color:var(--muted);font:12px Arial,sans-serif}@media(max-width:800px){header{align-items:start;flex-direction:column}main{grid-template-columns:1fr}textarea,pre{min-height:300px}}
</style></head><body>
<header><div><p class="eyebrow">VEGA / STUDIO</p><h1>Dilinle düşün, anında çalıştır.</h1></div><div class="actions"><button onclick="newFile()">Yeni</button><button onclick="openFile()">Aç</button><button onclick="saveFile()">Kaydet</button><button class="primary" onclick="runCode()">Çalıştır ▶</button></div></header>
<main><section class="column"><p class="label">VEGA KODU</p><textarea id="source" spellcheck="false"></textarea></section><section class="column"><p class="label">PYTHON ÇIKTISI / PROGRAM SONUCU</p><pre id="output"></pre><label class="input">GİRDİ<input id="stdin" placeholder="veri komutu için değer"></label></section></main><footer><span id="status">Hazır</span><button onclick="clearOutput()">Çıktıyı temizle</button></footer><input id="filePicker" type="file" accept=".veg" hidden>
<script>const source=document.getElementById('source'),output=document.getElementById('output'),status=document.getElementById('status');const starter=__STARTER__;source.value=starter;function setStatus(t){status.textContent=t}function clearOutput(){output.textContent='';setStatus('Çıktı temizlendi')}function newFile(){source.value=starter;setStatus('Yeni Vega dosyası')}function openFile(){document.getElementById('filePicker').click()}document.getElementById('filePicker').onchange=e=>{const f=e.target.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{source.value=r.result;setStatus('Dosya açıldı: '+f.name)};r.readAsText(f)};function saveFile(){const b=new Blob([source.value],{type:'text/plain'}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='program.veg';a.click();URL.revokeObjectURL(a.href);setStatus('Dosya indirildi')}async function runCode(){setStatus('Çalıştırılıyor...');output.textContent='';try{const r=await fetch('/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source:source.value,input:document.getElementById('stdin').value})});const x=await r.json();output.textContent=x.output;setStatus(x.ok?'Başarıyla çalıştı':'Derleme veya çalıştırma hatası')}catch(e){output.textContent='Sunucuya bağlanılamadı: '+e;setStatus('Bağlantı hatası')}}source.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter')runCode()});</script></body></html>"""


def compile_source(source: str) -> str:
    return transpile(parse(tokenize(source)))


def friendly_error(error: str) -> str:
    if "Expected a statement" in error or "found 'ekle'" in error:
        return "Komut bulunamadı: 'ekle' tek başına kullanılamaz.\n\nÖrnek:\nliste sayilar = liste.yeni 1\nsayilar.ekle 2"
    return error


class VegaHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if urlparse(self.path).path != "/":
            self.send_error(404)
            return
        body = PAGE.replace("__STARTER__", json.dumps(STARTER_SOURCE)).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length))
            code = compile_source(data.get("source", ""))
            result = subprocess.run([sys.executable, "-c", code], input=data.get("input", ""), capture_output=True, text=True, cwd=PROJECT_ROOT, check=False)
            output = code + "\n--- çıktı ---\n" + result.stdout + ("\n[stderr]\n" + result.stderr if result.stderr else "")
            response = {"ok": result.returncode == 0, "output": output}
        except (LexerError, ParserError, ValueError, json.JSONDecodeError) as error:
            response = {"ok": False, "output": friendly_error(str(error))}
        body = json.dumps(response, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8765), VegaHandler)
    print("Vega Studio: http://127.0.0.1:8765")
    threading.Timer(0.3, lambda: webbrowser.open("http://127.0.0.1:8765")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
