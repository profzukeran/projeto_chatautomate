import asyncio
import websockets

# Endereço do servidor
SERVIDOR = "ws://localhost:8765"

# Nome deste computador
NOME = "IA A"


async def receber_mensagens(websocket):

    try:

        async for mensagem in websocket:

            print("\n" + mensagem)
            print("Digite uma mensagem: ", end="")

    except websockets.exceptions.ConnectionClosed:

        print("\nConexão encerrada.")


async def enviar_mensagens(websocket):

    while True:

        mensagem = await asyncio.to_thread(
            input,
            "Digite uma mensagem: "
        )

        mensagem_completa = NOME + ": " + mensagem

        await websocket.send(mensagem_completa)


async def cliente():

    print("Conectando ao servidor...")

    async with websockets.connect(SERVIDOR) as websocket:

        print("Conectado ao servidor!")
        print("Você é:", NOME)

        await asyncio.gather(
            receber_mensagens(websocket),
            enviar_mensagens(websocket)
        )


asyncio.run(cliente())