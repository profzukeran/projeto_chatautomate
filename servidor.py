import asyncio
import websockets

# Lista que armazenará todos os clientes conectados
clientes = []


# Esta função será executada sempre que um cliente conectar
async def servidor(websocket):

    print("Novo cliente conectado.")

    clientes.append(websocket)

    try:

        # Aguarda mensagens desse cliente
        async for mensagem in websocket:

            print("Mensagem recebida:", mensagem)

            # Envia a mensagem para todos os outros clientes
            for cliente in clientes:

                if cliente != websocket:

                    await cliente.send(mensagem)

    except:

        print("Cliente desconectado.")

    finally:

        clientes.remove(websocket)


async def main():

    print("--------------------------------")

    print("Servidor iniciado")

    print("Porta: 8765")

    print("--------------------------------")

    async with websockets.serve(servidor, "0.0.0.0", 8765):

        await asyncio.Future()


asyncio.run(main())