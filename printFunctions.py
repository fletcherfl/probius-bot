from aliases import *
from miscFunctions import *

def printAbilities(abilities):#No identifier, print all abilities
	if len(abilities)<8:
		output=''
		for i in abilities:
			output+=i+'\n'
		return output
	else:
		output1=''
		output2=''
		for i in abilities[0:4]:
			output1+=i+'\n'
		for i in abilities[4:]:
			output2+=i+'\n'
		return[output1,output2]

def printTier(talents,tier):#Print a talent tier
	output=''
	for i in talents[tier]:
		output+=i+'\n'
	return output

def printAbility(abilities,hotkey):#Prints abilities with matching hotkey
	output=''
	for ability in abilities:
		if '**['+hotkey.upper()+']' in ability:
			output+=ability+'\n'
	return output

def printSearch(abilities, talents, name, hero):#Prints abilities and talents with the name of the identifier
	if '--' in name:
		[name,exclude]=name.split('--')
	else:
		exclude='this string is not in any abilities or talents'
	namelist=name.split('&')
	output=''
	for ability in abilities:
		if sum([1 for i in namelist if i in ability.lower()])==len(namelist) and exclude not in ability.lower():
			output+=ability+'\n'
	levelTiers=[0,1,2,3,4,5,6]
	if hero=='Varian':
		del levelTiers[1]
	else:
		del levelTiers[3]
	for i in levelTiers:
		talentTier=talents[i]
		for talent in talentTier:
			if sum([1 for i in namelist if i in talent.lower()])==len(namelist) and exclude not in talent.lower():
				output+=talent+'\n'
	return output

async def printLarge(channel,inputstring):#Get long string. Print lines out in 2000 character chunks
	strings=[i+'\n' for i in inputstring.split('\n')]
	output=strings.pop(0)
	while strings:
		if len(output)+len(strings[0])<2000:
			output+=strings.pop(0)
		else:
			await channel.send(output)
			output=strings.pop(0)
	await channel.send(output)

async def printAll(client,message,keyword):#When someone calls [all/keyword]
	async with message.channel.typing():
		if len(keyword)<4 and message.author.id!=183240974347141120:
			await message.channel.send('Please use a keyword with at least 4 letters minimum')
			return
		toPrint=''
		for hero in getHeroes():
			(abilities,talents)=client.heroPages[hero]
			output=printSearch(abilities,talents,keyword,hero)
			if output=='':
				continue
			toPrint+='`'+hero.replace('_',' ')+':` '+output
		if toPrint=='':
			return
		botChannels={'Wind Striders':571531013558239238,'The Hydeout':638160998305497089}
		if toPrint.count('\n')>5 and message.channel.guild.name in botChannels:#If the results is more lines than this, it gets dumped in specified bot channel
			channel=message.channel.guild.get_channel(botChannels[message.channel.guild.name])
			introText=message.author.mention+", Here's all heroes' "+'"'+keyword+'":\n'
			toPrint=introText+toPrint
		else:
			channel=message.channel
	await printLarge(channel,toPrint)

if __name__ == '__main__':
	from miscFunctions import *
	from heroPage import heroAbilitiesAndTalents

	output=[]
	for hero in getHeroes():
		[abilities,talents]=heroAbilitiesAndTalents(hero)
		abilities=extraD(abilities,hero)
		for ability in abilities:
			if 'Quest' in ability:
				output.append(ability.split(':** ')[0])
	for i in output:
		print(i)