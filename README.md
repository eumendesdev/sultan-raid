# Sultan - Bot de Raid para Discord

Sultan é um bot multifuncional para Discord, projetado para executar ações administrativas e de raid em servidores de forma eficiente e discreta. Ele é controlado por comandos seguros, operáveis tanto em canais de servidores quanto remotamente via Mensagens Diretas (DMs), com um sistema de logs detalhado e feedback em tempo real para o operador.

## ✨ Funcionalidades

- **Controle Remoto Seguro**: Execute todos os comandos a partir de sua DM, especificando o ID do servidor alvo, garantindo total discrição.
- **Sistema de Permissão**: Apenas usuários com IDs listados no arquivo `config.json` podem operar o bot, prevenindo o uso não autorizado.
- **Painel de Log em Tempo Real**: Em vez de spammar sua DM, o bot envia uma única mensagem de log que é editada em tempo real, mostrando o progresso de cada comando.
- **Feedback Profissional**: As notificações de início, sucesso ou erro são enviadas via *Discord embeds*, tornando a comunicação clara e organizada.
- **Modo Furtivo**: Comandos usados em canais de servidor são apagados instantaneamente para não deixar rastros.
- **Relatórios Detalhados**: Ao final de cada operação, o bot informa estatísticas precisas (canais criados, membros banidos, cargos deletados).

---

## ⚙️ Comandos

O prefixo padrão é `v!`.

| Comando | Ação | Uso no Servidor | Uso na DM |
| :--- | :--- | :--- | :--- |
| **`sultan`** | Cria um número configurável de canais de texto e os inunda com uma mensagem de spam. | `v!sultan` | `v!sultan <ID_DO_SERVIDOR>` |
| **`banall`** | Bane todos os membros do servidor (exceto o dono, o operador e o bot). | `v!banall` | `v!banall <ID_DO_SERVIDOR>` |
| **`kickall`**| Expulsa todos os membros possíveis do servidor. | `v!kickall` | `v!kickall <ID_DO_SERVIDOR>` |
| **`nuke`** | Deleta canais, cargos, emojis e cria um canal. | `v!nuke` | `v!nuke <ID_DO_SERVIDOR>` |
| **`renameall`**| Renomeia todos os membros para um nome específico. | `v!renameall [novo_nome]` | `v!renameall <ID_DO_SERVIDOR> [novo_nome]` |
| **`dmall`**| Envia uma mensagem privada para todos os membros do servidor. | `v!dmall <mensagem>` | `v!dmall <ID_DO_SERVIDOR> <mensagem>` |
| **`spamroles`**| Cria uma quantidade massiva de cargos. | `v!spamroles <qtd> [nome]` | *Não aplicável* |
| **`serveredit`**| Altera o nome do servidor. | `v!serveredit <novo_nome>` | `v!serveredit <ID> <novo_nome>` |
| **`renamechannels`**| Renomeia todos os canais do servidor. | `v!renamechannels [novo_nome]` | `v!renamechannels <ID> [novo_nome]` |
| **`giveroleall`**| Cria um cargo e o dá para todos. | `v!giveroleall [nome_cargo]` | `v!giveroleall <ID> [nome_cargo]` |
| **`stripallroles`**| Remove todos os cargos de todos os membros. | `v!stripallroles` | `v!stripallroles <ID_DO_SERVIDOR>` |
| **`serverlist`**| Lista todos os servidores onde o bot está. | *Apenas DM* | `v!serverlist` |
| **`help`**| Mostra a lista de comandos. | *Apenas DM* | `v!help` |
| **`nukebot`**| Faz o bot sair de todos os servidores. | *Apenas DM* | `v!nukebot` |
| **`cleandm`**| Limpa as DMs que o bot te enviou. | *Apenas DM* | `v!cleandm` |

---

## 🚀 Instalação e Configuração

Siga estes 5 passos para deixar seu bot pronto para uso.

### 1. Pré-requisitos
- Python 3.8 ou superior
- Uma conta no Discord

### 2. Instale as Dependências
Abra o terminal na pasta do projeto e execute:
```bash
pip install -r requirements.txt
```

### 3. Configure o Bot (`config.json`)
Abra o arquivo `config.json` e preencha os seguintes campos:

- `"token"`: O token secreto do seu bot. **Nunca compartilhe este token!**
- `"prefix"`: O prefixo que o bot usará para os comandos (ex: `v!`).
- `"perms"`: Uma lista de IDs de usuários do Discord que terão permissão para usar o bot.
- `"channel_name"`: O nome padrão para os canais criados pelo comando `sultan`.
- `"message_content"`: A mensagem que será enviada repetidamente nos canais criados.
- `"num_channels"`: O número de canais a serem criados pelo comando `sultan`.

**Exemplo de `config.json`:**
```json
{
    "token": "SEU_TOKEN_SUPER_SECRETO_AQUI",
    "prefix": "v!",
    "perms": ["SEU_ID_DE_USUARIO_AQUI", "ID_DE_OUTRO_USUARIO_AUTORIZADO"],
    "channel_name": "nome-canal",
    "message_content": "@here @everyone\n.gg/url-server",
    "num_channels": 50
}
```
> Para obter um ID de usuário, ative o Modo Desenvolvedor no Discord (`Configurações > Avançado`), clique com o botão direito no perfil de um usuário e selecione "Copiar ID do Usuário".

### 4. Crie a Aplicação no Discord
1. Vá para o **[Portal de Desenvolvedores do Discord](https://discord.com/developers/applications)** e crie uma "New Application".
2. Na aba **"Bot"**, clique em "Add Bot".
3. **Copie o Token** e cole-o no seu `config.json`.
4. **Ative as `Privileged Gateway Intents`**:
   - `SERVER MEMBERS INTENT`
   - `MESSAGE CONTENT INTENT`

   ![Intents](https://images.ctfassets.net/a364c9khexw9/3EU2g4bryuotzbkocgq6gE/e2b7630e783ac07157f2ed959cf81995/Picture_2.png)

### 5. Convide o Bot para o Servidor
1. Na aba **"OAuth2 > URL Generator"**, selecione as scopes `bot` e `applications.commands`.
2. Em **"Bot Permissions"**, marque a caixa **`Administrator`**. Isso garante que o bot terá todas as permissões necessárias para funcionar.
3. Copie a URL gerada e cole-a no seu navegador para convidar o bot para o servidor desejado.

---

## ▶️ Executando o Bot
Após concluir a configuração, inicie o bot executando o seguinte comando no terminal:
```bash
python bot.py
```
O terminal exibirá uma mensagem confirmando que o bot está online e pronto para receber comandos.

---

## ⚠️ Aviso

O uso de bots de raid é contra os Termos de Serviço do Discord e pode resultar no banimento da sua conta e da aplicação do bot. Este projeto foi desenvolvido para fins educacionais. Use por sua conta e risco.


