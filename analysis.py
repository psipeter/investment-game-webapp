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
	fig.savefig("plots/userTimes.pdf")

def plotGameTimes(games):
	gameTimes = []
	for game in games:
		gameTimes.append((game.tEnd - game.tStart).total_seconds())
	bins = np.arange(0, 200, 10)
	fig, ax = plt.subplots()
	sns.histplot(np.array(gameTimes), stat='probability', bins=bins)
	ax.set(xlim=((0, 200)), xlabel="Total Game Time (s)", title=f"Median={np.median(gameTimes):.2f}, N={len(gameTimes)}")
	fig.savefig("plots/gameTimes.pdf")

def makeDF():
	dfs = []
	columns = ('user', 'group', 'player', 'game', 'turn', 'reward', 'generosity')
	for user in User.objects.filter(nGames=REQUIRED):
		for player in ["A", "B"]:
			for g, game in enumerate(Game.objects.filter(complete=True, tutorial=False, user=user, userRole=player).order_by('tStart')):
				for t in range(ROUNDS):  # include final move
				# for t in range(ROUNDS-1):  # exclude final move
					give = int(game.userGives.split(',')[:-1][t])
					keep = int(game.userKeeps.split(',')[:-1][t])
					reward = int(game.userRewards.split(',')[:-1][t])
					gen = give/(give+keep) if (give+keep)>0 else np.NaN
					if player=="B" and t==ROUNDS-2: gen = np.NaN  # exclude B's final greedy move
					dfs.append(pd.DataFrame([[
						user.username,
						"generous" if user.group=='1' else "greedy",
						player,
						g,
						t,
						reward,
						gen
					]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	return df

def plotGenVsTime(df):
	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((16,16)))
	dfGenerousA = df.query("group == 'generous' & player == 'A'")
	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
	dfGenerousB = df.query("group == 'generous' & player == 'B'")
	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
	sns.lineplot(data=dfGenerousA, x='game', y='generosity', hue='user', ax=ax)
	sns.lineplot(data=dfGreedyA, x='game', y='generosity', hue='user', ax=ax2)
	sns.lineplot(data=dfGenerousB, x='game', y='generosity', hue='user', ax=ax3)
	sns.lineplot(data=dfGreedyB, x='game', y='generosity', hue='user', ax=ax4)
	ax.set(title="Learn to be Generous, Investor", ylabel='Generosity', xlabel="", ylim=((0, 1)))
	ax2.set(title="Learn to be Greedy, Investor", xlabel="", ylim=((0, 1)))
	ax3.set(title="Learn to be Generous, Trustee", xlabel='Game', ylabel='Generosity', ylim=((0, 1)))
	ax4.set(title="Learn to be Greedy, Trustee", xlabel='Game', ylim=((0, 1)))
	fig.savefig("plots/Generosity_vs_Time.pdf")

def plotScoreVsTime(df):
	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((16,16)))
	dfGenerousA = df.query("group == 'generous' & player == 'A'")
	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
	dfGenerousB = df.query("group == 'generous' & player == 'B'")
	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
	sns.lineplot(data=dfGenerousA, x='game', y='reward', hue='user', ax=ax)
	sns.lineplot(data=dfGreedyA, x='game', y='reward', hue='user', ax=ax2)
	sns.lineplot(data=dfGenerousB, x='game', y='reward', hue='user', ax=ax3)
	sns.lineplot(data=dfGreedyB, x='game', y='reward', hue='user', ax=ax4)
	ax.set(title="Learn to be Generous, Investor", ylabel='Score', xlabel="", ylim=((0, 30)))
	ax2.set(title="Learn to be Greedy, Investor", xlabel="", ylim=((0, 30)))
	ax3.set(title="Learn to be Generous, Trustee", xlabel='Game', ylabel='Score', ylim=((0, 30)))
	ax4.set(title="Learn to be Greedy, Trustee", xlabel='Game', ylim=((0, 30)))
	fig.savefig("plots/Score_vs_Time.pdf")


def plotScoreVsTimeSingle(username, player, games):
	user = User.objects.filter(username=username)[0]
	userGames = games.filter(user=user, userRole=player).order_by('tStart') 
	userScores = []
	for game in userGames:
		score = 0
		for r in game.userRewards.split(',')[:-1]:
			score += int(r)
		userScores.append(score)
		print(userScores)
	fig, ax = plt.subplots()
	sns.lineplot(y=userScores, x=np.arange(0, len(userScores)))
	ax.set(xlabel='Move number', ylabel='Score', ylim=((0, 100)), title=f"User={user}, Player={player}")
	fig.savefig(f"plots/{user}_{player}_Score.pdf")

def plotGenerosityVsTimeSingle(username, player, games):
	user = User.objects.filter(username=username)[0]
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
	fig.savefig(f"plots/{user}_{player}_Generosity.pdf")

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
	fig.savefig(f"plots/{group}_{player}_Score.pdf")

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
	fig.savefig(f"plots/{group}_{player}_Generosity.pdf")



# allGames = Game.objects.filter(complete=True, tutorial=False)
# plotUserTimes(allGames)
# plotGameTimes(allGames)


df = makeDF()
plotGenVsTime(df)
plotScoreVsTime(df)

# plotScoreVsTimeSingle("brent.komer@gmail.com", "A", allGames)
# plotGenerosityVsTimeSingle("brent.komer@gmail.com", "A", allGames)

# plotScoreVsTimeGroup("2", "B", allGames)
# plotGenerosityVsTimeGroup("2", "B", allGames)