import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get("ENV.SETTINGS", "IG.settings"))
import django
django.setup()

from game.models import Game, User, Feedback
from game.parameters import *

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plotUserTimes(games):
	userTimes = []
	for game in games:
		for t in game.userTimes.split(',')[:-1]:
			userTimes.append(float(t))
	bins = np.arange(0, 20, 0.5)
	fig, ax = plt.subplots()
	sns.histplot(np.array(userTimes), stat='probability', bins=bins)
	ax.set(xlim=((0, 20)), xlabel="User Response Time (s)", title=f"Median={np.median(userTimes):.2f}, N={len(userTimes)}")
	fig.savefig("userTimes.pdf")

def plotGameTimes(games):
	gameTimes = []
	for game in games:
		gameTimes.append((game.tEnd - game.tStart).total_seconds())

	bins = np.arange(0, 200, 10)
	fig, ax = plt.subplots()
	sns.histplot(np.array(gameTimes), stat='probability', bins=bins)
	ax.set(xlim=((0, 200)), xlabel="Total Game Time (s)", title=f"Median={np.median(gameTimes):.2f}, N={len(gameTimes)}")
	fig.savefig("gameTimes.pdf")

def plotScoreVsTimeSingle(user, player, games):
	userGames = games.filter(user=user, userRole=player).order_by('tStart')
	userScores = []
	for game in userGames:
		score = 0
		for r in game.userRewards.split(',')[:-1]:
			score += int(r)
		userScores.append(score)
		print(game.agent.name)
	print(userScores)

def plotGenerosityVsTimeSingle(user, player, games):
	userGames = games.filter(user=user, userRole=player).order_by('tStart')
	userGenerosities = []
	for game in userGames:
		for r in range(ROUNDS):
			give = int(game.userGives.split(',')[:-1][r])
			keep = int(game.userKeeps.split(',')[:-1][r])
			if (give+keep) > 0:
				if player=="B" and r==ROUNDS-1:
					pass
				else:
					userGenerosities.append(give/(give+keep))
	fig, ax = plt.subplots()
	sns.lineplot(y=userGenerosities, x=np.arange(0, len(userGenerosities)))
	ax.set(xlabel='Move number', ylabel='Generosity', ylim=((0, 1)), title=f"User={user}, Player={player}")
	fig.savefig(f"{user}_{player}_Generosity.pdf")

def plotScoreVsTimeGroup(group, player, games):
	users = User.objects.filter(group=group)
	dfs = []
	columns = ('user', 'Game', 'Score')
	for user in users:
		userGames = games.filter(user=user, userRole=player).order_by('tStart')
		for g in range(len(userGames)):
			game = userGames[g]
			score = 0
			for r in game.userRewards.split(',')[:-1]:
				score += int(r)
			dfs.append(pd.DataFrame([[user, g, score]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	fig, ax = plt.subplots()
	sns.lineplot(data=df, x='Game', y='Score')
	ax.set(title=f"Group={group}, Player={player}")
	fig.savefig(f"{group}_{player}_Score.pdf")

def plotGenerosityVsTimeGroup(group, player, games):
	users = User.objects.filter(group=group)
	dfs = []
	columns = ('user', 'Game', 'Round', 'Generosity')
	for user in users:
		userGames = games.filter(user=user, userRole=player).order_by('tStart')
		for g in range(len(userGames)):
			game = userGames[g]
			for r in range(ROUNDS):
				give = int(game.userGives.split(',')[:-1][r])
				keep = int(game.userKeeps.split(',')[:-1][r])
				if (give+keep) > 0:
					dfs.append(pd.DataFrame([[game.user, g, r, give/(give+keep)]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	fig, ax = plt.subplots()
	sns.lineplot(data=df, x='Game', y='Generosity')
	ax.set(ylim=((0, 1)), title=f"Group={group}, Player={player}")
	fig.savefig(f"{group}_{player}_Generosity.pdf")


allGames = Game.objects.filter(complete=True, tutorial=False)

# plotUserTimes(allGames)
# plotGameTimes(allGames)

# user = User.objects.filter(username="sharpshootinpete")[0]
# plotScoreVsTimeSingle(user, "B", allGames)
# plotGenerosityVsTimeSingle(user, "B", allGames)

# plotScoreVsTimeGroup("2", "B", allGames)
# plotGenerosityVsTimeGroup("2", "B", allGames)