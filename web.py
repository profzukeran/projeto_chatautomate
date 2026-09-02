from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer


PORTA = 8000


servidor = TCPServer(
    ("0.0.0.0", PORTA),
    SimpleHTTPRequestHandler
)


print("Servidor da página iniciado!")
print("Porta:", PORTA)


servidor.serve_forever()