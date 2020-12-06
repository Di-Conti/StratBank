import discord
from discord.ext import commands
import pandas as pd
import numpy as np
import datetime
import time

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv("token.env")
TOKEN = os.getenv('DISCORD_TOKEN')
#print(TOKEN)
GUILD = 'Strat'
#df = pd.read_csv('bank.csv')

MDP = os.getenv('MDP')

client = MongoClient(MDP)
db = client.test
bank = db["bank"]

description = '''StratBank'''
bot = commands.Bot(command_prefix='?', description=description)
#bot = discord.Client()

players = [] #Liste de dicos
pariB = False

def data_add(data, name, number): #Ancienne focntion
	data.loc[data['User'] == name, ['Money']] = data.loc[data['User'] == name, ['Money']] + number
	return data

def detect_players(tabs, name):
	for tab in tabs :
		#print(tab[0])
		if name == tab['pseudo'] :
			print("allo")
			return tabs.index(tab)

	return -1

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

@bot.command(hidden = True)
async def test(ctx):
	msg = await ctx.send("TEST")
	await msg.add_reaction('👍')

@bot.command(hidden = True)
async def debug(ctx):
	global players
	global pariB
	players = []
	pariB = False

@bot.command(name='cote', help='Pour voir comment la cote est calculée')
async def cote(ctx):
	await ctx.send("Pour les cotes : cote Choix = 100/((Somme Choix / (Somme Win + Somme Lose))*100))")

@bot.command(name='give', hidden=True)
async def giveAccount(ctx, member: discord.Member, *mont):
	auteur = str(ctx.author)
	montant = int(mont[0])
	membre = str(member)
	#df = pd.read_csv('bank.csv')
	if auteur == "TLG#5803" :
		compte = bank.find_one({"User":membre})
		if compte != None:
			#df = data_add(df, membre, montant)
			#df.to_csv('bank.csv', index=False)
			ajout = compte["Money"] + montant
			bank.update_one({"User": membre}, {"$set":{"Money": ajout}})
			await ctx.send("Argent distribué")
		else:
			await ctx.send("Pas de compte à ce nom !")
	else:
		await ctx.send("Vous n'êtes pas banquier !")

@bot.command(name='send', help='Pour donner de l\'argent à quelqu\'un')
async def sendAccount(ctx, member: discord.Member, *mont):
	auteur = str(ctx.author)
	montant = int(mont[0])
	membre = str(member)
	#df = pd.read_csv('bank.csv')

	if montant < 0 :
		await ctx.send("Le vol est interdit ici !")
		return

	if auteur == membre :
		await ctx.send("Tu peux pas envoyer de l'argent à toi-même !")
		return

	compteA = bank.find_one({"User":auteur})
	compteM = bank.find_one({"User":membre})

	if compteA != None and compteM != None:
		#filtre = df[df["User"] == auteur]
		#argent = filtre["Money"].tolist()
		if int(compteA["Money"]) < montant :
			montant = int(compteA["Money"])
			await ctx.send("Tu donnes de l'argent à un mec et maintenant t'es ruiné !")
		#df = data_add(df, auteur, -montant)
		#df = data_add(df, membre, montant)
		#df.to_csv('bank.csv', index=False)
		retrait = compteA["Money"] - montant
		ajout = compteM["Money"] + montant
		bank.update_one({"User": auteur}, {"$set":{"Money": retrait}})
		bank.update_one({"User": membre}, {"$set":{"Money": ajout}})
		await ctx.send(f"Argent envoyé de {auteur} à {membre}")
	else:
		await ctx.send("Pas de compte à ce nom !")

@bot.command(name='see', help='Pour voir ton compte')
async def seeAccount(ctx):
	auteur = str(ctx.author)
	#df = pd.read_csv('bank.csv')
	global bank
	compte = bank.find_one({"User":auteur})
	if compte != None:
		#filtre = df[df["User"] == auteur]
		#argent = filtre["Money"].tolist()
		embed = discord.Embed(title = "BANQUE DE :", description = str(ctx.author.name), colour = discord.Colour(0xE5E242))
		embed.set_thumbnail(url= ctx.author.avatar_url)
		embed.add_field(name = "StratCoins :", value = str(compte["Money"]), inline = True)
		await ctx.send(embed = embed)
	else:
		await ctx.send("T'as pas de compte !")

@bot.command(name='claim', help='Pour demander ton argent')
async def claimAccount(ctx):
	auteur = str(ctx.author)
	day = datetime.datetime.now()
	#df = pd.read_csv('bank.csv')
	global pariB
	global bank
	compte = bank.find_one({"User":auteur})
	if compte != None :
		if pariB != True :
			#filtre = df[df["User"] == auteur]
			#past = filtre["Date"].tolist()
			if compte["Date"] != str(day.date()) :
				#df = data_add(df, auteur, 500)
				#df.loc[df['User'] == auteur, ['Date']] = str(day.date())
				#df.to_csv('bank.csv', index=False)
				ajout = compte["Money"] + 500
				bank.update_one({"User": auteur}, {"$set":{"Money": ajout}})
				bank.update_one({"User": auteur}, {"$set":{"Date": str(day.date())}})
				await ctx.send("Tu as gagné 500 StratCoins")
			else :
				await ctx.send("T'as déjà eu assez d'argent pour aujourd'hui...")
		else :
			await ctx.send("Attendez la fin du pari pour demander de l'argent")
	else:
		await ctx.send("T'as pas de compte !")

