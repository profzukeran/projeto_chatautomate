const chat = document.getElementById("chat");

const campo = document.getElementById("mensagem");

const enviar = document.getElementById("enviar");

const iniciar = document.getElementById("iniciar");

const parar = document.getElementById("parar");

const statusSistema = document.querySelector("header span");

function horario(){

    return new Date().toLocaleTimeString([],{

        hour:"2-digit",

        minute:"2-digit"

    });

}

function adicionarMensagem(autor,texto){

    const mensagem = document.createElement("div");

    mensagem.classList.add("mensagem");

    if(autor=="IA A"){

        mensagem.classList.add("iaA");

    }

    else{

        mensagem.classList.add("iaB");

    }

    const avatar = autor=="IA A" ? "🤖" : "🧠";

    mensagem.innerHTML = `

        <div class="avatar">

            ${avatar}

        </div>

        <div class="balao">

            <div class="nome">

                ${autor}

            </div>

            <div>

                ${texto}

            </div>

            <div class="hora">

                ${horario()}

            </div>

        </div>

    `;

    chat.appendChild(mensagem);

    chat.scrollTop = chat.scrollHeight;

}

enviar.onclick = ()=>{

    if(campo.value=="") return;

    adicionarMensagem("IA A",campo.value);

    campo.value="";

}

iniciar.onclick = ()=>{

    statusSistema.innerHTML="Status: Conversando";

    adicionarMensagem("IA A","Olá! Estou pronta para iniciar nossa conversa.");

}

parar.onclick = ()=>{

    statusSistema.innerHTML="Status: Conversa encerrada";

    adicionarMensagem("IA B","Até a próxima!");

}