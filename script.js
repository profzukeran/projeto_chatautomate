// ==========================================
// ELEMENTOS DA PÁGINA
// ==========================================

const chat = document.getElementById("chat");

const campo = document.getElementById("mensagem");

const botaoEnviar = document.getElementById("enviar");

const status = document.getElementById("status");

const elementoNomeIA =
    document.getElementById("nomeIA");

const elementoDispositivo =
    document.getElementById("dispositivo");


// ==========================================
// NOME DA IA
// ==========================================

let nomeIA = "IA";


// ==========================================
// DESCOBRE AUTOMATICAMENTE O SERVIDOR
// ==========================================

// Verifica se estamos no Codespaces

let enderecoWebSocket;


// Se estiver usando HTTPS
// utiliza WSS

if (window.location.protocol === "https:") {

    // Pega o endereço atual da página
    // e troca a porta 8000 pela 8765

    enderecoWebSocket =
        "wss://" +
        window.location.hostname.replace(
            "-8000.",
            "-8765."
        );

}


// Se estiver usando HTTP local

else {

    enderecoWebSocket =
        "ws://localhost:8765";

}


console.log(
    "Servidor WebSocket:",
    enderecoWebSocket
);


// ==========================================
// CONEXÃO COM O WEBSOCKET
// ==========================================

const socket = new WebSocket(
    enderecoWebSocket
);


// ==========================================
// QUANDO CONECTAR
// ==========================================

socket.onopen = function () {

    status.textContent =
        "🟢 Conectado";

    console.log(
        "Conectado ao servidor WebSocket."
    );

};


// ==========================================
// QUANDO RECEBER UMA MENSAGEM
// ==========================================

socket.onmessage = function (event) {

    try {

        const dados =
            JSON.parse(event.data);


        // ==================================
        // IDENTIFICAÇÃO DA IA
        // ==================================

        if (dados.tipo === "identificacao") {

            nomeIA =
                dados.nome;


            if (elementoNomeIA) {

                elementoNomeIA.textContent =
                    nomeIA;

            }


            if (elementoDispositivo) {

                if (nomeIA === "IA A") {

                    elementoDispositivo.textContent =
                        "Dispositivo A";

                }

                else {

                    elementoDispositivo.textContent =
                        "Dispositivo B";

                }

            }


            console.log(
                "Esta conexão é:",
                nomeIA
            );


            return;

        }


        // ==================================
        // MENSAGEM DO SISTEMA
        // ==================================

        if (dados.tipo === "sistema") {

            adicionarMensagem(
                dados.mensagem,
                "sistema"
            );

            return;

        }


        // ==================================
        // MENSAGEM RECEBIDA
        // ==================================

        if (dados.tipo === "mensagem") {

            const texto =
                dados.remetente +
                ": " +
                dados.mensagem;


            adicionarMensagem(
                texto,
                "recebida"
            );

            return;

        }

    }

    catch (erro) {

        console.error(
            "Erro ao interpretar mensagem:",
            erro
        );

    }

};


// ==========================================
// QUANDO OCORRER UM ERRO
// ==========================================

socket.onerror = function (erro) {

    status.textContent =
        "🔴 Erro na conexão";

    console.error(
        "Erro no WebSocket:",
        erro
    );

};


// ==========================================
// QUANDO DESCONECTAR
// ==========================================

socket.onclose = function () {

    status.textContent =
        "🔴 Desconectado";

    console.log(
        "WebSocket desconectado."
    );

};


// ==========================================
// ADICIONA MENSAGEM NA TELA
// ==========================================

function adicionarMensagem(
    texto,
    tipo
) {

    const mensagem =
        document.createElement("div");


    mensagem.classList.add(
        "mensagem"
    );


    mensagem.classList.add(
        tipo
    );


    const balao =
        document.createElement("div");


    balao.classList.add(
        "balao"
    );


    balao.textContent =
        texto;


    mensagem.appendChild(
        balao
    );


    chat.appendChild(
        mensagem
    );


    // Mantém o chat na última mensagem

    chat.scrollTop =
        chat.scrollHeight;

}


// ==========================================
// ENVIA MENSAGEM
// ==========================================

function enviarMensagem() {

    const texto =
        campo.value.trim();


    // Não permite mensagem vazia

    if (texto === "") {

        return;

    }


    // Verifica a conexão

    if (
        socket.readyState !==
        WebSocket.OPEN
    ) {

        alert(
            "A conexão com o servidor ainda não foi estabelecida."
        );

        return;

    }


    // Envia somente o texto

    socket.send(
        texto
    );


    // Mostra a mensagem
    // no lado direito

    adicionarMensagem(
        nomeIA + ": " + texto,
        "enviada"
    );


    // Limpa o campo

    campo.value = "";


    // Volta o cursor para o campo

    campo.focus();

}


// ==========================================
// BOTÃO ENVIAR
// ==========================================

botaoEnviar.onclick =
    enviarMensagem;


// ==========================================
// TECLA ENTER
// ==========================================

campo.addEventListener(
    "keypress",
    function (event) {

        if (event.key === "Enter") {

            enviarMensagem();

        }

    }
);