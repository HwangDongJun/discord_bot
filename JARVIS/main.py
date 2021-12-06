from datetime import datetime
from typing import Optional

import discord, asyncio, os
from discord import Embed, Member
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

@bot.command(aliases=['KOSPI', '코스피'])
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

@bot.command(aliases=['채널'])
async def channel(ctx, channel: discord.TextChannel):
	await ctx.send(f"대상채널이름: {channel.name} \n대상채널ID: {channel.id}")

#@bot.command(aliases=['유저', '사용자'])
#async def user(ctx, user: discord.User):
#	await ctx.send(f"대상유저이름: {user.name} \n대상유저ID: {user.id} \n대상유저현재활동: {user.activities}, {user.")

@bot.command(aliases=['유저', '사용자'])
async def user_info(ctx, target: Optional[Member]):
	target = target or ctx.author

	embed = Embed(title="User information",
				  colour=target.colour,
				  timestamp=datetime.utcnow())
	embed.set_thumbnail(url=target.avatar_url)

	fields = [("Name", str(target), True),
			  ("ID", target.id, False),
			  ("Bot?", target.bot, True),
			  ("Top role", target.top_role.mention, True),
			  ("Status", str(target.status).title(), True),
			  ("Activity", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", True),
			  ("Created at", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
			  ("Joined at", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True)]

	for name, value, inline in fields:
		embed.add_field(name=name, value=value, inline=inline)
	
	await ctx.send(embed=embed)

@bot.command(aliases=['공지사항', '공지', '학교망해라'])
async def university_info(ctx):
	notice = list(); today_notice_count = 0
	for offset in [0, 10, 20, 30, 40, 50]:
		req = requests.get(f'https://computer.cnu.ac.kr/computer/notice/bachelor.do?mode=list&&articleLimit=10&article.offset={offset}')
		html = req.text
		soup = bs(html, "lxml")
	
		noticeContents = soup.select("tbody > tr")
		for nc in noticeContents:
			try:
				if "공" in nc.select_one("td.b-num-box").text.strip():
					notice_str = f'[공지] {nc.select_one("td.b-td-left > div.b-title-box > div.b-m-con > span.b-date").text.strip()}-{nc.select_one("td.b-td-left > div.b-title-box > a").text.strip()}'
					if notice_str not in notice:
						notice.append(notice_str)
				else:
					today_ = str(datetime.today().year)[2:] + "." + str(datetime.today().month) + "."
					if len(str(datetime.today().day)) == 1:
						today_ += "0" + str(datetime.today().day)
					else:
						today_ += str(datetime.today().day)
					if today_ in nc.select_one("td.b-td-left > div.b-title-box > div.b-m-con > span.b-date").text.strip():
						notice_str = f'{nc.select_one("td.b-td-left > div.b-title-box > div.b-m-con > span.b-date").text.strip()}-{nc.select_one("td.b-td-left > div.b-title-box > a").text.strip()}'
						notice.append(notice_str)
						today_notice_count += 1
			except AttributeError:
				continue

	if today_notice_count == 0:
		notice.append("오늘날짜로 공지된 공지사항이 없습니다.")

	await ctx.send('\n'.join(notice))

@bot.command(aliases=['사업단공지사항', '사업단공지', '사업단망해라'])
async def university_saupdan_info(ctx):
	notice = list(); today_notice_count = 0
	for offset in [0, 10, 20, 30, 40, 50]:
		req = requests.get(f'https://computer.cnu.ac.kr/computer/notice/project.do?mode=list&&articleLimit=10&article.offset={offset}')
		html = req.text
		soup = bs(html, "lxml")
	
		noticeContents = soup.select("tbody > tr")
		for nc in noticeContents:
			try:
				if "공" in nc.select_one("td.b-num-box").text.strip():
					notice_str = f'[공지] {nc.select_one("td.b-td-left > div.b-title-box > div.b-m-con > span.b-date").text.strip()}-{nc.select_one("td.b-td-left > div.b-title-box > a").text.strip()}'
					if notice_str not in notice:
						notice.append(notice_str)
				else:
					today_ = str(datetime.today().year)[2:] + "." + str(datetime.today().month) + "."
					if len(str(datetime.today().day)) == 1:
						today_ += "0" + str(datetime.today().day)
					else:
						today_ += str(datetime.today().day)
					if today_ in nc.select_one("td.b-td-left > div.b-title-box > div.b-m-con > span.b-date").text.strip():
						notice_str = f'{nc.select_one("td.b-td-left > div.b-title-box > div.b-m-con > span.b-date").text.strip()}-{nc.select_one("td.b-td-left > div.b-title-box > a").text.strip()}'
						notice.append(notice_str)
						today_notice_count += 1
			except AttributeError:
				continue

	if today_notice_count == 0:
		notice.append("오늘날짜로 공지된 공지사항이 없습니다.")

	await ctx.send('\n'.join(notice))

bot.run('ODcyMTUxMzQzODM2NTY1NTI0.YQlsPA.0WC-wOQDCfThOsMkILkoX_S0gkA')
