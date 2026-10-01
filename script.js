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

const iaAtual =
    window.IA_NOME &&
    ["IA A", "IA B"].includes(window.IA_NOME)
        ? window.IA_NOME
        : (
            window.location.port === "8001"
                ? "IA B"
                : "IA A"
        );

let nomeIA = iaAtual;


// ==========================================
// DESCOBRE AUTOMATICAMENTE O SERVIDOR
// ==========================================

let enderecoWebSocket;
const identificacao =
    `?ia=${encodeURIComponent(iaAtual)}`;

if (window.location.protocol === "https:") {

    const hostnameWebSocket =
        window.location.hostname.replace(
            /-800[01]\./,
            "-8765."
        );

    enderecoWebSocket =
        `wss://${hostnameWebSocket}/${identificacao}`;

}
else {

    enderecoWebSocket =
        `ws://${window.location.hostname}:8765/${identificacao}`;

}

const urlSocket = enderecoWebSocket;


console.log(
    "Servidor WebSocket:",
    urlSocket
);


// ==========================================
// CONEXÃO COM O WEBSOCKET
// ==========================================

let socket;
let temporizadorReconexao;

function conectarWebSocket() {

    const conexao = new WebSocket(urlSocket);
    socket = conexao;

    conexao.onopen = function () {

        status.textContent = "🟢 Conectado";
        console.log("Conectado ao servidor WebSocket.");

    };

    conexao.onmessage = receberMensagem;

    conexao.onerror = function (erro) {

        status.textContent = "🔴 Erro na conexão";
        console.error("Erro no WebSocket:", erro);

    };

    conexao.onclose = function () {

        if (socket !== conexao) {
            return;
        }

        status.textContent = "🟡 Reconectando...";
        console.log("WebSocket desconectado; tentando reconectar.");

        temporizadorReconexao = window.setTimeout(function () {

            if (socket === conexao) {
                conectarWebSocket();
            }

        }, 1500);

    };

}

conectarWebSocket();


// ==========================================
// QUANDO CONECTAR
// ==========================================

// ==========================================
// QUANDO RECEBER UMA MENSAGEM
// ==========================================

function receberMensagem(event) {

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


        if (dados.tipo === "tema") {

            adicionarMensagem(
                `Tema iniciado por ${dados.remetente}: ${dados.mensagem}`,
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

            const posicao =
                dados.remetente === iaAtual
                    ? "enviada"
                    : "recebida";


            adicionarMensagem(
                texto,
                posicao
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

}


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

    socket.send(JSON.stringify({
        tipo: "iniciar_conversa",
        tema: texto,
    }));


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