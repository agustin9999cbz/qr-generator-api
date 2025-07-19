from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, HTMLResponse
import qrcode
import qrcode.image.svg
from io import BytesIO
import uvicorn
import webbrowser
import threading

app = FastAPI(
    title="Generador de QR",
    description="Una API para generar códigos QR personalizados",
    version="1.0"
)

@app.get("/", response_class=HTMLResponse, tags=["Visualizador"])
def visualizador():
    return """
    <html>
    <head>
      <title>QR Generator</title>
      <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; color: #222; }
        form { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px #ccc; width: 340px; margin: 30px auto; }
        input, select, button { margin: 8px 0; padding: 6px; width: 100%; border-radius: 4px; border: 1px solid #bbb; }
        button { background: #0078d7; color: #fff; border: none; cursor: pointer; }
        button:hover { background: #005fa3; }
        h2, h3 { text-align: center; }
        iframe { display: block; margin: 0 auto; background: #fff; }
        .manual { background: #fff; padding: 18px; border-radius: 8px; box-shadow: 0 2px 8px #ccc; width: 700px; margin: 30px auto; }
        ul { margin: 0 0 0 20px; }
      </style>
    </head>
    <body>
      <h2>Generador de QR</h2>
      <div class="manual">
        <h3>Manual de Uso</h3>
        <ul>
          <li><b>Texto:</b> Escribe el texto o URL que deseas codificar en el QR.</li>
          <li><b>Box size:</b> Tamaño de cada cuadro del QR (1 a 20).</li>
          <li><b>Border:</b> Grosor del borde (1 a 10).</li>
          <li><b>Fill color:</b> Color de los cuadros del QR (nombre en inglés o código HEX, ej: black, #000000).</li>
          <li><b>Back color:</b> Color de fondo (nombre en inglés o código HEX, ej: white, #ffffff).</li>
          <li><b>Formato:</b> Elige PNG o SVG.</li>
          <li><b>Descargar:</b> Marca para descargar el archivo en vez de solo previsualizarlo.</li>
        </ul>
        <p>Haz clic en "Generar QR" para ver la vista previa o descargar el código QR.</p>
      </div>
      <form method="get" action="/qr" target="qrframe">
        Texto: <input name="texto" required maxlength="500"><br>
        Box size: <input name="box_size" type="number" value="10" min="1" max="20"><br>
        Border: <input name="border" type="number" value="4" min="1" max="10"><br>
        Fill color: <input name="fill_color" value="black"><br>
        Back color: <input name="back_color" value="white"><br>
        Formato: <select name="format">
          <option value="png">PNG</option>
          <option value="svg">SVG</option>
        </select><br>
        Descargar: <input type="checkbox" name="download" value="true"><br>
        <button type="submit">Generar QR</button>
      </form>
      <h3>Vista previa:</h3>
      <iframe name="qrframe" style="width:300px;height:300px;border:1px solid #ccc;"></iframe>
      <p style="text-align:center;color:#888;">Docs automáticos en <a href="/docs" target="_blank">/docs</a></p>
    </body>
    </html>
    """

@app.get("/qr", tags=["Generador QR"])
def generar_qr(
    texto: str = Query(..., max_length=500),
    box_size: int = Query(10, ge=1, le=20),
    border: int = Query(4, ge=1, le=10),
    fill_color: str = Query("black"),
    back_color: str = Query("white"),
    format: str = Query("png", pattern="^(png|svg)$"),
    download: bool = Query(False)
):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(texto)
    qr.make(fit=True)

    buffer = BytesIO()

    if format.lower() == "svg":
        img = qr.make_image(image_factory=qrcode.image.svg.SvgImage, fill_color=fill_color, back_color=back_color)
        img.save(buffer)
        media_type = "image/svg+xml"
        file_ext = "svg"
    else:
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img.save(buffer, format="PNG")
        media_type = "image/png"
        file_ext = "png"

    buffer.seek(0)

    import time
    headers = {}
    if download:
        timestamp = int(time.time())
        headers["Content-Disposition"] = f"attachment; filename=qr_{timestamp}.{file_ext}"

    return StreamingResponse(buffer, media_type=media_type, headers=headers)

@app.get("/qr/params", tags=["Generador QR"])
def qr_params():
    return {
        "box_size": {"default": 10, "min": 1, "max": 20},
        "border": {"default": 4, "min": 1, "max": 10},
        "fill_color": {"default": "black"},
        "back_color": {"default": "white"},
        "format": {"default": "png", "options": ["png", "svg"]},
        "texto": {"max_length": 500}
    }


# ⬇️ Esto hace que se abra el navegador automáticamente
def abrir_navegador():
    webbrowser.open("http://127.0.0.1:8000/")

def abrir_navegador_docs():
    webbrowser.open("http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start()
    threading.Timer(1.7, abrir_navegador_docs).start()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
