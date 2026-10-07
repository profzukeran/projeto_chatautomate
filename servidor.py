import asyncio
import json
import os
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen

import websockets


# ==========================================
# LISTA DE CLIENTES CONECTADOS
# ==========================================

clientes = {}
clientes_lock = asyncio.Lock()
historicos = {"IA A": [], "IA B": []}
tarefa_conversa = None

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/chat"
)
OLLAMA_MODEL_PADRAO = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_MODELS = {
    "IA A": os.getenv("OLLAMA_MODEL_IA_A", OLLAMA_MODEL_PADRAO),
    "IA B": os.getenv("OLLAMA_MODEL_IA_B", OLLAMA_MODEL_PADRAO),
}
MAX_AGENT_TURNS = int(os.getenv("MAX_AGENT_TURNS", "6"))

PROMPTS = {
    "IA A": (
        "Você é a IA A. Converse em português de portugal a IA B. "
        "Apresente ideias próprias, responda ao que a outra IA disse e "
        "mantenha cada resposta concisa."
        "respostas curtas"
        "perguntas curtas"
    ),
    "IA B": (
        "Você é a IA B. Converse em português brasileiro com a IA A. "
        "Analise criticamente as ideias recebidas, acrescente perspectivas "
        "novas e mantenha cada resposta concisa."
        "respostas curtas"
        "perguntas curtas"
    ),
}


async def publicar(dados):

    mensagem = json.dumps(dados, ensure_ascii=False)

    for cliente in tuple(clientes):

        try:
            await cliente.send(mensagem)
        except websockets.exceptions.ConnectionClosed:
            pass


