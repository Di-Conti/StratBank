import discord
from discord.ext import commands
import pandas as pd
import numpy as np
import datetime
import time

TOKEN = 'Nzc4NzczMTA4Mzk1MDgxNzI4.X7W2-Q.xIHusryjMTULg3GiTvi9fCmr0C4'
GUILD = 'Strat'
#df = pd.read_csv('bank.csv')

description = '''StratBank'''
bot = commands.Bot(command_prefix='?', description=description)
#bot = discord.Client()

players = [] #Trouver un moyen plus simple de stocker les joueurs (dans un dico)
pariB = False

def data_add(data, name, number):
	data.loc[data['User'] == name, ['Money']] = data.loc[data['User'] == name, ['Money']] + number
	return data

def detect_players(tabs, name):
	for tab in tabs :
		print(tab[0])
		if name == tab[0] :
			return True

	return False

##############
#Faire d'autres fonctions pour raccourcir la fonction pari
##############

async def play(ctx,path): #Fonction de Thomas Menchi : https://github.com/Menchit-ai/Discord-bot/blob/master/bot.py

    voice_channel = ctx.author.voice
    if voice_channel is None: await ctx.send("Vous n'êtes pas dans un channel audio."); return
    vc = None


    if (ctx.me.voice is None): 
        vc = await ctx.author.voice.channel.connect()
    elif ctx.author.voice.channel != ctx.me.voice.channel:
        await ctx.voice_client.disconnect()
        vc = await ctx.author.voice.channel.connect()
    else:
	    print("là")
	    vc = ctx.voice_client    

    vc.play(discord.FFmpegPCMAudio(path), after=lambda e: print('done', e))
    vc.is_playing()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    guild = discord.utils.get(bot.guilds, name=GUILD)

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    texts = '\n - '.join([text.name for text in guild.text_channels])
    print(f'Channels:\n - {texts}')

    ids = [member.id for member in guild.members]
    print(ids)

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


@bot.command(hidden = True)
async def membres(ctx):
	server = ctx.guild
	pers = server.member_count
	members = '\n - '.join([member.name for member in server.members])
	#ids = [member.name for member in server.members]
	print(str(members))

@bot.command()
async def test(ctx):
	embed = discord.Embed(title = "C'est un test", description = "oui")
	embed.add_field(name = "Bot", value = "Machin", inline = True)
	#await ctx.send(embed = embed)

	#def checker(message):
		#return (message.content == "test")

	#tester = await bot.wait_for('message', check = checker)

	#auteur = tester.author

	#print(str(auteur.name))

	embed.add_field(name = "Bot2", value = "Machin2", inline = True)
	a = embed.to_dict()
	b = a['fields']
	c = b[0]
	d = c['name']
	print(d)

	embed.to_dict()['fields'][0]['name'] = "AHHHH"
	await ctx.send(embed = embed)



@bot.command(name='see', help='Pour voir ton compte')
async def seeAccount(ctx):
	auteur = str(ctx.author)
	df = pd.read_csv('bank.csv')
	if auteur in df["User"].tolist():
		filtre = df[df["User"] == auteur]
		argent = filtre["Money"].tolist()
		embed = discord.Embed(title = "BANQUE DE :", description = str(ctx.author.name), colour = discord.Colour(0xE5E242))
		embed.set_thumbnail(url= ctx.author.avatar_url)
		embed.add_field(name = "StratCoins :", value = str(argent[0]), inline = True)
		await ctx.send(embed = embed)
		#await ctx.send(f'Ton argent : {str(argent[0])}')
	else:
		await ctx.send("T'as pas de compte !")

@bot.command(name='claim', help='Pour demander ton argent')
async def claimAccount(ctx):
	auteur = str(ctx.author)
	day = datetime.datetime.now()
	df = pd.read_csv('bank.csv')
	global pariB
	if auteur in df["User"].tolist():
		if pariB != True :
			filtre = df[df["User"] == auteur]
			past = filtre["Date"].tolist()
			if past[0] != str(day.date()) :
				df.loc[df['User'] == auteur, ['Money']] = df.loc[df['User'] == auteur, ['Money']] + 500
				df.loc[df['User'] == auteur, ['Date']] = str(day.date())
				df.to_csv('bank.csv', index=False)
				await ctx.send("Tu as gagné 500 StratCoins")
			else :
				await ctx.send("T'as déjà eu assez d'argent pour aujourd'hui...")
		#await ctx.send(f'Ton argent : {str(argent[0])}')
		else :
			await ctx.send("Attendez la fin du pari pour demander de l'argent")
	else:
		await ctx.send("T'as pas de compte !")

@bot.command(name='create', help='Pour te créer un compte StratBank')
async def createAccount(ctx):
	df = pd.read_csv('bank.csv')
	auteur = str(ctx.author)
	global pariB
	if not auteur in df["User"].tolist() :
		if pariB != True :
			day = datetime.datetime.now()
			df2 = pd.DataFrame({"User": [auteur],"Money":[100], "Date" : str(day.date())})
			tot = pd.concat([df, df2], ignore_index=True)
			tot.to_csv('bank.csv', index=False)
			await ctx.send("Compte créé")
		else :
			await ctx.send("Attendez la fin du pari pour créer un compte")
	else :
		await ctx.send("Vous existez déjà !")

