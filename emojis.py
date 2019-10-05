from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from aliases import *#Spellcheck and alternate names for heroes
import discord

def emoji(text):
	hero=aliases(text[0])#Emoji pages are case sensitive. Sadly, capitalizing also ruins non-hero emojis (Nexus pack etc).
	emojiCode=text[1].replace('lol','rofl').replace('wow','surprised')

	emojiPackCode='2_'
	if hero in ['Nexus','Chomp']:
		emojiPackCode=''
	elif emojiCode in ['happy','rofl','sad','silly','meh']:
		emojiPackCode='1_'

	emojiCode=emojiCode.capitalize()
	if emojiCode=='Rofl':
		emojiCode='ROFL'

	imageFormat='.png'
	if hero in ['Chomp']:
		imageFormat='.gif'

	emojiPage='https://heroesofthestorm.gamepedia.com/File:Emoji_'+hero+'_Pack_'+emojiPackCode+hero+'_'+emojiCode+imageFormat

	html = urlopen(emojiPage)
	bs = BeautifulSoup(html, 'html.parser')
	images = bs.find_all('img', {'src':re.compile(imageFormat)})
	emojiImagePage=images[0]['src']

	e = discord.Embed()
	e.set_image(url=emojiImagePage)
	return e