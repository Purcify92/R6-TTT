import discord
import os
import random
import asyncio

# Define the roles and their probabilities for different numbers of players
ROLES = {
    3: {'Innocent': 0.33, 'Terrorist': 0.33, 'Detective': 0.33},
    4: {'Innocent': 0.5, 'Terrorist': 0.25, 'Detective': 0.25},
    5: {'Innocent': 0.4, 'Terrorist': 0.4, 'Detective': 0.2},
    6: {'Innocent': 0.4, 'Terrorist': 0.3, 'Detective': 0.3},
    7: {'Innocent': 0.4, 'Terrorist': 0.4, 'Detective': 0.2},
    8: {'Innocent': 0.35, 'Terrorist': 0.35, 'Detective': 0.3},
    9: {'Innocent': 0.3, 'Terrorist': 0.35, 'Detective': 0.35},
    10: {'Innocent': 0.3, 'Terrorist': 0.4, 'Detective': 0.3}
}

bot = discord.Bot()

games = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    

@bot.slash_command(description="Start a Game of R6 TTT")
async def startgame(ctx, numplayers: discord.Option(discord.SlashCommandOptionType.integer)):
    # Generate a new Game ID
    game_id = ''.join(random.choices('0123456789abcdef', k=8))
    while game_id in games:
        game_id = ''.join(random.choices('0123456789abcdef', k=8))

    # Add the Game ID to the games dictionary
    games[game_id] = { 'players': [] }

    if numplayers < 3:
        await ctx.respond('Sorry, the game requires at least three players.')
        del games[game_id]
        return

    if numplayers > 10:
        await ctx.respond('Sorry, there can only be 10 players in a match.')
        del games[game_id]
        return

    # Get role probabilities
    roleprobs = ROLES.get(numplayers)

    # Store game data
    game_data = { 'num_players': numplayers, 'role_probs': roleprobs }
    games[game_id].update(game_data)
    print(f'game_data={game_data}, role_probs={roleprobs}')

    embed = discord.Embed(title="Game Starting :white_check_mark:")
    embed.add_field(name="No. of Players", value=numplayers, inline=False)
    embed.add_field(name="Round ID", value=game_id, inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(description="Join a Game of R6 TTT")
async def joingame(ctx, roundid: discord.Option(discord.SlashCommandOptionType.string)):
    game_data = games.get(roundid)
    if game_data is None:
        ctx.respond("Invalid Round ID")
        return
    if len(game_data['players']) >= game_data['num_players']:
        ctx.respond("Game is already full")
        return
    game_data['players'].append(ctx.author.id)
    num_players_joined = len(game_data['players'])

    author = ctx.author
    await author.send(f'You have joined the game (ID: {roundid}). There are currently {num_players_joined}/{game_data["num_players"]} players in the game.')
    await ctx.respond(f'You have sucessfully joined game (ID: {roundid})')

    if num_players_joined >= game_data['num_players']:
        players = game_data['players']
        random.shuffle(players)
        roles_assigned = {}
        roles = []
        for role, probability in game_data['role_probs'].items():
            num_roles = round(probability * game_data['num_players'])
            for i in range(num_roles):
                roles.append(role)
        print(f'roles before shuffle: {roles}')  # Debugging
        random.shuffle(roles)
        print(f'roles after shuffle: {roles}')  # Debugging
        terrorists_left = len([role for role in roles if role == 'Terrorist'])
        detectives_left = len([role for role in roles if role == 'Detective'])
        for i in range(game_data['num_players']):
            player = players[i]
            assigned_role = random.choice(list(game_data['role_probs'].keys()))
            while assigned_role in roles_assigned.values() and (assigned_role == 'Innocent' or (assigned_role == 'Terrorist' and terrorists_left == 0) or (assigned_role == 'Detective' and detectives_left == 0)):
                assigned_role = random.choice(list(game_data['role_probs'].keys()))
            roles_assigned[player] = assigned_role
            if assigned_role == 'Terrorist':
                terrorists_left -= 1
            elif assigned_role == 'Detective':
                detectives_left -= 1
            print(f"Assigned {roles_assigned[players[i]]} to player {players[i]}")
        
        for player in players:
            print(player)
            user = await bot.fetch_user(player)
            print(user)
            print(roles_assigned.keys())
            embed = discord.Embed(title=f"You are {roles_assigned[player]}")
            await user.send(embed=embed)

        del games[roundid]


    

bot.run('MTExNzI5MDgwMzcxNTM4NzQ1Mw.Gni7-B.Qry-HJnrz-qcetuprqwBN-JyY2_lSVofJuXv_0')