def consultar_ollama(modelo, prompt_sistema, mensagens):

    payload = {
        "model": modelo,
        "stream": False,
        "messages": [
            {"role": "system", "content": prompt_sistema},
            *mensagens,
        ],
    }

    requisicao = Request(
        OLLAMA_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(requisicao, timeout=120) as resposta:
        resultado = json.loads(resposta.read().decode("utf-8"))

    texto = resultado.get("message", {}).get("content", "").strip()

    if not texto:
        raise RuntimeError("O Ollama retornou uma resposta vazia.")

    return texto


def api_ia_a(mensagens):

    return consultar_ollama(
        OLLAMA_MODELS["IA A"],
        PROMPTS["IA A"],
        mensagens,
    )


def api_ia_b(mensagens):

    return consultar_ollama(
        OLLAMA_MODELS["IA B"],
        PROMPTS["IA B"],
        mensagens,
    )


APIS_IA = {
    "IA A": api_ia_a,
    "IA B": api_ia_b,
}


async def conduzir_conversa(tema, iniciador):

    global tarefa_conversa

    historicos["IA A"] = []
    historicos["IA B"] = []
    historicos[iniciador].append({"role": "user", "content": tema})

    await publicar({
        "tipo": "tema",
        "remetente": iniciador,
        "mensagem": tema,
    })

    ordem = [iniciador, "IA B" if iniciador == "IA A" else "IA A"]

    try:

        for turno in range(MAX_AGENT_TURNS):

            nome_ia = ordem[turno % 2]
            texto = await asyncio.to_thread(
                APIS_IA[nome_ia],
                list(historicos[nome_ia]),
            )

            historicos[nome_ia].append({
                "role": "assistant",
                "content": texto,
            })

            await publicar({
                "tipo": "mensagem",
                "remetente": nome_ia,
                "mensagem": texto,
            })

            proxima_ia = ordem[(turno + 1) % 2]
            historicos[proxima_ia].append({
                "role": "user",
                "content": f"{nome_ia} disse: {texto}",
            })

        await publicar({
            "tipo": "sistema",
            "mensagem": f"Conversa encerrada após {MAX_AGENT_TURNS} respostas.",
        })

    except Exception as erro:

        await publicar({
            "tipo": "sistema",
            "mensagem": f"Falha ao consultar o Ollama: {erro}",
        })

    finally:
        tarefa_conversa = None


# ==========================================
# SERVIDOR WEBSOCKET
# ==========================================

async def servidor(websocket):

    global tarefa_conversa

    request_obj = getattr(websocket, "request", None)
    caminho = request_obj.path if request_obj is not None and hasattr(request_obj, "path") else "/"

    params = parse_qs(
        urlparse(caminho).query
    )

    nome_solicitado = params.get("ia", [""])[0]

    async with clientes_lock:

        if nome_solicitado not in ["IA A", "IA B"]:
            entidades_livres = [
                nome for nome in ("IA A", "IA B")
                if nome not in clientes.values()
            ]

            if not entidades_livres:
                await websocket.send(json.dumps({
                    "tipo": "sistema",
                    "mensagem": "Servidor cheio. Apenas duas IAs são permitidas.",
                }, ensure_ascii=False))
                await websocket.close()
                return

            nome_solicitado = entidades_livres[0]

        websocket_anterior = next(
            (
                cliente for cliente, nome in clientes.items()
                if nome == nome_solicitado
            ),
            None,
        )

        if websocket_anterior is None and len(clientes) >= 2:
            await websocket.send(json.dumps({
                "tipo": "sistema",
                "mensagem": "Servidor cheio. Apenas duas IAs são permitidas.",
            }, ensure_ascii=False))
            await websocket.close()
            return

        if websocket_anterior is not None:
            clientes.pop(websocket_anterior, None)

        nomeIA = nome_solicitado
        clientes[websocket] = nomeIA

    if websocket_anterior is not None:
        await websocket_anterior.close(
            code=4001,
            reason="Substituída por uma nova conexão da mesma entidade",
        )



    print("--------------------------------")
    print(nomeIA, "conectada.")
    print("Clientes conectados:", len(clientes))
    print("--------------------------------")


    # Informa ao cliente qual IA ele é

    await websocket.send(
        json.dumps({
            "tipo": "identificacao",
            "nome": nomeIA
        })
    )


    try:

        async for mensagem in websocket:

            try:
                dados = json.loads(mensagem)
            except json.JSONDecodeError:
                dados = {"tipo": "iniciar_conversa", "tema": mensagem}

            if dados.get("tipo") != "iniciar_conversa":
                continue

            tema = str(dados.get("tema", "")).strip()

            if not tema:
                await websocket.send(json.dumps({
                    "tipo": "sistema",
                    "mensagem": "Digite um tema para iniciar a conversa.",
                }, ensure_ascii=False))
                continue

            if len(tema) > 1000:
                await websocket.send(json.dumps({
                    "tipo": "sistema",
                    "mensagem": "O tema deve ter no máximo 1000 caracteres.",
                }, ensure_ascii=False))
                continue

            if tarefa_conversa is not None and not tarefa_conversa.done():
                await websocket.send(json.dumps({
                    "tipo": "sistema",
                    "mensagem": "Já existe uma conversa em andamento.",
                }, ensure_ascii=False))
                continue

            tarefa_conversa = asyncio.create_task(
                conduzir_conversa(tema, nomeIA)
            )


    except websockets.exceptions.ConnectionClosed:

        print(
            nomeIA,
            "desconectada."
        )


    finally:

        # Remove o cliente

        async with clientes_lock:
            clientes.pop(websocket, None)


        print(
            "Clientes conectados:",
            len(clientes)
        )


# ==========================================
# INICIA O SERVIDOR
# ==========================================

async def main():

    print("--------------------------------")
    print("Servidor WebSocket iniciado")
    print(
        "Porta WebSocket: 8765 | "
        f"Ollama IA A: {OLLAMA_MODELS['IA A']} | "
        f"Ollama IA B: {OLLAMA_MODELS['IA B']}"
    )
    print("--------------------------------")


    async with websockets.serve(
        servidor,
        "0.0.0.0",
        8765
    ):

        await asyncio.Future()


# ==========================================
# EXECUTA O SERVIDOR
# ==========================================

if __name__ == "__main__":
    asyncio.run(main())