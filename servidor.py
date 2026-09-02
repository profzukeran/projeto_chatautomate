import asyncio
import websockets
import json


# ==========================================
# LISTA DE CLIENTES CONECTADOS
# ==========================================

clientes = {}


# ==========================================
# SERVIDOR WEBSOCKET
# ==========================================

async def servidor(websocket):

    # Verifica quantos clientes estão conectados

    if len(clientes) >= 2:

        await websocket.send(
            json.dumps({
                "tipo": "sistema",
                "mensagem": "Servidor cheio. Apenas duas IAs são permitidas."
            })
        )

        await websocket.close()

        return


    # Define o nome da IA

    if "IA A" not in clientes.values():

        nomeIA = "IA A"

    else:

        nomeIA = "IA B"


    # Guarda o cliente

    clientes[websocket] = nomeIA


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

        # Aguarda mensagens

        async for mensagem in websocket:

            print(
                nomeIA,
                "enviou:",
                mensagem
            )


            # Cria a mensagem estruturada

            dados = {
                "tipo": "mensagem",
                "remetente": nomeIA,
                "mensagem": mensagem
            }


            mensagem_json = json.dumps(
                dados
            )


            # Envia para os outros clientes

            for cliente in clientes:

                if cliente != websocket:

                    await cliente.send(
                        mensagem_json
                    )


    except websockets.exceptions.ConnectionClosed:

        print(
            nomeIA,
            "desconectada."
        )


    finally:

        # Remove o cliente

        if websocket in clientes:

            del clientes[websocket]


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
    print("Porta: 8765")
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

asyncio.run(main())