from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class IAHandler(SimpleHTTPRequestHandler):
    """Servidor HTTP que abre uma página específica para cada IA."""

    def __init__(self, *args, pagina, directory=None, **kwargs):
        self.pagina = pagina
        super().__init__(*args, directory=directory, **kwargs)

    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]

        if path in ("", "/"):
            path = f"/{self.pagina}"

        return super().translate_path(path)


def iniciar_servidor_http(porta, pagina):
    handler = partial(IAHandler, pagina=pagina, directory=BASE_DIR)
    servidor = ThreadingHTTPServer(("0.0.0.0", porta), handler)

    print("--------------------------------")
    print(f"Servidor HTTP da {pagina.replace('.html', '')} iniciado")
    print(f"URL: http://localhost:{porta}/")
    print("--------------------------------")

    servidor.serve_forever()