@bot.command(name='pari', help='Pour parier quelques pièces') #pass_context?
async def pari(ctx):
	global players
	global pariB
	df = pd.read_csv('bank.csv')
	auteurInit = ctx.author
	winDol = 0
	loseDol = 0
	coteW = 2
	coteL = 2

	if(pariB):
		await ctx.send("Un pari est déjà en cours")
		return

	pariB = True

	#await ctx.send("LE PARI COMMENCE : WIN OU LOSE?")
	#await play(ctx,'./Sounds/piece.mp3')
	embed = discord.Embed(title = "LE PARI COMMENCE", description = "WIN OU LOSE?", colour = discord.Colour(0xE5E242))
	embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
	graph = await ctx.send(embed = embed)

	def check(message):
		return message.channel == ctx.message.channel and (message.content[0:4] == "win " or message.content[0:5] == "lose ") #Améliorer les checks avec fonctions de message

	temps = time.time()

	while (time.time() - temps) <= 60:
		try:
			part = await bot.wait_for('message', timeout = 10, check = check)
			auteur = str(part.author)
			Coherence = True
			if auteur in df["User"].tolist():
				msg = part.content.split(" ")
				montant = -1

				for m in msg :
					if m.isnumeric():
						montant = int(m)

				if montant < 0 :
					await ctx.send("Il est où le prix ?")

				else:
					print(auteur)
					moneyUser = df.loc[df['User'] == auteur, ['Money']]
					print(str(moneyUser))
					moneyUser = moneyUser['Money'].iloc[0]
					print(moneyUser)

					if(int(moneyUser) <= 0):
						await ctx.send("T'as pas de fric...")

					else:

						if int(moneyUser) < montant:
							montant = int(moneyUser)
							await ctx.send("T'avais pas assez d'argent, mais t'en fais pas on a fait un all-in de " + str(montant) + " StratCoins")

						if detect_players(players, auteur) :
							for tab in players :
								if auteur == tab[0] :
									ind = players.index(tab)

									if msg[0] == tab[2] :
										montplus = tab[3]
										montplus = int(montplus) + montant
										ctx.send(f"{auteur} va remettre {montant} StratCoins !")
										embed.to_dict()['fields'][ind]['value'] = "" + msg[0].upper() + " : " + str(montplus) + " StratCoins"
									else :
										Coherence = False

						else :
							players.append([auteur, str(part.author.name), msg[0], str(montant)])
							embed.add_field(name = str(part.author.name), value = "" + msg[0].upper() + " : " + str(montant) + " StratCoins", inline = True)
							await ctx.send("Pari enregistré")

						if Coherence :

							df = data_add(df, auteur, -(montant))
							df.to_csv('bank.csv', index=False)
							print(players)

							print(str(montant)) #Pourcentage de chance que l’événement se produise : (1/Cote) x 100

							if msg[0] == "win" :
								winDol = winDol + montant
							elif msg[0] == "lose" :
								loseDol = loseDol + montant

							if (winDol != 0) and (loseDol != 0) :
								coteW = float("{:.2f}".format(100/((winDol / (winDol + loseDol))*100)))
								coteL = float("{:.2f}".format(100/((loseDol / (winDol + loseDol))*100)))
								await ctx.send(f"POUR LES COTES : WIN = {coteW}, LOSE = {coteL}") #Mettre aussi dans Embed 

							await graph.edit(embed = embed)

						else :
							await ctx.send("Vous avez déjà fait un choix et il est définitif !")
			else:
				await ctx.send("Apparemment t'es encore chez BNP Paribas...")
		except:
			pass

	if len(players) == 0:
		await ctx.send("Aucun pari n'a été enregistré...")
		return

	await ctx.send("FIN DES PARIS : ON ATTEND LE RESULTAT")

	def check2(message):
		return message.channel == ctx.message.channel and message.author == auteurInit and (message.content == "win" or message.content == "lose")

	part2 = await bot.wait_for('message', check = check2)

	#await ctx.send("FIN")

	result = part2.content
	if result == "win":
		coteT = coteW
	elif result == "lose" :
		coteT = coteL
	winners = []
	df = pd.read_csv('bank.csv')

	embedEnd = discord.Embed(title = "LES RESULTATS", description = "VOICI LES GAGNANTS :", colour = discord.Colour(0xE5E242))

	for i in range(len(players)):
		if(players[i][2] == result):
			print("oui")
			winners.append(players[i][1])
			won = players[i][3]
			won = int(won) * coteT
			won = int(won)
			print(won)
			df = data_add(df, players[i][0], won)
			embedEnd.add_field(name = players[i][1], value = "+" + str(won) + " StratCoins", inline = True)


	df.to_csv('bank.csv', index=False)
	players = []
	pariB = False

	#wonners = ', '.join([str(w) for w in winners])
	#await ctx.send(f'Les gagnants sont : {wonners}')

	await ctx.send(embed = embedEnd)


bot.run(TOKEN)