@bot.command(name='create', help='Pour te créer un compte StratBank')
async def createAccount(ctx):
	#df = pd.read_csv('bank.csv')
	auteur = str(ctx.author)
	global pariB
	global bank
	if bank.find_one({"User":auteur}) == None :
		if pariB != True :
			day = datetime.datetime.now()
			#df2 = pd.DataFrame({"User": [auteur],"Money":[1000], "Date" : str(day.date())})
			#tot = pd.concat([df, df2], ignore_index=True)
			#tot.to_csv('bank.csv', index=False)
			bank.insert_one(
				{
				"User" : auteur,
				"Money" : 1500,
				"Date" : str(day.date()),
				}
			)
			await ctx.send("Compte créé")
		else :
			await ctx.send("Attendez la fin du pari pour créer un compte")
	else :
		await ctx.send("Vous existez déjà !")

@bot.command(name='pari', help='Pour parier quelques pièces')
async def pari(ctx):
	global players
	global pariB
	global bank
	#df = pd.read_csv('bank.csv')
	auteurInit = ctx.author
	winDol = 0
	loseDol = 0
	coteW = 2
	coteL = 2

	if(pariB):
		await ctx.send("Un pari est déjà en cours")
		return

	pariB = True

	embed = discord.Embed(title = "LE PARI COMMENCE", description = "WIN OU LOSE?", colour = discord.Colour(0xE5E242))
	embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
	graph = await ctx.send(embed = embed) #Mettre un argument pour le titre en plus

	def check(message):
		return message.channel == ctx.message.channel and (message.content[0:4] == "win " or message.content[0:5] == "lose ") #Améliorer les checks avec fonctions de message

	temps = time.time()

	while (time.time() - temps) <= 60:
		try:
			part = await bot.wait_for('message', timeout = 10, check = check)
			#checkM = bot.get_emoji(558322116685070378)
			await part.add_reaction('👍')
			
			auteur = str(part.author)
			Coherence = True
			compte = bank.find_one({"User":auteur})
			if compte != None:
				msg = part.content.split(" ")
				montant = -1

				for m in msg :
					if m.isnumeric():
						montant = int(m) #Améliorer syntaxe avec rsplit

				if montant < 0 :
					await ctx.send("Il est où le prix ?")

				else:
					print(auteur)
					#moneyUser = df.loc[df['User'] == auteur, ['Money']]
					#moneyUser = moneyUser['Money'].iloc[0]
					moneyUser = compte["Money"]
					print(moneyUser)

					if(int(moneyUser) <= 0):
						await ctx.send("T'as pas de fric...")

					else:

						if int(moneyUser) < montant:
							montant = int(moneyUser)
							await ctx.send("T'avais pas assez d'argent, mais t'en fais pas on a fait un all-in de " + str(montant) + " StratCoins")

						ind = detect_players(players, auteur)

						if ind != -1 :

							print(ind)

							if msg[0] == players[ind]['choice'] :
								montplus = players[ind]['montant']
								montplus = int(montplus) + montant
								players[ind]['montant'] = montplus
								await ctx.send(f"{players[ind]['name']} va remettre {montant} StratCoins !")
								embed.to_dict()['fields'][ind]['value'] = "" + msg[0].upper() + " : " + str(montplus) + " StratCoins"
							else :
								Coherence = False

						else :
							players.append({'pseudo' : auteur, 'name' : str(part.author.name), 'choice' : msg[0], 'montant' : str(montant)})
							embed.add_field(name = str(part.author.name), value = "" + msg[0].upper() + " : " + str(montant) + " StratCoins", inline = True)
							await ctx.send("Pari enregistré")
							#await part.add_reaction('👍')

						if Coherence :

							#df = data_add(df, auteur, -(montant))
							#df.to_csv('bank.csv', index=False)
							retrait = compte["Money"] - montant
							bank.update_one({"User": auteur}, {"$set":{"Money": retrait}})
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
		players = []
		pariB = False
		return

	elif len(players) == 1:
		if players[0]['pseudo'] == str(auteurInit):
			await ctx.send("ON NE FAIT PAS D'ARNAQUE ICI !!!")
			players = []
			pariB = False
			return


	await ctx.send("FIN DES PARIS : ON ATTEND LE RESULTAT")

	def check2(message):
		return message.channel == ctx.message.channel and message.author == auteurInit and (message.content == "win" or message.content == "lose")

	part2 = await bot.wait_for('message', check = check2)

	#await ctx.send("FIN")

	#print("numero1")

	result = part2.content
	if result == "win":
		coteT = coteW
	elif result == "lose" :
		coteT = coteL
	#df = pd.read_csv('bank.csv')

	#print("numero2")

	embedEnd = discord.Embed(title = "LES RESULTATS", description = "VOICI LES GAGNANTS :", colour = discord.Colour(0xE5E242))

	for i in range(len(players)):
		if(players[i]['choice'] == result):
			print("oui")
			won = players[i]['montant']
			won = int(won) * coteT
			won = int(won)
			print(won)
			#df = data_add(df, players[i]['pseudo'], won)
			ajout = compte["Money"] + won
			bank.update_one({"User": players[i]['pseudo']}, {"$set":{"Money": ajout}})
			embedEnd.add_field(name = players[i]['name'], value = "+" + str(won) + " StratCoins", inline = True)


	#df.to_csv('bank.csv', index=False)
	players = []
	pariB = False

	#wonners = ', '.join([str(w) for w in winners])
	#await ctx.send(f'Les gagnants sont : {wonners}')

	await ctx.send(embed = embedEnd)


bot.run(TOKEN)