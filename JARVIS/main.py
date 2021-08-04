import discord, asyncio, os
from discord.ext import commands

import requests
from bs4 import BeautifulSoup as bs

bot = commands.Bot(command_prefix='!', status=discord.Status.online)

@bot.event
async def on_ready():
	print("J.A.R.V.I.S. is ready.")

@bot.event
async def on_member_join(member):
	print(f'{member} has joined a server.')

@bot.event
async def on_member_remove(member):
	print(f'{member} has left a server.')

@bot.command(aliases=['안녕', 'hi', '안녕하세요'])
async def hello(ctx):
	await ctx.send(f'{ctx.author.mention}님 안녕하세요!')

@bot.command(aliases=['KOSPI'])
async def kospi(ctx, text):
	# 주식 데이터를 그때그때 저장할 시 시간이 오래 걸리기에 다른 대안이 필요하긴함...
	# 또한 현재 코스피만 만들둔 상태임 // 코스닥도 추가해야함
		# 참고 : https://www.youtube.com/watch?v=VOX_mJwmhmg&ab_channel=%ED%83%9D%EC%BD%94%EB%94%A9TechCoding
	stock_dict = dict()
	for page in range(1, 5): # 36page까지 하면 11초나 걸림...
		req = requests.get(f"https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page={page}")
		html = req.text
		soup = bs(html, "lxml")
	
		stockContents = soup.select("#contentarea > div.box_type_l > table.type_2 > tbody > tr")
		for sc in stockContents:
			try:
				stockRank = sc.select_one("td.no").text
				stockName = sc.select_one("td:nth-child(2) > a").text
				stockPrice = sc.select_one("td:nth-child(3)").text
				stockCap = sc.select_one("td:nth-child(7)").text
				if stockName not in stock_dict:
					stock_dict[stockName] = [stockRank, stockPrice, stockCap]
			except AttributeError:
				continue

	if text.upper() in stock_dict:
		stock_info = stock_dict[text.upper()]
		await ctx.send(f"{ctx.author.mention} KOSPI {stock_info[0]}등 {text.upper()} 종목의 현재가는 {stock_info[1]}원이고, 시가총액은 {stock_info[2]}억 원 입니다.")
	else:
		await ctx.send(f"현재 {ctx.author.mention}님이 요청하신 기업에 대한 정보는 없습니다.")


bot.run('ODcyMTUxMzQzODM2NTY1NTI0.YQlsPA.qGfEO2UuSY_ZBWyX9EMh9pFZAhA')
