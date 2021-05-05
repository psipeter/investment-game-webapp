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
import imageio

def plotSurveys():
	dfs = []
	columns = ('group', 'age', 'gender', 'income', 'education', 'veteran',
		'compensation', 'objective', 'selfLearning', 'otherIdentity', 'otherStrategy', 'otherNumber',
		'empathy', 'risk', 'altruism')
	# for user in User.objects.filter(nGames__gte=1):
	for user in User.objects.filter(nGames__gte=1):
		if user.compensation == '<':
			compensation = 'Less than normal'
		elif user.compensation == '=':
			compensation = 'Normal'
		else:
			compensation = 'More than normal'
		empathy = None
		risk = None
		altruism = None
		if user.empathy=='1': empathy='strongly disagree'
		if user.empathy=='2': empathy='disagree'
		if user.empathy=='3': empathy='undecided'
		if user.empathy=='4': empathy='agree'
		if user.empathy=='5': empathy='strongly agree'
		if user.risk=='1': risk='strongly disagree'
		if user.risk=='2': risk='disagree'
		if user.risk=='3': risk='undecided'
		if user.risk=='4': risk='agree'
		if user.risk=='5': risk='strongly agree'
		if user.altruism=='1': altruism='strongly disagree'
		if user.altruism=='2': altruism='disagree'
		if user.altruism=='3': altruism='undecided'
		if user.altruism=='4': altruism='agree'
		if user.altruism=='5': altruism='strongly agree'
		dfs.append(pd.DataFrame([[
			user.group,
			int(user.age),
			user.gender,
			user.income,
			user.education,
			'yes' if user.veteran=='1' else 'no',
			compensation,
			user.objective if user.objective else 'N/A',
			user.selfLearning if user.selfLearning else 'N/A',
			user.otherIdentity if user.otherIdentity else 'N/A',
			user.otherStrategy if user.otherStrategy else 'N/A',
			user.otherNumber if user.otherNumber else 'N/A',
			empathy,
			risk,
			altruism
		]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	# print(df)

	fig, ax = plt.subplots()
	median = np.median(df['age'])
	sns.histplot(data=df, x='age', ax=ax)
	ax.set(title=f'Age, Median = {median}')
	fig.savefig('plots/age.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='income', ax=ax)
	ax.set(title=f'Income')
	fig.savefig('plots/income.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='gender', ax=ax)
	ax.set(title='Gender')
	fig.savefig('plots/gender.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='veteran', ax=ax)
	ax.set(title="Have you ever played the Prisoner's Dilemma?")
	fig.savefig('plots/veteran.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='compensation', ax=ax)
	ax.set(title="Was the money you earned for completing this HIT appropriate?")
	fig.savefig('plots/compensation.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='objective', hue='group', ax=ax)
	ax.set(title="What was your objective when playing the investment game?")
	fig.savefig('plots/objective.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='selfLearning', hue='group', ax=ax)  # multiple='dodge'
	ax.set(title="Were you able to learn an effective strategy?")
	fig.savefig('plots/selfLearning.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='otherIdentity', hue='group',  ax=ax)  # multiple='dodge'
	ax.set(title="What were your beliefs about the identity of your opponents?")
	fig.savefig('plots/otherIdentity.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='otherStrategy', hue='group',  ax=ax)  # multiple='dodge'
	ax.set(title="How would you describe the strategies of your opponents?")
	fig.savefig('plots/otherStrategy.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='otherNumber', hue='group',  ax=ax)  # multiple='dodge'
	ax.set(title="What were your beliefs about the number of opponents you played?")
	fig.savefig('plots/otherNumber.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='empathy', ax=ax)
	ax.set_title("I am confident that I understand what others \n are thinking or feeling during conversation")
	fig.savefig('plots/empathy.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='risk', ax=ax)
	ax.set_title("A coworker approaches you and asks for a $1000 loan, \npromising to return you the money, plus 20% interest, in a month. \nI would trust them and loan them the money")
	plt.tight_layout()
	fig.savefig('plots/risk.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='altruism', ax=ax)
	ax.set_title("I win a million dollars in the lottery. \n I would keep the money for myself \n rather than giving it away to friends, family, or charity")
	fig.savefig('plots/altruism.pdf')

# plotSurveys()

def plotTimes():
	games = Game.objects.filter(complete=True, tutorial=False)
	userTimes = []
	for game in games:
		for t in game.userTimes.split(',')[:-1]:
			userTimes.append(float(t))
	gameTimes = []
	for game in games:
		gameTimes.append((game.tEnd - game.tStart).total_seconds())

	bins = np.arange(0, 20, 0.5)
	fig, ax = plt.subplots()
	sns.histplot(np.array(userTimes), stat='probability', bins=bins)
	ax.set(xlim=((0, 20)), xlabel="User Response Time (s)", title=f"Median={np.median(userTimes):.2f}, N={len(userTimes)}")
	fig.savefig("plots/userTimes.pdf")

	bins = np.arange(0, 200, 10)
	fig, ax = plt.subplots()
	sns.histplot(np.array(gameTimes), stat='probability', bins=bins)
	ax.set(xlim=((0, 200)), xlabel="Total Game Time (s)", title=f"Median={np.median(gameTimes):.2f}, N={len(gameTimes)}")
	fig.savefig("plots/gameTimes.pdf")

# plotTimes()


def plotScoreGenByGroup():
	dfs = []
	columns = ('user', 'group', 'player', 'game', 'turn', 'reward', 'generosity')
	for user in User.objects.filter(nGames=REQUIRED):
		for player in ["A", "B"]:
			for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
				for t in range(TURNS):
					give = int(game.userGives.split(',')[:-1][t])
					keep = int(game.userKeeps.split(',')[:-1][t])
					reward = int(game.userRewards.split(',')[:-1][t])
					gen = give/(give+keep) if (give+keep)>0 else -0.1  # visual indicator, rather than lose data
					dfs.append(pd.DataFrame([[
						user.username, user.group, player, g, t, reward, gen
					]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	xticks = np.arange(0, int(REQUIRED/2))

	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((12,12)))
	dfGenerousA = df.query("group == 'generous' & player == 'A'")
	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
	dfGenerousB = df.query("group == 'generous' & player == 'B'")
	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
	sns.lineplot(data=dfGenerousA, x='game', y='generosity', ax=ax)
	sns.lineplot(data=dfGreedyA, x='game', y='generosity', ax=ax2)
	sns.lineplot(data=dfGenerousB, x='game', y='generosity', ax=ax3)
	sns.lineplot(data=dfGreedyB, x='game', y='generosity', ax=ax4)
	ax.set(title="Learn to be Generous, Investor", xticks=xticks, ylabel='Generosity', xlabel="", ylim=((-0.1, 1)))
	ax2.set(title="Learn to be Greedy, Investor", xticks=xticks, xlabel="", ylim=((-0.1, 1)))
	ax3.set(title="Learn to be Generous, Trustee", xticks=xticks, xlabel='Game', ylabel='Generosity', ylim=((-0.1, 1)))
	ax4.set(title="Learn to be Greedy, Trustee", xticks=xticks, xlabel='Game', ylim=((-0.1, 1)))
	fig.savefig("plots/GenerosityVsTimeByGroup.pdf")

	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((12,12)))
	dfGenerousA = df.query("group == 'generous' & player == 'A'")
	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
	dfGenerousB = df.query("group == 'generous' & player == 'B'")
	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
	sns.lineplot(data=dfGenerousA, x='game', y='reward', ax=ax)
	sns.lineplot(data=dfGreedyA, x='game', y='reward', ax=ax2)
	sns.lineplot(data=dfGenerousB, x='game', y='reward', ax=ax3)
	sns.lineplot(data=dfGreedyB, x='game', y='reward', ax=ax4)
	ax.set(title="Learn to be Generous, Investor", xticks=xticks, ylabel='Score', xlabel="", ylim=((0, 30)))
	ax2.set(title="Learn to be Greedy, Investor", xticks=xticks, xlabel="", ylim=((0, 30)))
	ax3.set(title="Learn to be Generous, Trustee", xticks=xticks, xlabel='Game', ylabel='Score', ylim=((0, 30)))
	ax4.set(title="Learn to be Greedy, Trustee", xticks=xticks, xlabel='Game', ylim=((0, 30)))
	fig.savefig("plots/ScoreVsTimeByGroup.pdf")

plotScoreGenByGroup()


def plotHistByGroup():
	dfs = []
	columns = ('user', 'group', 'player', 'game', 'turn', 'move', 'generosity', 'reward')
	for group in ["generous", "greedy"]:
		for player in ["A", "B"]:
			for user in User.objects.filter(nGames=REQUIRED, group=group):
				for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
					for t in range(TURNS):  # include final move
						give = int(game.userGives.split(',')[:-1][t])
						keep = int(game.userKeeps.split(',')[:-1][t])
						gen = give/(give+keep) if (give+keep)>0 else -0.1
						reward = int(game.userRewards.split(',')[:-1][t])
						dfs.append(pd.DataFrame([[
							user.username, user.group, player, g, t, g*TURNS + t, gen, reward
						]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	
	for group in ["generous", "greedy"]:
		for player in ["A", "B"]:
			xlim = ((0, 15)) if player=="A" else ((0, 30))
			bins = np.linspace(0, 15, 16) if player=="A" else np.linspace(0, 30, 11)
			images = []
			for g in range(int(REQUIRED/2)):
				for t in range(TURNS):
					move = g*TURNS + t
					data = df.query('group==@group & player==@player & move==@move')
					fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=((12, 6)))
					sns.histplot(data=data, x='generosity', ax=ax, stat='probability', bins=np.linspace(-0.1, 1, 12))
					sns.histplot(data=data, x='reward', ax=ax2, stat='probability', bins=bins)
					ax.set(ylim=(0, 1), xlim=(-0.1, 1), title=f'Generosity: {group}, {player}, game {g}, turn {t}')
					ax2.set(ylim=(0, 1), xlim=xlim, title=f'Score: {group}, {player}, game {g}, turn {t}')
					fig.savefig(f'plots/HistByGroup/{group}_{player}_{move}.png')
					# images.append(imageio.imread(f'plots/GenHistOverTime/{group}_{player}_{t}.png'))
					plt.close('all')
			# imageio.mimsave(f'plots/GenHistOverTime/{group}_{player}_all.gif', images)

# plotHistByGroup()



def plotObjectiveVsGenScore():
	dfs = []
	columns = ('user', 'group', 'player', 'objective', 'game', 'turn', 'reward', 'generosity')
	for user in User.objects.filter(nGames=REQUIRED):
		if not user.objective: continue
		for player in ["A", "B"]:
			for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
				for t in range(TURNS):
					give = int(game.userGives.split(',')[:-1][t])
					keep = int(game.userKeeps.split(',')[:-1][t])
					reward = int(game.userRewards.split(',')[:-1][t])
					gen = give/(give+keep) if (give+keep)>0 else -0.1  # visual indicator, rather than lose data
					dfs.append(pd.DataFrame([[
						user.username, user.group, player, user.objective, g, t, reward, gen
					]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2)
	sns.barplot(data=df, x='objective', y='generosity', hue='group', ax=ax)
	sns.barplot(data=df, x='objective', y='reward', hue='group', ax=ax2)
	plt.tight_layout()
	fig.savefig(f'plots/ObjectiveVsGenScore.pdf')

# plotObjectiveVsGenScore()


def plotSelfLearningVsScore():
	dfs = []
	columns = ('user', 'group', 'player', 'selfLearning', 'game', 'turn', 'reward', 'generosity')
	for user in User.objects.filter(nGames=REQUIRED):
		if not user.selfLearning: continue
		for player in ["A", "B"]:
			for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
				for t in range(TURNS):
					give = int(game.userGives.split(',')[:-1][t])
					keep = int(game.userKeeps.split(',')[:-1][t])
					reward = int(game.userRewards.split(',')[:-1][t])
					gen = give/(give+keep) if (give+keep)>0 else -0.1  # visual indicator, rather than lose data
					dfs.append(pd.DataFrame([[
						user.username, user.group, player, user.selfLearning, g, t, reward, gen
					]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	fig, ax = plt.subplots()
	sns.barplot(data=df, x='selfLearning', y='reward', hue='group', ax=ax, order=['slow', 'good', 'fast'])
	ax.set(title="Were you able to learn an effective strategy?")
	fig.savefig(f'plots/selfLearningVsScore.pdf')

# plotSelfLearningVsScore()


def plotResponseTimeVsGenScore():
	dfs = []
	columns = ('user', 'group', 'player', 'response time', 'reward', 'generosity')
	for user in User.objects.filter(nGames=REQUIRED):
		for player in ["A", "B"]:
			times = []
			rewards = []
			gens = []
			for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
				for t in range(TURNS):
					give = int(game.userGives.split(',')[:-1][t])
					keep = int(game.userKeeps.split(',')[:-1][t])
					time = float(game.userTimes.split(',')[:-1][t])
					reward = int(game.userRewards.split(',')[:-1][t])
					gen = give/(give+keep) if (give+keep)>0 else -0.1  # visual indicator, rather than lose data
					times.append(time)
					rewards.append(reward)
					gens.append(gen)
			dfs.append(pd.DataFrame([[
				user.username, user.group, player, np.mean(times), np.mean(rewards), np.mean(gens)
			]], columns=columns))			
	df = pd.concat([df for df in dfs], ignore_index=True)
	fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
	sns.scatterplot(data=df, x='response time', y='reward', hue='group', ax=ax)
	sns.scatterplot(data=df, x='response time', y='generosity', hue='group', ax=ax2)
	ax.set(xlim=((0, 100)))
	ax2.set(xlim=((0, 100)))
	fig.savefig(f'plots/ResponseTimeVsGenScore.pdf')

# plotResponseTimeVsGenScore()



def plotWinningsVsResponseTime():
	dfs = []
	columns = ('user', 'group', 'player', 'response time', 'winnings')
	for user in User.objects.filter(nGames=REQUIRED):
		for player in ["A", "B"]:
			times = []
			rewards = []
			gens = []
			for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
				for t in range(TURNS):
					time = float(game.userTimes.split(',')[:-1][t])
					if time>30:
						continue  # skip datapoint if time is greater than 30s (AFK)
					times.append(time)
			dfs.append(pd.DataFrame([[
				user.username, user.group, player, np.mean(times), float(user.winnings)
			]], columns=columns))			
	df = pd.concat([df for df in dfs], ignore_index=True)
	fig, ((ax, ax2),(ax3,ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((12,12)))
	sns.regplot(data=df.query('player=="A" & group=="greedy"'), x='response time', y='winnings', ax=ax)
	sns.regplot(data=df.query('player=="B" & group=="greedy"'), x='response time', y='winnings', ax=ax2)
	sns.regplot(data=df.query('player=="A" & group=="generous"'), x='response time', y='winnings', ax=ax3)
	sns.regplot(data=df.query('player=="B" & group=="generous"'), x='response time', y='winnings', ax=ax4)
	ax.set(title='Player A, Group Greedy', ylim=((3, 6)))
	ax2.set(title='Player B, Group Greedy', ylim=((3, 6)))
	ax3.set(title='Player A, Group Generous', ylim=((3, 6)))
	ax4.set(title='Player B, Group Generous', ylim=((3, 6)))
	fig.savefig(f'plots/WinningsVsResponseTime.pdf')

# plotWinningsVsResponseTime()


def plotScoreGenVsLikert():
	dfs = []
	columns = ('user', 'group', 'player', 'risk', 'empathy', 'altruism', 'reward', 'generosity', 'E', 'R', 'A')
	for user in User.objects.filter(nGames=REQUIRED):
		empathy = None
		risk = None
		altruism = None
		if user.empathy=='1': empathy, E='D!', 0
		if user.empathy=='2': empathy, E='D', 1
		if user.empathy=='3': empathy, E='?', 2
		if user.empathy=='4': empathy, E='A', 3
		if user.empathy=='5': empathy, E='A!', 4
		if user.risk=='1': risk, R='D!', 0
		if user.risk=='2': risk, R='D', 1
		if user.risk=='3': risk, R='?', 2
		if user.risk=='4': risk, R='A', 3
		if user.risk=='5': risk, R='A!', 4
		if user.altruism=='1': altruism, A = 'D!', 0
		if user.altruism=='2': altruism, A = 'D', 1
		if user.altruism=='3': altruism, A = '?', 2
		if user.altruism=='4': altruism, A = 'A', 3
		if user.altruism=='5': altruism, A = 'A!', 4
		if empathy==None or risk==None or altruism==None: continue
		for player in ["A", "B"]:
			times = []
			rewards = []
			gens = []
			for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
				for t in range(TURNS):
					give = int(game.userGives.split(',')[:-1][t])
					keep = int(game.userKeeps.split(',')[:-1][t])
					time = float(game.userTimes.split(',')[:-1][t])
					reward = int(game.userRewards.split(',')[:-1][t])
					gen = give/(give+keep) if (give+keep)>0 else -0.1  # visual indicator, rather than lose data
					times.append(time)
					rewards.append(reward)
					gens.append(gen)
			dfs.append(pd.DataFrame([[
				user.username, user.group, player, risk, empathy, altruism, np.mean(rewards), np.mean(gens),E,R,A
			]], columns=columns))			
	df = pd.concat([df for df in dfs], ignore_index=True)

	fig, ((ax, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(nrows=2, ncols=3, sharex=True, figsize=((12, 12)))
	sns.barplot(data=df, x='E', y='reward', ax=ax)
	sns.barplot(data=df, x='E', y='generosity', ax=ax4)
	sns.barplot(data=df, x='R', y='reward', ax=ax2)
	sns.barplot(data=df, x='R', y='generosity', ax=ax5)
	sns.barplot(data=df, x='A', y='reward', ax=ax3)
	sns.barplot(data=df, x='A', y='generosity', ax=ax6)
	ax.set(xticklabels=['D!', 'D', '?', 'A', 'A!'], xlabel='', title='empathy')
	ax2.set(xticklabels=['D!', 'D', '?', 'A', 'A!'], xlabel='', ylabel='', title='risk')
	ax3.set(xticklabels=['D!', 'D', '?', 'A', 'A!'], xlabel='', ylabel='', title='altruism')
	ax4.set(xlabel='', xticklabels=['D!', 'D', '?', 'A', 'A!'], ylim=((0, 1)))
	ax5.set(xlabel='', xticklabels=['D!', 'D', '?', 'A', 'A!'], ylabel='', ylim=((0, 1)))
	ax6.set(xlabel='', xticklabels=['D!', 'D', '?', 'A', 'A!'], ylabel='', ylim=((0, 1)))
	plt.tight_layout()
	fig.savefig(f'plots/ScoreGenVsLikert.pdf')

# plotScoreGenVsLikert()








































def makeDF():
	dfs = []
	columns = ('user', 'group', 'player', 'game', 'turn', 'reward', 'generosity')
	for user in User.objects.filter(nGames=REQUIRED):
		for player in ["A", "B"]:
			for g, game in enumerate(Game.objects.filter(complete=True, tutorial=False, user=user, userRole=player).order_by('tStart')):
				for t in range(TURNS):  # include final move
				# for t in range(ROUNDS-1):  # exclude final move
					give = int(game.userGives.split(',')[:-1][t])
					keep = int(game.userKeeps.split(',')[:-1][t])
					reward = int(game.userRewards.split(',')[:-1][t])
					gen = give/(give+keep) if (give+keep)>0 else np.NaN
					# if player=="B" and t==TURNS-2: gen = np.NaN  # exclude B's final greedy move
					dfs.append(pd.DataFrame([[
						user.username,
						user.group,
						player,
						g,
						t,
						reward,
						gen
					]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	return df

	dfs2 = []
	columns = ('group', 'player', 'move', 'min-reward', 'max-reward', 'mean-reward',
		'min-gen', 'max-gen', 'mean-gen')
	for group in ['greedy', 'generous']:
		for player in ["A", "B"]:
			for game in range(int(REQUIRED/2)):
				for turn in range(TURNS-1):
					dfUsers = df.query('group==@group & player==@player & game==@game & turn==@turn')
					dfs2.append(pd.DataFrame([[
						group,
						player,
						game*(TURNS-1) + turn,
						np.min(dfUsers['reward']),
						np.max(dfUsers['reward']),
						np.mean(dfUsers['reward']),
						np.min(dfUsers['generosity']),
						np.max(dfUsers['generosity']),
						np.mean(dfUsers['generosity']),
					]], columns=columns))
	df2 = pd.concat([df for df in dfs2], ignore_index=True)
	return df2

# def plotGenVsTime(df, byUser=False):
# 	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((16,16)))
# 	dfGenerousA = df.query("group == 'generous' & player == 'A'")
# 	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
# 	dfGenerousB = df.query("group == 'generous' & player == 'B'")
# 	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
# 	sns.lineplot(data=dfGenerousA, x='move', y='mean-gen', ax=ax)
# 	sns.lineplot(data=dfGreedyA, x='move', y='mean-gen', ax=ax2)
# 	sns.lineplot(data=dfGenerousB, x='move', y='mean-gen', ax=ax3)
# 	sns.lineplot(data=dfGreedyB, x='move', y='mean-gen', ax=ax4)
# 	ax.set(title="Learn to be Generous, Investor", ylabel='Generosity', xlabel="", ylim=((0, 1)))
# 	ax2.set(title="Learn to be Greedy, Investor", xlabel="", ylim=((0, 1)))
# 	ax3.set(title="Learn to be Generous, Trustee", xlabel='Game', ylabel='Generosity', ylim=((0, 1)))
# 	ax4.set(title="Learn to be Greedy, Trustee", xlabel='Game', ylim=((0, 1)))
# 	ax.fill_between(np.arange(0, len(dfGenerousA['move'])), dfGenerousA['min-gen'], dfGenerousA['max-gen'], alpha=0.1)	
# 	ax2.fill_between(np.arange(0, len(dfGreedyA['move'])), dfGreedyA['min-gen'], dfGreedyA['max-gen'], alpha=0.1)	
# 	ax3.fill_between(np.arange(0, len(dfGenerousB['move'])), dfGenerousB['min-gen'], dfGenerousB['max-gen'], alpha=0.1)	
# 	ax4.fill_between(np.arange(0, len(dfGreedyB['move'])), dfGreedyB['min-gen'], dfGreedyB['max-gen'], alpha=0.1)	
# 	fig.savefig("plots/Generosity_vs_Time.pdf")

# def plotScoreVsTime(df, byUser=False):
# 	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((16,16)))
# 	dfGenerousA = df.query("group == 'generous' & player == 'A'")
# 	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
# 	dfGenerousB = df.query("group == 'generous' & player == 'B'")
# 	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
# 	sns.lineplot(data=dfGenerousA, x='move', y='mean-reward', ax=ax)
# 	sns.lineplot(data=dfGreedyA, x='move', y='mean-reward', ax=ax2)
# 	sns.lineplot(data=dfGenerousB, x='move', y='mean-reward', ax=ax3)
# 	sns.lineplot(data=dfGreedyB, x='move', y='mean-reward', ax=ax4)
# 	ax.fill_between(np.arange(0, len(dfGenerousA['move'])), dfGenerousA['min-reward'], dfGenerousA['max-reward'], alpha=0.1)	
# 	ax2.fill_between(np.arange(0, len(dfGreedyA['move'])), dfGreedyA['min-reward'], dfGreedyA['max-reward'], alpha=0.1)	
# 	ax3.fill_between(np.arange(0, len(dfGenerousB['move'])), dfGenerousB['min-reward'], dfGenerousB['max-reward'], alpha=0.1)	
# 	ax4.fill_between(np.arange(0, len(dfGreedyB['move'])), dfGreedyB['min-reward'], dfGreedyB['max-reward'], alpha=0.1)	
# 	ax.set(title="Learn to be Generous, Investor", ylabel='Score', xlabel="", ylim=((0, 30)))
# 	ax2.set(title="Learn to be Greedy, Investor", xlabel="", ylim=((0, 30)))
# 	ax3.set(title="Learn to be Generous, Trustee", xlabel='Game', ylabel='Score', ylim=((0, 30)))
# 	ax4.set(title="Learn to be Greedy, Trustee", xlabel='Game', ylim=((0, 30)))
# 	fig.savefig("plots/Score_vs_Time.pdf")

def plotGenVsTime(df, byUser=False):
	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((16,16)))
	dfGenerousA = df.query("group == 'generous' & player == 'A'")
	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
	dfGenerousB = df.query("group == 'generous' & player == 'B'")
	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
	if byUser:
		sns.lineplot(data=dfGenerousA, x='game', y='generosity', hue='user', ax=ax)
		sns.lineplot(data=dfGreedyA, x='game', y='generosity', hue='user', ax=ax2)
		sns.lineplot(data=dfGenerousB, x='game', y='generosity', hue='user', ax=ax3)
		sns.lineplot(data=dfGreedyB, x='game', y='generosity', hue='user', ax=ax4)
	else:
		sns.lineplot(data=dfGenerousA, x='game', y='generosity', ax=ax)
		sns.lineplot(data=dfGreedyA, x='game', y='generosity', ax=ax2)
		sns.lineplot(data=dfGenerousB, x='game', y='generosity', ax=ax3)
		sns.lineplot(data=dfGreedyB, x='game', y='generosity', ax=ax4)
	ax.set(title="Learn to be Generous, Investor", ylabel='Generosity', xlabel="", ylim=((0, 1)))
	ax2.set(title="Learn to be Greedy, Investor", xlabel="", ylim=((0, 1)))
	ax3.set(title="Learn to be Generous, Trustee", xlabel='Game', ylabel='Generosity', ylim=((0, 1)))
	ax4.set(title="Learn to be Greedy, Trustee", xlabel='Game', ylim=((0, 1)))
	fig.savefig("plots/Generosity_vs_Time.pdf")

def plotScoreVsTime(df, byUser=False):
	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((16,16)))
	dfGenerousA = df.query("group == 'generous' & player == 'A'")
	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
	dfGenerousB = df.query("group == 'generous' & player == 'B'")
	dfGreedyB = df.query("group == 'greedy' & player == 'B'")

	if byUser:
		sns.lineplot(data=dfGenerousA, x='game', y='reward', hue='user', ax=ax)
		sns.lineplot(data=dfGreedyA, x='game', y='reward', hue='user', ax=ax2)
		sns.lineplot(data=dfGenerousB, x='game', y='reward', hue='user', ax=ax3)
		sns.lineplot(data=dfGreedyB, x='game', y='reward', hue='user', ax=ax4)
	else:
		sns.lineplot(data=dfGenerousA, x='game', y='reward', ax=ax)
		sns.lineplot(data=dfGreedyA, x='game', y='reward', ax=ax2)
		sns.lineplot(data=dfGenerousB, x='game', y='reward', ax=ax3)
		sns.lineplot(data=dfGreedyB, x='game', y='reward', ax=ax4)
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
		userScores.append(score/TURNS)
	fig, ax = plt.subplots()
	sns.lineplot(y=userScores, x=np.arange(0, len(userScores)))
	ax.set(xlabel='Move number', ylabel='Score', ylim=((0, CAPITAL*MATCH)), title=f"User={user}, Group={user.group}, Player={player}")
	fig.savefig(f"plots/users/{user}_{user.group}_{player}_Score.pdf")

def plotGenerosityVsTimeSingle(username, player, games):
	user = User.objects.filter(username=username)[0]
	userGames = games.filter(user=user, userRole=player).order_by('tStart') 
	userGenerosities = []
	for game in userGames:
		for r in range(TURNS):
			give = int(game.userGives.split(',')[:-1][r])
			keep = int(game.userKeeps.split(',')[:-1][r])
			if (give+keep) > 0:
				userGenerosities.append(give/(give+keep))
	fig, ax = plt.subplots()
	sns.lineplot(y=userGenerosities, x=np.arange(0, len(userGenerosities)))
	ax.set(xlabel='Move number', ylabel='Generosity', ylim=((-0.01, 1)), title=f"User={user}, Group={user.group}, Player={player}")
	fig.savefig(f"plots/users/{user}_{user.group}_{player}_Generosity.pdf")


def plotGenHistOverTime():
	dfs = []
	columns = ('user', 'group', 'player', 'move', 'generosity')
	for group in ["generous", "greedy"]:
		for player in ["A", "B"]:
			for user in User.objects.filter(nGames=REQUIRED, group=group):
				for g, game in enumerate(Game.objects.filter(complete=True, tutorial=False, user=user, userRole=player).order_by('tStart')):
					for t in range(TURNS):  # include final move
					# for t in range(TURNS-1):  # include final move
						give = int(game.userGives.split(',')[:-1][t])
						keep = int(game.userKeeps.split(',')[:-1][t])
						gen = give/(give+keep) if (give+keep)>0 else np.NaN
						# if player=="B" and t==TURNS-2: gen = np.NaN  # exclude B's final greedy move
						dfs.append(pd.DataFrame([[
							user.username,
							user.group,
							player,
							g*TURNS + t,
							# g*(TURNS-1) + t,
							gen
						]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	
	for group in ["generous", "greedy"]:
		for player in ["A", "B"]:
			images = []
			for t in range(int(REQUIRED/2)*TURNS):
			# for t in range(int(REQUIRED/2)*(TURNS-1)):
				data = df.query('group==@group & player==@player & move==@t')
				fig, ax = plt.subplots()
				sns.histplot(data=data, x='generosity', ax=ax, stat='probability', bins=np.linspace(0, 1, 11))
				ax.set(ylim=(0, 1), xlim=(0, 1), title=f'{group}, {player}, {t}')
				fig.savefig(f'plots/GenHistOverTime/{group}_{player}_{t}.png')
				images.append(imageio.imread(f'plots/GenHistOverTime/{group}_{player}_{t}.png'))
				plt.close('all')
			imageio.mimsave(f'plots/GenHistOverTime/{group}_{player}_all.gif', images)

			# from matplotlib.animation import FuncAnimation
			# nFrames = int(REQUIRED/2)*(TURNS-1)
			# def animate(i):
			# 	im = plt.imread(f'plots/GenHistOverTime/{group}_{player}_{i}.pdf')
			# 	plt.imshow()
			# anim = FuncAnimation(plt.gcf(), animate, frames=nFrames, interval=(2000.0/nFrames))
			# anim.save(f'plots/GenHistOverTime/{group}_{player}_all.gif', writer='imagemagick')

# plotGenHistOverTime()

# def plotScoreVsTimeGroup(group, player, games):
# 	users = User.objects.filter(group=group)
# 	dfs = []
# 	columns = ('user', 'Game', 'Score')
# 	for user in users:
# 		userGames = games.filter(user=user, userRole=player).order_by('tStart')
# 		for g in range(len(userGames)):
# 			game = userGames[g]
# 			score = 0
# 			for r in game.userRewards.split(',')[:-1]:
# 				score += int(r)
# 			dfs.append(pd.DataFrame([[user, g, score]], columns=columns))
# 	df = pd.concat([df for df in dfs], ignore_index=True)
# 	fig, ax = plt.subplots()
# 	sns.lineplot(data=df, x='Game', y='Score')
# 	ax.set(title=f"Group={group}, Player={player}")
# 	fig.savefig(f"plots/{group}_{player}_Score.pdf")

# def plotGenerosityVsTimeGroup(group, player, games):
# 	users = User.objects.filter(group=group)
# 	dfs = []
# 	columns = ('user', 'Game', 'Round', 'Generosity')
# 	for user in users:
# 		userGames = games.filter(user=user, userRole=player).order_by('tStart')
# 		for g in range(len(userGames)):
# 			game = userGames[g]
# 			for r in range(ROUNDS):
# 				give = int(game.userGives.split(',')[:-1][r])
# 				keep = int(game.userKeeps.split(',')[:-1][r])
# 				if (give+keep) > 0:
# 					dfs.append(pd.DataFrame([[game.user, g, r, give/(give+keep)]], columns=columns))
# 	df = pd.concat([df for df in dfs], ignore_index=True)
# 	fig, ax = plt.subplots()
# 	sns.lineplot(data=df, x='Game', y='Generosity')
# 	ax.set(ylim=((0, 1)), title=f"Group={group}, Player={player}")
# 	fig.savefig(f"plots/{group}_{player}_Generosity.pdf")



# allGames = Game.objects.filter(complete=True, tutorial=False)

# plotUserTimes(allGames)
# plotGameTimes(allGames)


# df = makeDF()
# plotScoreVsTime(df)
# plotGenVsTime(df)

# for user in User.objects.filter(nGames=REQUIRED):
# 	for player in ['A', 'B']:
# 		plotScoreVsTimeSingle(user.username, player, allGames)
# 		plotGenerosityVsTimeSingle(user.username, player, allGames)

# surveyDF = surveyDF()
# plotSurveys(surveyDF)