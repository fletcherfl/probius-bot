from miscFunctions import *
from urllib.request import urlopen
from aliases import *
from itertools import repeat
from json import loads
import asyncio
import aiohttp
import nest_asyncio
nest_asyncio.apply()

def trimForHeroesTalents(hero):
	hero=hero.replace('The','').lower()
	remove=".' -_"
	for i in remove:
		hero=hero.replace(i,'')
	hero=hero.replace('butcher','thebutcher').replace('ú','u').replace('cho','chogall')
	return hero

async def additionalInfo(hero,name,description):
	addDict={#Adds text to the end of descriptions
	'cassia':{'War Traveler':'The bonus is not lost when stutterstepping.'},
	'valla':{'Strafe':'The duration of Hatred is paused when channeling, and reset to full when Strafe ends.'},
	'alexstrasza':{
		'Cleansing Flame':'Dragonqueen: Cleansing Flame is cast instantly, and its cooldown is reduced by 10s. The duration of Dragonqueen is paused, while basic abilities continue to cool down while in flight.',
		'Dragon Scales':'Getting Stunned, Rooted, or Silenced while Dragon Scales is active refreshes its duration to 2 seconds.'},
	'maiev':{'Spirit of Vengeance':'Reactivate to teleport to the spirit.'},
	'sylvanas':{'Haunting Wave':'Sylvanas is unstoppable while flying to the banshee.'},
	'lunara':{'Leaping Strike':'Lunara is unstoppable while leaping.'},
	'chen':{'Storm, Earth, Fire':'Using Storm, Earth, Fire removes most negative effects from Chen.'},
	'guldan':{'Life Tap':'Costs 222 (+4% per level) Health.'},
	'johanna':{"Heaven's Fury":'4 bolts per second per enemy, up to 2 enemies.'}
	}
	if hero in addDict:
		if name in addDict[hero]:
			description+=' ``'+addDict[hero][name]+'``'
	return description

async def fixTooltips(hero,name,description):
	fixDict={#Replaces text using strikethrough
	'tracer':{'Sleight of Hand':['20%','23%']},
	'cassia':{'War Traveler':['8%','4%','1 second','0.5 seconds']},
	'sylvanas':{'Haunting Wave':['teleport','fly']}
	}
	if hero in fixDict:
		if name in fixDict[hero]:
			for i in range(len(fixDict[hero][name])//2):
				description=description.replace(fixDict[hero][name][2*i],'~~'+fixDict[hero][name][2*i]+'~~ '+'``'+fixDict[hero][name][2*i+1]+'``')
	return await additionalInfo(hero,name,description)

async def descriptionFortmatting(description):
	if 'Repeatable Quest' in description:
		description=description.replace('Repeatable Quest:','\n    **❢ Repeatable Quest:**')
	else:
		description=description.replace('Quest:','\n    **❢ Quest:**')
	description=description.replace('Reward:','\n    **? Reward:**')
	return description

async def fetch(session, url):
	async with session.get(url) as response:
		return await response.text()

async def downloadHero(hero,client,patch):
	async with aiohttp.ClientSession() as session:
		if patch=='':
			page = await fetch(session, 'https://raw.githubusercontent.com/heroespatchnotes/heroes-talents/master/hero/'+hero+'.json')
		else:
			page = await fetch(session, 'https://raw.githubusercontent.com/MGatner/heroes-talents/'+patch+'/hero/'+hero+'.json')
		#client.heroPages={...'genji':[abilities,talents], ...}
		page=loads(page)
		abilities=[]
		if hero in ['ltmorales', 'valeera', 'deathwing', 'zarya']:
			resource='energy'
		elif hero=='chen':
			resource='brew'
		elif hero=='sonya':
			resource='fury'
		else:
			resource='mana'

		for i in page['abilities'].keys():
			for ability in page['abilities'][i]:
				if 'hotkey' in ability:
					output='**['+ability['hotkey']+'] '
				else:
					output='**[D] '
				output+=ability['name']+':** '
				if 'cooldown' in ability or 'manaCost' in ability:
					output+='*'
					if 'cooldown' in ability:
						output+=str(ability['cooldown'])+' seconds'
						if 'manaCost' in ability:
							output+=', '
					if 'manaCost' in ability:
						output+=str(ability['manaCost'])+' '+resource
					output+=';* '
				output+=await descriptionFortmatting(ability['description'])
				output=await fixTooltips(hero,ability['name'],output)
				abilities.append(output)

		talents=[]
		keys=sorted(list(page['talents'].keys()),key=lambda x:int(x))
		for key in keys:
			tier=page['talents'][key]
			talentTier=[]
			for talent in tier:
				output='**['+str(int(key)-2*int(hero=='chromie' and key!='1'))+'] '
				output+=talent['name']+':** '
				if 'cooldown' in talent:
					output+='*'+str(talent['cooldown'])+' seconds;* '
				output+=await descriptionFortmatting(talent['description'])
				output=await fixTooltips(hero,talent['name'],output)
				talentTier.append(output)
			talents.append(talentTier)
		client.heroPages[aliases(hero)]=(abilities,talents)

async def loopFunction(client,heroes,patch):
	for future in asyncio.as_completed(map(downloadHero, heroes,repeat(client),repeat(patch))):
		await future

async def downloadAll(client,argv):
	if len(argv)==2:
		patch=argv[1]
	else:
		patch=''
	heroes=getHeroes()
	heroes=list(map(trimForHeroesTalents,heroes))
	loop = asyncio.get_event_loop()#running instead of event when calling from a coroutine. But running is for python3.7+
	loop.run_until_complete(loopFunction(client,heroes,patch))

async def heroStats(hero,channel):
	if hero=='The_Lost_Vikings':
		for i in ['Olaf','Baleog','Erik']:
			await heroStats(i,channel)
	else:
		async with aiohttp.ClientSession() as session:
			page = await fetch(session, 'https://heroesofthestorm.gamepedia.com/index.php?title=Data:'+hero)
			page=''.join([i for i in page])
			page=page.split('<td><code>skills</code>')[0]

			output=[]
			usefulStats=['date', 'health', 'resource', 'attack speed', 'attack range', 'attack damage', 'unit radius']
			for i in usefulStats:
				page=page.split('<td>'+i+'\n')[1]
				page=page[page.index('<td>')+4:]
				output.append('**'+i.replace('attack','aa').replace('unit ','').replace('health','hp').capitalize()+'**: '+str(page[:page.index('</td>')]).replace('\n',''))
			await channel.send('``'+hero+':`` '+', '.join(output))