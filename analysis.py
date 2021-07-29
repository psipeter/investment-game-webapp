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

from statannot import add_stat_annotation
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from scipy.spatial.distance import jensenshannon
from scipy.ndimage import histogram, gaussian_filter1d
from scipy.stats import ttest_ind, entropy, ks_2samp, chisquare

sns.set_context(rc = {'patch.linewidth': 0})
palette = sns.color_palette('deep')
sns.set(context='paper', style='white', font='CMU Serif',
    rc={'font.size':10, 'mathtext.fontset': 'cm', 'axes.labelpad':0, 'axes.linewidth': 0.5, 'axes.titlepad': 20, 'axes.titlesize': 14})
pvalue_thresholds = [[1e-3, "***"], [1e-2, "**"], [1e-1, "*"], [1e0, "ns"]]

def plotSurveys():
	dfs = []
	columns = ('group', 'age', 'gender', 'income', 'education', 'veteran',
		'compensation', 'objective', 'selfLearning', 'otherIdentity', 'otherStrategy', 'otherNumber',
		'empathy', 'risk', 'altruism', 'avatar', 'winnings')
	# for user in User.objects.filter(nGames__gte=1):
	for user in User.objects.filter(nGames=REQUIRED):
		dfs.append(pd.DataFrame([[
			user.group,
			int(user.age),
			user.gender,
			user.income,
			user.education,
			user.veteran,
			user.compensation if user.compensation else 'N/A',
			user.objective if user.objective else 'N/A',
			user.selfLearning if user.selfLearning else 'N/A',
			user.otherIdentity if user.otherIdentity else 'N/A',
			user.otherStrategy if user.otherStrategy else 'N/A',
			user.otherNumber if user.otherNumber else 'N/A',
			user.empathy if user.empathy else 'N/A',
			user.risk if user.risk else 'N/A',
			user.altruism if user.altruism else 'N/A',
			user.avatar, 
			user.winnings,
		]], columns=columns))
	df = pd.concat([df for df in dfs], ignore_index=True)
	# print(f'Total users: {User.objects.filter(nGames=REQUIRED).count()}')
	# print(f'Female users: {User.objects.filter(nGames=REQUIRED, gender="f").count()}')
	# print(f'Believe opponent is a computer: {User.objects.filter(nGames=REQUIRED, otherIdentity="computer").count()}')
	# print(f'Believe opponent is sometimes human: {User.objects.filter(nGames=REQUIRED, otherIdentity="human").count() + User.objects.filter(nGames=REQUIRED, otherIdentity="mix").count()}')
	# print(f'Believe opponent is the same every game: {User.objects.filter(nGames=REQUIRED, otherNumber="same").count()}')
	# print(f'Believe opponent is sometimes unique: {User.objects.filter(nGames=REQUIRED, otherNumber="mix").count() + User.objects.filter(nGames=REQUIRED, otherNumber="unique").count()}')

	fig, ax = plt.subplots()
	median = np.median(df['age'])
	sns.histplot(data=df, x='age', ax=ax, bins=np.arange(18, 118, 5), shrink=0.95, color="#1f77b4bf")
	ax.set(xlim=((17, 69)), xlabel='Age')
	fig.savefig('plots/age.pdf')
	fig.savefig('plots/age.svg')


	incomes = ['20k', '40k', '60k', '80k', '100k', '>100k']
	incomes_count = []
	for i in range(len(incomes)):
		inc = incomes[i]
		incomes_count.append(len(df.query("income == @inc")))
	fig, ax = plt.subplots()
	# sns.histplot(data=df, x='income', ax=ax)
	sns.barplot(x=incomes, y=incomes_count, ax=ax)
	for patch in ax.patches:
		current_width = patch.get_width()
		patch.set_width(0.9)
		patch.set_linewidth(0)
		# patch.set_color(palette[0])
		patch.set_color("#1f77b4bf")
		patch.set_edgecolor('k')
		patch.set_x(patch.get_x() + current_width - 0.85)
	ax.set(xlabel=f'Income', ylabel='Count')
	fig.savefig('plots/income.pdf')
	fig.savefig('plots/income.svg')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='gender', ax=ax, shrink=0.9)
	ax.set(xlabel='Gender')
	ax.set_xticklabels(['Male', 'Female'])
	fig.savefig('plots/gender.pdf')
	fig.savefig('plots/gender.svg')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='veteran', ax=ax)
	ax.set(title="Have you ever played the Prisoner's Dilemma?")
	fig.savefig('plots/veteran.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='compensation', ax=ax)
	ax.set(title="Was the money you earned for completing this HIT appropriate?")
	fig.savefig('plots/compensation.pdf')

	ys = [
		len(df.query('objective=="equal" & group=="generous"')),
		len(df.query('objective=="equal" & group=="greedy"')),
		len(df.query('objective=="self" & group=="generous"')),
		len(df.query('objective=="self" & group=="greedy"')),
		len(df.query('objective=="random" & group=="generous"')),
		len(df.query('objective=="random" & group=="greedy"')),
	]
	fig, ax = plt.subplots()
	sns.histplot(data=df, x='objective', hue='group', ax=ax, multiple="dodge", shrink=0.9)
	# ax.set(title="What was your objective when playing the investment game?")
	ax.set(xlabel='', title="Orientation")
	# ax.set_xticklabels(['socially oriented', 'self oriented', 'n/a', 'random'])
	for i, v in enumerate(ys):
		plt.text(x=i/3, y=v, s=f"{v}")
	fig.savefig('plots/orientation.pdf')
	fig.savefig('plots/orientation.svg')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='selfLearning', hue='group', ax=ax)  # multiple='dodge'
	ax.set(title="Were you able to learn an effective strategy?")
	fig.savefig('plots/selfLearning.pdf')

	ys = [
		len(df.query('otherIdentity=="computer" & group=="generous"')),
		len(df.query('otherIdentity=="computer" & group=="greedy"')),
		len(df.query('otherIdentity=="human" & group=="generous"')),
		len(df.query('otherIdentity=="human" & group=="greedy"')),
		len(df.query('otherIdentity=="mix" & group=="generous"')),
		len(df.query('otherIdentity=="mix" & group=="greedy"')),
	]
	fig, ax = plt.subplots()
	sns.histplot(data=df, x='otherIdentity', hue='group', ax=ax, multiple="dodge", shrink=0.9)  # multiple='dodge'
	# ax.set_xticklabels(['computer', 'human', 'n/a', 'mix'])
	ax.set(xlabel='', title="Opponent Identity")
	for i, v in enumerate(ys):
		plt.text(x=i/3, y=v, s=f"{v}")
	fig.savefig('plots/otherIdentity.pdf')
	fig.savefig('plots/identity.svg')
	raise

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='otherStrategy', hue='group',  ax=ax)  # multiple='dodge'
	ax.set(title="How would you describe the strategies of your opponents?")
	fig.savefig('plots/otherStrategy.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='otherNumber', hue='group',  ax=ax)  # multiple='dodge'
	ax.set(title="What were your beliefs about the number of opponents you played?")
	fig.savefig('plots/otherNumber.pdf')

	answers = ['D!', 'D', 'U', 'A', 'A!']
	answers_verbose = ['Strongly\nDisagree', 'Disagree', 'Undecided', 'Agree', 'Stongly\nAgree']
	counts = []
	for i in range(len(answers)):
		answer = answers[i]
		counts.append(len(df.query("empathy == @answer")))
	fig, ax = plt.subplots()
	# sns.histplot(data=df, x='income', ax=ax)
	sns.barplot(x=answers, y=counts, ax=ax)
	for patch in ax.patches:
		current_width = patch.get_width()
		patch.set_width(0.9)
		patch.set_linewidth(0)
		patch.set_color("#1f77b4bf")
		patch.set_edgecolor('k')
		patch.set_x(patch.get_x() + current_width - 0.85)
	ax.set(xlabel='', ylabel='Count', title="Empathy")
	# ax.set(xlabel='', ylabel='Count', title=r"$\bf{Empathy}$" '\nI am confident that I understand what others \n are thinking or feeling during conversation')
	ax.set_xticklabels(answers_verbose)
	plt.tight_layout()
	fig.savefig('plots/empathy.pdf')
	fig.savefig('plots/empathy.svg')


	answers = ['D!', 'D', 'U', 'A', 'A!']
	answers_verbose = ['Strongly\nDisagree', 'Disagree', 'Undecided', 'Agree', 'Stongly\nAgree']
	counts = []
	for i in range(len(answers)):
		answer = answers[i]
		counts.append(len(df.query("risk == @answer")))
	fig, ax = plt.subplots()
	# sns.histplot(data=df, x='income', ax=ax)
	sns.barplot(x=answers, y=counts, ax=ax)
	for patch in ax.patches:
		current_width = patch.get_width()
		patch.set_width(0.9)
		patch.set_linewidth(0)
		patch.set_color("#1f77b4bf")
		patch.set_edgecolor('k')
		patch.set_x(patch.get_x() + current_width - 0.85)
	ax.set(xlabel='', ylabel='Count', title="Risk")
	# ax.set(xlabel='', ylabel='Count', title=r"$\bf{Risk}$" '\nA coworker approaches you and asks for a $1000 loan, \npromising to return you the money, plus 20% interest, in a month. \nI would trust them and loan them the money')
	ax.set_xticklabels(answers_verbose)
	plt.tight_layout()
	fig.savefig('plots/risk.pdf')
	fig.savefig('plots/risk.svg')

	answers = ['D!', 'D', 'U', 'A', 'A!']
	answers_verbose = ['Strongly\nDisagree', 'Disagree', 'Undecided', 'Agree', 'Stongly\nAgree']
	counts = []
	for i in range(len(answers)):
		answer = answers[i]
		counts.append(len(df.query("altruism == @answer")))
	fig, ax = plt.subplots()
	# sns.histplot(data=df, x='income', ax=ax)
	sns.barplot(x=answers, y=counts, ax=ax)
	for patch in ax.patches:
		current_width = patch.get_width()
		patch.set_width(0.9)
		patch.set_linewidth(0)
		patch.set_color("#1f77b4bf")
		patch.set_edgecolor('k')
		patch.set_x(patch.get_x() + current_width - 0.85)
	ax.set(xlabel='', ylabel='Count', title="Altruism")
	# ax.set(xlabel='', ylabel='Count', title=r"$\bf{Altruism}$" '\nI win a million dollars in the lottery. \n I would keep the money for myself \n rather than giving it away to friends, family, or charity'))
	ax.set_xticklabels(answers_verbose)
	plt.tight_layout()
	fig.savefig('plots/altruism.pdf')
	fig.savefig('plots/altruism.svg')

	# fig, ax = plt.subplots()
	# sns.histplot(data=df, x='empathy', ax=ax)
	# ax.set_title("I am confident that I understand what others \n are thinking or feeling during conversation")
	# fig.savefig('plots/empathy.pdf')

	# fig, ax = plt.subplots()
	# sns.histplot(data=df, x='risk', ax=ax)
	# ax.set_title("A coworker approaches you and asks for a $1000 loan, \npromising to return you the money, plus 20% interest, in a month. \nI would trust them and loan them the money")
	# plt.tight_layout()
	# fig.savefig('plots/risk.pdf')

	# fig, ax = plt.subplots()
	# sns.histplot(data=df, x='altruism', ax=ax)
	# ax.set_title("I win a million dollars in the lottery. \n I would keep the money for myself \n rather than giving it away to friends, family, or charity")
	# fig.savefig('plots/altruism.pdf')

	# fig, ax = plt.subplots(figsize=((12, 12)))
	# sns.barplot(x=['Positive', 'Neutral', 'Bugs/Complaints', 'Requests for new content',  'Strategy Comment'], y=[52, 32, 13, 14, 8], ax=ax)
	# ax.set_title("Free Response Feedback")
	# fig.savefig('plots/feedback.pdf')

	fig, ax = plt.subplots()
	sns.histplot(data=df, x='winnings', ax=ax)
	ax.set(title=f"Winnings: Sum={np.sum(df['winnings']):.1f}, Mean={np.mean(df['winnings']):.2f}, Median={np.median(df['winnings'])}, N={len(df['winnings'])}")
	fig.savefig('plots/Winnings.pdf')

	fig, ax = plt.subplots()
	xticks = np.array([1,2,3,4])
	sns.histplot(data=df, x='avatar', ax=ax)
	ax.set(xticks=xticks, title="Avatar Choice")
	fig.savefig('plots/Avatar.pdf')

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


def plotScoreGenVsSurvey(load=True):
	if not load:
		dfs = []
		userDfs = []
		columns = ('user', 'group', 'player', 'age', 'gender', 'objective', 'altruism', 'risk', 'empathy', 'learning', 'game', 'turn', 'reward', 'generosity')
		userColumns = ('user', 'group', 'objective', 'altruism')
		for user in User.objects.filter(nGames=REQUIRED):
			if user.objective=='equal':
				objective = 'equal'
			elif user.objective=='self':
				objective = 'self'
			else:
				objective = 'n/a'
			if user.altruism=='D!' or user.altruism=='D':
				altruism = 'high'
			elif user.altruism=='A!' or user.altruism=='A':
				altruism = 'low'
			else:
				altruism = 'n/a'
			if user.risk=='D!' or user.risk=='D':
				risk = 'low'
			elif user.risk=='A!' or user.risk=='A':
				risk = 'high'
			else:
				risk = 'n/a'
			if user.empathy=='D!' or user.empathy=='D':
				empathy = 'low'
			elif user.empathy=='A!' or user.empathy=='A':
				empathy = 'high'
			else:
				empathy = 'n/a'
			if user.selfLearning:
				learning = user.selfLearning
			else:
				learning = 'n/a'
			userDfs.append(pd.DataFrame([[user.username, user.group, objective, altruism, ]], columns=userColumns))
			for player in ["A", "B"]:
				for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
					for t in range(TURNS):
						give = int(game.userGives.split(',')[:-1][t])
						keep = int(game.userKeeps.split(',')[:-1][t])
						reward = int(game.userRewards.split(',')[:-1][t])
						gen = give/(give+keep) if (give+keep)>0 else -0.1  # visual indicator, rather than lose data
						dfs.append(pd.DataFrame([[
							user.username, user.group, player, int(user.age), user.gender, objective, altruism, risk, empathy, learning, g, t, reward, gen
						]], columns=columns))
		df = pd.concat([df for df in dfs], ignore_index=True)
		userDf = pd.concat([df for df in userDfs], ignore_index=True)
		df.to_pickle("plots/plotScoreGenVsSurvey_df.pkl")
		userDf.to_pickle("plots/plotScoreGenVsSurvey_userDf.pkl")
	else:
		df = pd.read_pickle("plots/plotScoreGenVsSurvey_df.pkl")
		userDf = pd.read_pickle("plots/plotScoreGenVsSurvey_userDf.pkl")


	# def my_formatter(x, pos):
	# 	"""Format 1 as 1, 0 as 0, and all values whose absolute values is between
	# 	0 and 1 without the leading "0." (e.g., 0.7 is formatted as .7 and -0.4 is
	# 	formatted as -.4)."""
	# 	val_str = '{:g}'.format(x)
	# 	if np.abs(x) > 0 and np.abs(x) < 1:
	# 		return val_str.replace("0", "", 1)
	# 	else:
	# 		return val_str
	# major_formatter = FuncFormatter(my_formatter)

	x = 'group'
	y1 = 'generosity'
	y2 = 'reward'
	order = ['greedy', 'generous']

	hue = 'objective'
	hue_order = ['self', 'equal']
	box_pairs = [((order[0], hue_order[0]), (order[0], hue_order[1])), ((order[1], hue_order[0]), (order[1], hue_order[1]))]
	y1a = np.mean(df.query("group=='greedy' & objective=='self'")['generosity'])
	y1b = np.mean(df.query("group=='greedy' & objective=='equal'")['generosity'])
	y1c = np.mean(df.query("group=='generous' & objective=='self'")['generosity'])
	y1d = np.mean(df.query("group=='generous' & objective=='equal'")['generosity'])
	y2a = np.mean(df.query("group=='greedy' & objective=='self'")['reward'])
	y2b = np.mean(df.query("group=='greedy' & objective=='equal'")['reward'])
	y2c = np.mean(df.query("group=='generous' & objective=='self'")['reward'])
	y2d = np.mean(df.query("group=='generous' & objective=='equal'")['reward'])
	y1ticks = np.around([y1a, y1b, y1c, y1d], decimals=2)
	y2ticks = np.around([y2a, y2b, y2c, y2d], decimals=1)
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)))
	sns.barplot(data=df, x=x, y=y1, hue=hue, hue_order=hue_order, ax=ax)
	sns.barplot(data=df, x=x, y=y2, hue=hue, hue_order=hue_order, ax=ax2)
	add_stat_annotation(ax, data=df, x=x, y=y1, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.17, line_height=0.01)
	add_stat_annotation(ax2, data=df, x=x, y=y2, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.17, line_height=0.01)
	ax.set(xlabel='', ylabel='', ylim=((0.15, 0.5)), yticks=y1ticks)
	ax2.set(xlabel='', ylabel='', ylim=((8, 14.2)), yticks=y2ticks)
	plt.tight_layout()
	ax.legend([Line2D([0], [0], color=palette[0], lw=4), Line2D([0], [0], color=palette[1], lw=4),],
		("self-oriented", "socially-oriented"), loc='upper left', title=hue, frameon=False)
	ax2.get_legend().remove()
	ax.set_xticklabels(['Generous', 'Greedy'])
	ax2.set_xticklabels(['Generous', 'Greedy'])
	ax.set_title("Generosity", pad=20)
	ax2.set_title("Score", pad=20)
	plt.tight_layout()
	sns.despine(top=True, right=True, left=True, bottom=True)
	fig.savefig(f'plots/ScoreGenVsOrientation.pdf')
	fig.savefig(f'plots/ScoreGenVsOrientation.svg')
	raise

	hue = 'altruism'
	hue_order = ['low', 'high']
	box_pairs = [((order[0], hue_order[0]), (order[0], hue_order[1])), ((order[1], hue_order[0]), (order[1], hue_order[1]))]
	y1a = np.mean(df.query("group=='greedy' & altruism=='low'")['generosity'])
	y1b = np.mean(df.query("group=='greedy' & altruism=='high'")['generosity'])
	y1c = np.mean(df.query("group=='generous' & altruism=='low'")['generosity'])
	y1d = np.mean(df.query("group=='generous' & altruism=='high'")['generosity'])
	y2a = np.mean(df.query("group=='greedy' & altruism=='low'")['reward'])
	y2b = np.mean(df.query("group=='greedy' & altruism=='high'")['reward'])
	y2c = np.mean(df.query("group=='generous' & altruism=='low'")['reward'])
	y2d = np.mean(df.query("group=='generous' & altruism=='high'")['reward'])
	y1ticks = np.around([y1a, y1b, y1c, y1d], decimals=2)
	y2ticks = np.around([y2a, y2b, y2c, y2d], decimals=1)
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)))
	sns.barplot(data=df, x=x, y=y1, hue=hue, hue_order=hue_order, ax=ax)
	sns.barplot(data=df, x=x, y=y2, hue=hue, hue_order=hue_order, ax=ax2)
	add_stat_annotation(ax, data=df, x=x, y=y1, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.47, line_height=0.01)
	add_stat_annotation(ax2, data=df, x=x, y=y2, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.2, line_height=0.01)
	plt.tight_layout()
	ax.legend(loc='upper right', title=hue, bbox_to_anchor=(0.9, 0.8), frameon=False)
	ax2.get_legend().remove()
	ax.set(xlabel='', ylabel='', ylim=((0.15, 0.45)), yticks=y1ticks)
	ax2.set(xlabel='', ylabel='', ylim=((8, 14)), yticks=y2ticks)
	ax.set_title("Generosity", pad=20)
	ax2.set_title("Score", pad=20)
	plt.tight_layout()
	sns.despine(top=True, right=True, left=True, bottom=True)
	fig.savefig(f'plots/ScoreGenVsAltruism.pdf')

	hue = 'risk'
	hue_order = ['low', 'high']
	box_pairs = [((order[0], hue_order[0]), (order[0], hue_order[1])), ((order[1], hue_order[0]), (order[1], hue_order[1]))]
	y1a = np.mean(df.query("group=='greedy' & risk=='low'")['generosity'])
	y1b = np.mean(df.query("group=='greedy' & risk=='high'")['generosity'])
	y1c = np.mean(df.query("group=='generous' & risk=='low'")['generosity'])
	y1d = np.mean(df.query("group=='generous' & risk=='high'")['generosity'])
	y2a = np.mean(df.query("group=='greedy' & risk=='low'")['reward'])
	y2b = np.mean(df.query("group=='greedy' & risk=='high'")['reward'])
	y2c = np.mean(df.query("group=='generous' & risk=='low'")['reward'])
	y2d = np.mean(df.query("group=='generous' & risk=='high'")['reward'])
	y1ticks = np.around([y1a, y1b, y1c, y1d], decimals=2)
	y2ticks = np.around([y2a, y2b, y2c, y2d], decimals=1)
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)))
	sns.barplot(data=df, x=x, y=y1, hue=hue, hue_order=hue_order, ax=ax)
	sns.barplot(data=df, x=x, y=y2, hue=hue, hue_order=hue_order, ax=ax2)
	add_stat_annotation(ax, data=df, x=x, y=y1, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.15, line_height=0.01)
	add_stat_annotation(ax2, data=df, x=x, y=y2, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.2, line_height=0.01)
	plt.tight_layout()
	ax.legend(loc='upper right', title=hue, bbox_to_anchor=(0.9, 0.8), frameon=False)
	ax2.get_legend().remove()
	ax.set(xlabel='', ylabel='', ylim=((0.15, 0.5)), yticks=y1ticks)
	ax2.set(xlabel='', ylabel='', ylim=((8, 14)), yticks=y2ticks)
	ax.set_title("Generosity", pad=20)
	ax2.set_title("Score", pad=20)
	plt.tight_layout()
	sns.despine(top=True, right=True, left=True, bottom=True)
	fig.savefig(f'plots/ScoreGenVsRisk.pdf')

	hue = 'empathy'
	hue_order = ['low', 'high']
	box_pairs = [((order[0], hue_order[0]), (order[0], hue_order[1])), ((order[1], hue_order[0]), (order[1], hue_order[1]))]
	y1a = np.mean(df.query("group=='greedy' & empathy=='low'")['generosity'])
	y1b = np.mean(df.query("group=='greedy' & empathy=='high'")['generosity'])
	y1c = np.mean(df.query("group=='generous' & empathy=='low'")['generosity'])
	y1d = np.mean(df.query("group=='generous' & empathy=='high'")['generosity'])
	y2a = np.mean(df.query("group=='greedy' & empathy=='low'")['reward'])
	y2b = np.mean(df.query("group=='greedy' & empathy=='high'")['reward'])
	y2c = np.mean(df.query("group=='generous' & empathy=='low'")['reward'])
	y2d = np.mean(df.query("group=='generous' & empathy=='high'")['reward'])
	y1ticks = np.around([y1a, y1b, y1c, y1d], decimals=2)
	y2ticks = np.around([y2a, y2b, y2c, y2d], decimals=1)
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)))
	sns.barplot(data=df, x=x, y=y1, hue=hue, hue_order=hue_order, ax=ax)
	sns.barplot(data=df, x=x, y=y2, hue=hue, hue_order=hue_order, ax=ax2)
	add_stat_annotation(ax, data=df, x=x, y=y1, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.55, line_height=0.01)
	add_stat_annotation(ax2, data=df, x=x, y=y2, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.2, line_height=0.01)
	plt.tight_layout()
	ax.legend(loc='upper right', title=hue, bbox_to_anchor=(0.9, 0.8), frameon=False)
	ax2.get_legend().remove()
	ax.set(xlabel='', ylabel='', ylim=((0.15, 0.4)), yticks=y1ticks)
	ax2.set(xlabel='', ylabel='', ylim=((8, 14)), yticks=y2ticks)
	ax.set_title("Generosity", pad=20)
	ax2.set_title("Score", pad=20)
	plt.tight_layout()
	sns.despine(top=True, right=True, left=True, bottom=True)
	fig.savefig(f'plots/ScoreGenVsEmpathy.pdf')


	hue = 'gender'
	hue_order = ['m', 'f']
	box_pairs = [((order[0], hue_order[0]), (order[0], hue_order[1])), ((order[1], hue_order[0]), (order[1], hue_order[1]))]
	y1a = np.mean(df.query("group=='greedy' & gender=='m'")['generosity'])
	y1b = np.mean(df.query("group=='greedy' & gender=='f'")['generosity'])
	y1c = np.mean(df.query("group=='generous' & gender=='m'")['generosity'])
	y1d = np.mean(df.query("group=='generous' & gender=='f'")['generosity'])
	y2a = np.mean(df.query("group=='greedy' & gender=='m'")['reward'])
	y2b = np.mean(df.query("group=='greedy' & gender=='f'")['reward'])
	y2c = np.mean(df.query("group=='generous' & gender=='m'")['reward'])
	y2d = np.mean(df.query("group=='generous' & gender=='f'")['reward'])
	y1ticks = np.around([y1a, y1b, y1c, y1d], decimals=2)
	y2ticks = np.around([y2a, y2b, y2c, y2d], decimals=1)
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)))
	sns.barplot(data=df, x=x, y=y1, hue=hue, hue_order=hue_order, ax=ax)
	sns.barplot(data=df, x=x, y=y2, hue=hue, hue_order=hue_order, ax=ax2)
	add_stat_annotation(ax, data=df, x=x, y=y1, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.5, line_height=0.01)
	add_stat_annotation(ax2, data=df, x=x, y=y2, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.2, line_height=0.01)
	plt.tight_layout()
	ax.legend(loc='upper right', title=hue, bbox_to_anchor=(0.9, 0.8), frameon=False)
	ax2.get_legend().remove()
	ax.set(xlabel='', ylabel='', ylim=((0.15, 0.4)), yticks=y1ticks)
	ax2.set(xlabel='', ylabel='', ylim=((8, 14)), yticks=y2ticks)
	ax.set_title("Generosity", pad=20)
	ax2.set_title("Score", pad=20)
	plt.tight_layout()
	sns.despine(top=True, right=True, left=True, bottom=True)
	fig.savefig(f'plots/ScoreGenVsGender.pdf')


	hue = 'learning'
	hue_order = ['slow', 'good', 'fast']
	box_pairs = [
		((order[0], hue_order[0]), (order[0], hue_order[1])),
		((order[0], hue_order[1]), (order[0], hue_order[2])),
		((order[0], hue_order[0]), (order[0], hue_order[2])),
		((order[1], hue_order[0]), (order[1], hue_order[1])),
		((order[1], hue_order[1]), (order[1], hue_order[2])),
		((order[1], hue_order[0]), (order[1], hue_order[2])),
	]
	y1a = np.mean(df.query("group=='greedy' & learning=='slow'")['generosity'])
	y1b = np.mean(df.query("group=='greedy' & learning=='good'")['generosity'])
	y1c = np.mean(df.query("group=='greedy' & learning=='fast'")['generosity'])
	y1d = np.mean(df.query("group=='generous' & learning=='slow'")['generosity'])
	y1e = np.mean(df.query("group=='generous' & learning=='good'")['generosity'])
	y1f = np.mean(df.query("group=='generous' & learning=='fast'")['generosity'])
	y2a = np.mean(df.query("group=='greedy' & learning=='slow'")['reward'])
	y2b = np.mean(df.query("group=='greedy' & learning=='good'")['reward'])
	y2c = np.mean(df.query("group=='greedy' & learning=='fast'")['reward'])
	y2d = np.mean(df.query("group=='generous' & learning=='slow'")['reward'])
	y2e = np.mean(df.query("group=='generous' & learning=='good'")['reward'])
	y2f = np.mean(df.query("group=='generous' & learning=='fast'")['reward'])
	y1ticks = np.around([y1a, y1b, y1c, y1d, y1e, y1f], decimals=2)
	y2ticks = np.around([y2a, y2b, y2c, y2d, y2e, y2f], decimals=1)	
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)))
	sns.barplot(data=df, x=x, y=y1, hue=hue, hue_order=hue_order, ax=ax)
	sns.barplot(data=df, x=x, y=y2, hue=hue, hue_order=hue_order, ax=ax2)
	add_stat_annotation(ax, data=df, x=x, y=y1, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-0.8, line_height=0.01, line_offset=0.02)
	add_stat_annotation(ax2, data=df, x=x, y=y2, hue=hue, hue_order=hue_order, box_pairs=box_pairs,
		test='t-test_ind', text_format='star', loc='inside', line_offset_to_box=-1.25, line_height=0.01, line_offset=-0.02)
	plt.tight_layout()
	ax.legend(loc='upper right', title=hue, bbox_to_anchor=(0.9, 0.8), frameon=False)
	ax2.get_legend().remove()
	ax.set(xlabel='', ylabel='', ylim=((0.15, 0.6)), yticks=y1ticks)
	ax2.set(xlabel='', ylabel='', ylim=((8, 14)), yticks=y2ticks)
	# ax.set_title("Generosity", pad=80)
	# ax2.set_title("Score", pad=80)
	plt.tight_layout()
	sns.despine(top=True, right=True, left=True, bottom=True)
	fig.savefig(f'plots/ScoreGenVsLearning.pdf')

	# low_equal = len(userDf.query('altruism=="low" & objective=="equal"'))
	# low_self = len(userDf.query('altruism=="low" & objective=="self"'))
	# high_equal = len(userDf.query('altruism=="high" & objective=="equal"'))
	# high_self = len(userDf.query('altruism=="high" & objective=="self"'))
	# fig, ax = plt.subplots()
	# sns.barplot(x=['Low, Equal', 'Low, Selfish', 'High, Equal', 'High, Selfish'], y=[low_equal, low_self, high_equal, high_self], ax=ax)
	# ax.set(title="Altruism and Objective")
	# plt.tight_layout()
	# fig.savefig(f'plots/AltruismVsObjective.pdf')

# plotScoreGenVsSurvey()

def plotScatters():
	dfs = []
	columns = ('user', 'group', 'player', 'age', 'score', 'generosity', 'response time')
	for user in User.objects.filter(nGames=REQUIRED):
		for player in ["A", "B"]:
			times = []
			rewards = []
			gens = []
			for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
				for t in range(TURNS):
					time = float(game.userTimes.split(',')[:-1][t])
					give = int(game.userGives.split(',')[:-1][t])
					keep = int(game.userKeeps.split(',')[:-1][t])
					reward = int(game.userRewards.split(',')[:-1][t])
					gen = give/(give+keep) if (give+keep)>0 else -0.1  # visual indicator, rather than lose data
					if 0.1<time<30: times.append(time)  # skip datapoint if time is greater than 30s (AFK)
					rewards.append(reward)
					gens.append(gen)
			dfs.append(pd.DataFrame([[
				user.username, user.group, player, int(user.age), np.mean(rewards), np.mean(gens), np.mean(times),
			]], columns=columns))			
	df = pd.concat([df for df in dfs], ignore_index=True)

	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8,4)))
	sns.regplot(data=df, x='age', y='score', ax=ax)
	sns.regplot(data=df, x='age', y='generosity', ax=ax2)
	plt.tight_layout()
	fig.savefig('plots/ScoreGenVsAge.pdf')

	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8,4)))
	sns.regplot(data=df, x='response time', y='score', ax=ax)
	sns.regplot(data=df, x='response time', y='generosity', ax=ax2)
	plt.tight_layout()
	fig.savefig('plots/ScoreGenVsResponseTime.pdf')

	fig, ((ax2, ax),(ax4,ax3)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((8,4)))
	sns.regplot(data=df.query('player=="A" & group=="greedy"'), x='age', y='score', ax=ax)
	sns.regplot(data=df.query('player=="B" & group=="greedy"'), x='age', y='score', ax=ax2)
	sns.regplot(data=df.query('player=="A" & group=="generous"'), x='age', y='score', ax=ax3)
	sns.regplot(data=df.query('player=="B" & group=="generous"'), x='age', y='score', ax=ax4)
	ax.set(title='Player A, Group Greedy')
	ax2.set(title='Player B, Group Greedy')
	ax3.set(title='Player A, Group Generous')
	ax4.set(title='Player B, Group Generous')
	fig.savefig(f'plots/ScoreVsAge_groups.pdf')

	fig, ((ax2, ax),(ax4,ax3)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((8,4)))
	sns.regplot(data=df.query('player=="A" & group=="greedy"'), x='age', y='generosity', ax=ax)
	sns.regplot(data=df.query('player=="B" & group=="greedy"'), x='age', y='generosity', ax=ax2)
	sns.regplot(data=df.query('player=="A" & group=="generous"'), x='age', y='generosity', ax=ax3)
	sns.regplot(data=df.query('player=="B" & group=="generous"'), x='age', y='generosity', ax=ax4)
	ax.set(title='Player A, Group Greedy', ylim=((-0.1, 1.1)))
	ax2.set(title='Player B, Group Greedy', ylim=((-0.1, 1.1)))
	ax3.set(title='Player A, Group Generous', ylim=((-0.1, 1.1)))
	ax4.set(title='Player B, Group Generous', ylim=((-0.1, 1.1)))
	fig.savefig(f'plots/GenVsAge_groups.pdf')

	fig, ((ax2, ax),(ax4,ax3)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((8,4)))
	sns.regplot(data=df.query('player=="A" & group=="greedy"'), x='response time', y='score', ax=ax)
	sns.regplot(data=df.query('player=="B" & group=="greedy"'), x='response time', y='score', ax=ax2)
	sns.regplot(data=df.query('player=="A" & group=="generous"'), x='response time', y='score', ax=ax3)
	sns.regplot(data=df.query('player=="B" & group=="generous"'), x='response time', y='score', ax=ax4)
	ax.set(title='Player A, Group Greedy')
	ax2.set(title='Player B, Group Greedy')
	ax3.set(title='Player A, Group Generous')
	ax4.set(title='Player B, Group Generous')
	fig.savefig(f'plots/ScoreVsResponseTime_groups.pdf')

	fig, ((ax2, ax),(ax4,ax3)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((8,4)))
	sns.regplot(data=df.query('player=="A" & group=="greedy"'), x='response time', y='generosity', ax=ax)
	sns.regplot(data=df.query('player=="B" & group=="greedy"'), x='response time', y='generosity', ax=ax2)
	sns.regplot(data=df.query('player=="A" & group=="generous"'), x='response time', y='generosity', ax=ax3)
	sns.regplot(data=df.query('player=="B" & group=="generous"'), x='response time', y='generosity', ax=ax4)
	ax.set(title='Player A, Group Greedy', ylim=((-0.1, 1.1)))
	ax2.set(title='Player B, Group Greedy', ylim=((-0.1, 1.1)))
	ax3.set(title='Player A, Group Generous', ylim=((-0.1, 1.1)))
	ax4.set(title='Player B, Group Generous', ylim=((-0.1, 1.1)))
	fig.savefig(f'plots/GenVsResponseTime_groups.pdf')

# plotScatters()

def plotScoreGenLine(load=True, first_last_games=3):
	if not load:
		dfs = []
		columns = ('user', 'group', 'player', 'fourgroup', 'game', 'turn', 'score', 'generosity')
		for user in User.objects.filter(nGames=REQUIRED):
			username = user.username
			group = user.group
			for player in ["A", "B"]:
				if group=='greedy' and player=='A': fourgroup = "Investor\nGreedy"
				if group=='greedy' and player=='B': fourgroup = "Trustee\nGreedy"
				if group=='generous' and player=='A': fourgroup = "Investor\nGenerous"
				if group=='generous' and player=='B': fourgroup = "Trustee\nGenerous"
				for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
					for t in range(TURNS):
						give = int(game.userGives.split(',')[:-1][t])
						keep = int(game.userKeeps.split(',')[:-1][t])
						score = int(game.userRewards.split(',')[:-1][t])
						gen = give/(give+keep) if (give+keep)>0 else -0.1  # visual indicator, rather than lose data
						dfs.append(pd.DataFrame([[
							username, group, player, fourgroup, g+1, t, score, gen
						]], columns=columns))
		df = pd.concat([df for df in dfs], ignore_index=True)
		df.to_pickle("plots/plotScoreGenLine.pkl")
	else:
		df = pd.read_pickle("plots/plotScoreGenLine.pkl")

	first_games = first_last_games
	last_games = int(REQUIRED/2)-first_last_games
	fourgroups = ["Investor\nGreedy", "Investor\nGenerous", "Trustee\nGreedy", "Trustee\nGenerous"]
	fourlabels = ["Investor, Greedy", "Investor, Generous", "Trustee, Greedy", "Trustee, Generous"]
	fournames = ["InvestorGreedy", "InvestorGenerous", "TrusteeGreedy", "TrusteeGenerous"]
	yLimsGen = [((0, 0.5)), ((0.3, 0.6)), ((0, 0.5)), ((0.2, 0.4))]
	yLimsScore = [((7, 10)), ((10, 12)), ((12, 20)), ((7, 11))]

	fig, axes = plt.subplots(nrows=4, ncols=2, figsize=((6.5, 4)), sharex=True)
	for i, fourgroup in enumerate(fourgroups):
		data = df.query("fourgroup==@fourgroup")
		score1 = np.array(data.query('game<=@first_games')['score'])
		gen1 = np.array(data.query('game<=@first_games')['generosity'])
		score2 = np.array(data.query('game>@last_games')['score'])
		gen2 = np.array(data.query('game>@last_games')['generosity'])
		Tval_score, pval_score = ttest_ind(score1, score2, equal_var=False)
		Tval_gen, pval_gen = ttest_ind(gen1, gen2, equal_var=False)
		print(f"{fourlabels[i]}, Learning Welsh T test: SCORE p={pval_score:.5f}")
		print(f"{fourlabels[i]}, Learning Welsh T test: GEN p={pval_gen:.5f}")
		sns.lineplot(data=data, x='game', y='generosity', ax=axes[i][0])
		sns.lineplot(data=data, x='game', y='score', ax=axes[i][1])
		axes[i][0].set(xticks=((1, 15)), ylim=yLimsGen[i], yticks=yLimsGen[i], ylabel='', xlabel='')
		axes[i][1].set(xticks=((1, 15)), ylim=yLimsScore[i], yticks=yLimsScore[i], ylabel='', xlabel='')
		axes[i][0].legend(handles=[], title=f"{fourlabels[i]}", loc="upper center", frameon=False)
		axes[i][1].legend(handles=[], title=f"{fourlabels[i]}", loc="upper center", frameon=False)	
	axes[0][0].set(title='Generosity')
	axes[0][1].set(title='Score')
	axes[3][0].set(xlabel='Game')
	axes[3][1].set(xlabel='Game')
	plt.tight_layout()
	fig.savefig(f'plots/ScoreGenLine_Human.pdf')
	fig.savefig(f'plots/ScoreGenLine_Human.svg')

# plotScoreGenLine()
# raise

def plotScoreGenDistribution(load=True, speed_thr=4, exploration_thr=2.0, first_last_games=3):
	first_games = first_last_games
	last_games = int(REQUIRED/2)-first_last_games
	first_turns = first_games*TURNS
	last_turns = last_games*TURNS
	players = ["A", "B"]
	fourgroups = ["Investor\nGreedy", "Investor\nGenerous", "Trustee\nGreedy", "Trustee\nGenerous"]
	fourlabels = ["Investor, Greedy", "Investor, Generous", "Trustee, Greedy", "Trustee, Generous"]
	fournames = ["InvestorGreedy", "InvestorGenerous", "TrusteeGreedy", "TrusteeGenerous"]
	four1 = fourgroups[0]
	four2 = fourgroups[1]
	four3 = fourgroups[2]
	four4 = fourgroups[3]

	if load:
		df = pd.read_pickle("plots/plotScoreGenDistribution.pkl")
	else:
		# collect average data about the user
		dfsUser = []
		columns = ('user', 'group', 'player', 'orientation', 'speed', 'exploration', 'opponent')
		for user in User.objects.filter(nGames=REQUIRED):
			opponent = "computer" if user.otherIdentity == "computer" else "human" if (user.otherIdentity=="human" or user.otherIdentity=="mix") else "n/a"
			orientation = "self" if user.objective == "self" else "social" if user.objective=="equal" else "n/a"
			if orientation=="n/a" or opponent=="n/a":
				continue  # don't add to dataset unless they answered all questions 
			for player in players:
				times = []
				gens = []
				rewards = []
				for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
					for t in range(TURNS):
						time = float(game.userTimes.split(',')[:-1][t])
						give = int(game.userGives.split(',')[:-1][t])
						keep = int(game.userKeeps.split(',')[:-1][t])
						reward = int(game.userRewards.split(',')[:-1][t])
						gen = 0 if give+keep==0 else give/(give+keep)
						# gen = give/(give+keep) if (give+keep)>0 else -0.1  # visual indicator, rather than lose data
						times.append(np.clip(time, 0.1, 30))  # clip turn times to max 30s (for AFK players)
						rewards.append(reward)
						gens.append(gen)
				# speed = 'fast' if np.median(times) < speed_thr else 'slow'					
				speed = 'fast' if np.mean(times) < speed_thr else 'slow'
				# exploration = 'low' if np.std(gens[:first_turns]) < exploration_thr else 'high'
				exploration = 'low' if entropy(gens[:first_turns]) < exploration_thr else 'high'
				# print(gens[:first_turns], entropy(gens[:first_turns]))
				dfsUser.append(pd.DataFrame([[user.username, user.group, player, orientation, speed, exploration, opponent]], columns=columns))			
		dfUser = pd.concat([df for df in dfsUser], ignore_index=True)
		# create the main dataframe (per-turn score/gen info), appending user data
		dfs = []
		columns = ('user', 'group', 'player',  'fourgroup', # game attr
			'game', 'turn', 'score', 'generosity',  # move attr
			'orientation', 'speed', 'exploration', 'opponent')  # user attr
		for user in User.objects.filter(nGames=REQUIRED):
			username = user.username
			group = user.group
			if not np.any(dfUser['user'].str.contains(username)):
				continue
			for player in players:
				userDF = dfUser.query("user==@username & group==@group & player==@player")
				orientation = userDF['orientation'].values[0]
				speed = userDF['speed'].values[0]
				exploration = userDF['exploration'].values[0]
				opponent = userDF['opponent'].values[0]
				if group=='greedy' and player=='A': fourgroup = "Investor\nGreedy"
				if group=='greedy' and player=='B': fourgroup = "Trustee\nGreedy"
				if group=='generous' and player=='A': fourgroup = "Investor\nGenerous"
				if group=='generous' and player=='B': fourgroup = "Trustee\nGenerous"
				for g, game in enumerate(Game.objects.filter(complete=True, user=user, userRole=player).order_by('tStart')):
					for t in range(TURNS):
						give = int(game.userGives.split(',')[:-1][t])
						keep = int(game.userKeeps.split(',')[:-1][t])
						score = int(game.userRewards.split(',')[:-1][t])
						gen = 0 if give+keep==0 else give/(give+keep)
						dfs.append(pd.DataFrame([[
							username, group, player, fourgroup,
							g+1, t, score, gen,
							orientation, speed, exploration, opponent,
						]], columns=columns))
		df = pd.concat([df for df in dfs], ignore_index=True)
		df.to_pickle("plots/plotScoreGenDistribution.pkl")
	dfLast = df.query('game>@last_games')


	# print("ALL")
	# yLimsGen = [((-0.1, 1.1)), ((-0.1, 1.1)), ((-0.1, 0.6)), ((-0.1, 0.6))]
	# yTicksGen = [((0, 1)), ((0, 1)), ((0, 0.6)), ((0, 0.6))]
	# yLimsScore = [((2, 11)), ((6, 16)), ((10, 30)), ((-1.5, 24))]
	# yTicksScore = [((2, 11)), ((6, 16)), ((10, 30)), ((0, 24))]
	# xticks = ((1, first_games, last_games+1, 15))
	# fig, axes = plt.subplots(nrows=4, ncols=2, figsize=((6.5, 8)), sharex=True)
	# for i, fourgroup in enumerate(fourgroups):
	# 	data = df.query("fourgroup==@fourgroup")
	# 	score1 = np.array(data.query('game<=@first_games')['score'])
	# 	gen1 = np.array(data.query('game<=@first_games')['generosity'])
	# 	score2 = np.array(data.query('game>@last_games')['score'])
	# 	gen2 = np.array(data.query('game>@last_games')['generosity'])
	# 	ksval_score, pval_score = ks_2samp(score1, score2)
	# 	ksval_gen, pval_gen = ks_2samp(gen1, gen2)
	# 	print(f"{fourlabels[i]}, Learning KS test: SCORE p={pval_score:.5f}")
	# 	print(f"{fourlabels[i]}, Learning KS test: GEN p={pval_gen:.5f}")
	# 	sns.kdeplot(data=data, x='game', y='generosity', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=axes[i][0])
	# 	sns.kdeplot(data=data, x='game', y='score', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=axes[i][1])
	# 	axes[i][0].axvspan(1, first_games, color='gray', alpha=0.3)
	# 	axes[i][1].axvspan(1, first_games, color='gray', alpha=0.3)
	# 	axes[i][0].axvspan(last_games+1, 15, color='gray', alpha=0.3)
	# 	axes[i][1].axvspan(last_games+1, 15, color='gray', alpha=0.3)
	# 	axes[i][0].set(xticks=xticks, ylim=yLimsGen[i], yticks=yTicksGen[i], ylabel='', xlabel='')
	# 	axes[i][1].set(xticks=xticks, ylim=yLimsScore[i], yticks=yTicksScore[i], ylabel='', xlabel='')
	# 	axes[i][0].legend(handles=[], title=f"{fourlabels[i]}", loc="upper center", frameon=False)
	# 	axes[i][1].legend(handles=[], title=f"{fourlabels[i]}", loc="upper center", frameon=False)	
	# axes[0][0].set(title='Generosity')
	# axes[0][1].set(title='Score')
	# axes[3][0].set(xlabel='Game')
	# axes[3][1].set(xlabel='Game')
	# plt.tight_layout()
	# fig.savefig(f'plots/ScoreGenDistribution_Human.pdf')
	# fig.savefig(f'plots/ScoreGenDistribution_Human.svg')

	print("ORIENTATION")
	independent = ['self', 'social']
	ind_label = ["Self-Oriented", "Socially-Oriented"]
	ind0, ind1 = independent[0], independent[1]
	slf, social = "self", "social"
	box_pairs = [
		((four1, ind0), (four1, ind1)),
		((four2, ind0), (four2, ind1)),
		((four3, ind0), (four3, ind1)),
		((four4, ind0), (four4, ind1)),
		]

	yLimsGen = [((-0.1, 1.1)), ((-0.1, 1.1)), ((-0.1, 0.6)), ((-0.1, 0.6))]
	yTicksGen = [((0, 1)), ((0, 1)), ((0, 0.6)), ((0, 0.6))]
	yLimsScore = [((2, 11)), ((6, 16)), ((10, 30)), ((-1.5, 24))]
	yTicksScore = [((2, 11)), ((6, 16)), ((10, 30)), ((0, 24))]
	for i, fourgroup in enumerate(fourgroups):
		data = df.query("fourgroup==@fourgroup")
		print(f'{fourlabels[i]}, orientation self {len(data.query("orientation==@slf"))}, social {len(data.query("orientation==@social"))}')
		score1 = np.array(data.query('orientation==@ind0 & game<=@first_games')['score'])
		gen1 = np.array(data.query('orientation==@ind0 & game<=@first_games')['generosity'])
		score2 = np.array(data.query('orientation==@ind1 & game<=@first_games')['score'])
		gen2 = np.array(data.query('orientation==@ind1 & game<=@first_games')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"initial distribution KS test: SCORE p={pval_score:.5f}, GEN p={pval_gen:.5f}")
		score1 = np.array(data.query('orientation==@ind0 & game>@last_games')['score'])
		gen1 = np.array(data.query('orientation==@ind0 & game>@last_games')['generosity'])
		score2 = np.array(data.query('orientation==@ind1 & game>@last_games')['score'])
		gen2 = np.array(data.query('orientation==@ind1 & game>@last_games')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"final distribution KS test: SCORE p={pval_score:.5f}, GEN p={pval_gen:.5f}")
		score1 = np.array(data.query('orientation==@ind0')['score'])
		gen1 = np.array(data.query('orientation==@ind0')['generosity'])
		score2 = np.array(data.query('orientation==@ind1')['score'])
		gen2 = np.array(data.query('orientation==@ind1')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"overall distribution KS test: SCORE p={pval_score:.5f}, GEN p={pval_gen:.5f}")
		fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((6.5, 4)), sharex=True)
		sns.kdeplot(data=data.query("orientation==@ind0"), x='game', y='generosity', color=palette[0], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax)
		sns.kdeplot(data=data.query("orientation==@ind0"), x='game', y='score', color=palette[0], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax2)
		sns.kdeplot(data=data.query("orientation==@ind1"), x='game', y='generosity', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax3)
		sns.kdeplot(data=data.query("orientation==@ind1"), x='game', y='score', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax4)
		ax.axvspan(last_games+1, 15, color='gray', alpha=0.3)
		ax2.axvspan(last_games+1, 15, color='gray', alpha=0.3)
		ax3.axvspan(last_games+1, 15, color='gray', alpha=0.3)
		ax4.axvspan(last_games+1, 15, color='gray', alpha=0.3)
		ax.set(ylim=yLimsGen[i], yticks=yTicksGen[i], ylabel='', title='Generosity')
		ax2.set(ylim=yLimsScore[i], yticks=yTicksScore[i], ylabel='', title='Score')
		ax3.set(ylim=yLimsGen[i], yticks=yTicksGen[i], xticks=((last_games+1, 15)), xlabel='Game', ylabel='')
		ax4.set(ylim=yLimsScore[i], yticks=yTicksScore[i], xticks=((last_games+1, 15)), xlabel='Game', ylabel='')
		ax.legend(handles=[], title=f"{fourlabels[i]}, {ind_label[0]}", loc="upper center", frameon=False)
		ax2.legend(handles=[], title=f"{fourlabels[i]}, {ind_label[0]}", loc="upper center", frameon=False)
		ax3.legend(handles=[], title=f"{fourlabels[i]}, {ind_label[1]}", loc="upper center", frameon=False)
		ax4.legend(handles=[], title=f"{fourlabels[i]}, {ind_label[1]}", loc="upper center", frameon=False)
		plt.tight_layout()
		fig.savefig(f'plots/ScoreGenDistribution_Human_Orientation_{fournames[i]}.pdf')
		fig.savefig(f'plots/ScoreGenDistribution_Human_Orientation_{fournames[i]}.svg')

	# y1s = [
	# 	np.mean(dfLast.query("fourgroup==@four1 & orientation==@ind0")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four1 & orientation==@ind1")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four2 & orientation==@ind0")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four2 & orientation==@ind1")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four3 & orientation==@ind0")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four3 & orientation==@ind1")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four4 & orientation==@ind0")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four4 & orientation==@ind1")['generosity']),
	# 	]
	# y2s = [
	# 	np.mean(dfLast.query("fourgroup==@four1 & orientation==@ind0")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four1 & orientation==@ind1")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four2 & orientation==@ind0")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four2 & orientation==@ind1")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four3 & orientation==@ind0")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four3 & orientation==@ind1")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four4 & orientation==@ind0")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four4 & orientation==@ind1")['score']),
	# 	]
	# for i, fourgroup in enumerate(fourgroups):
	# 	data = dfLast.query("fourgroup==@fourgroup")
	# 	score1 = np.array(data.query('orientation==@ind0')['score'])
	# 	gen1 = np.array(data.query('orientation==@ind0')['generosity'])
	# 	score2 = np.array(data.query('orientation==@ind1')['score'])
	# 	gen2 = np.array(data.query('orientation==@ind1')['generosity'])
	# 	Tval_score, pval_score = ttest_ind(score1, score2, equal_var=False)
	# 	Tval_gen, pval_gen = ttest_ind(gen1, gen2, equal_var=False)
	# 	print(f"{fourlabels[i]}, Orientation Welsh T test: SCORE p={pval_score:.5f}")
	# 	print(f"{fourlabels[i]}, Orientation Welsh T test: GEN p={pval_gen:.5f}")
	# fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((6.5, 2)), sharex=True)
	# sns.barplot(data=dfLast, x='fourgroup', y='generosity', order=fourgroups, hue='orientation', hue_order=independent, ax=ax)
	# sns.barplot(data=dfLast, x='fourgroup', y='score', order=fourgroups, hue='orientation', hue_order=independent, ax=ax2)
	# add_stat_annotation(ax, data=dfLast, x='fourgroup', y='generosity', order=fourgroups, hue='orientation', hue_order=independent,
	# 	box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside', verbose=0, pvalue_thresholds=pvalue_thresholds)
	# add_stat_annotation(ax2, data=dfLast, x='fourgroup', y='score', order=fourgroups, hue='orientation', hue_order=independent,
	# 	box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside', verbose=0, pvalue_thresholds=pvalue_thresholds)
	# for i, v in enumerate(y1s):
	# 	plt.text(x=i/3, y=10*v, s=f"{v:.2f}", fontsize=8)
	# for i, v in enumerate(y2s):
	# 	plt.text(x=i/3, y=5+v/2, s=f"{v:.2f}", fontsize=8)
	# ax.set(xlabel='', ylabel='', title='Generosity', yticks=(()))
	# ax2.set(xlabel='', ylabel='', title='Score', yticks=(()))
	# ax2.get_legend().remove()
	# sns.despine(ax=ax, left=True, right=True, top=True)
	# sns.despine(ax=ax2, left=True, right=True, top=True)
	# plt.tight_layout()
	# fig.savefig(f'plots/ScoreGenBarplot_Human_Orientation.pdf')
	# fig.savefig(f'plots/ScoreGenBarplot_Human_Orientation.svg')


	# print("EXPLORATION")
	# independent = ['low', 'high']
	# ind_label = ["Low Exploration", "High Exploration"]
	# ind0, ind1 = independent[0], independent[1]
	# low, high = 'low', 'high'
	# box_pairs = [
	# 	((four1, ind0), (four1, ind1)),
	# 	((four2, ind0), (four2, ind1)),
	# 	((four3, ind0), (four3, ind1)),
	# 	((four4, ind0), (four4, ind1)),
	# 	]

	# yLimsGen = [((-0.1, 1.1)), ((-0.1, 1.1)), ((-0.1, 0.6)), ((-0.1, 0.6))]
	# yTicksGen = [((0, 1)), ((0, 1)), ((0, 0.6)), ((0, 0.6))]
	# yLimsScore = [((2, 11)), ((6, 16)), ((10, 30)), ((-1.5, 24))]
	# yTicksScore = [((2, 11)), ((6, 16)), ((10, 30)), ((0, 24))]
	# for i, fourgroup in enumerate(fourgroups):
	# 	data = df.query("fourgroup==@fourgroup")
	# 	print(f'{fourlabels[i]}, exploration low {len(data.query("exploration==@low"))}, high {len(data.query("exploration==@high"))}')
	# 	score1 = np.array(data.query('exploration==@ind0 & game<=@first_games')['score'])
	# 	gen1 = np.array(data.query('exploration==@ind0 & game<=@first_games')['generosity'])
	# 	score2 = np.array(data.query('exploration==@ind1 & game<=@first_games')['score'])
	# 	gen2 = np.array(data.query('exploration==@ind1 & game<=@first_games')['generosity'])
	# 	ksval_score, pval_score = ks_2samp(score1, score2)
	# 	ksval_gen, pval_gen = ks_2samp(gen1, gen2)
	# 	print(f"initial distribution KS test: SCORE p={pval_score:.5f}, GEN p={pval_gen:.5f}")
	# 	score1 = np.array(data.query('exploration==@ind0 & game>@last_games')['score'])
	# 	gen1 = np.array(data.query('exploration==@ind0 & game>@last_games')['generosity'])
	# 	score2 = np.array(data.query('exploration==@ind1 & game>@last_games')['score'])
	# 	gen2 = np.array(data.query('exploration==@ind1 & game>@last_games')['generosity'])
	# 	ksval_score, pval_score = ks_2samp(score1, score2)
	# 	ksval_gen, pval_gen = ks_2samp(gen1, gen2)
	# 	print(f"final distribution KS test: SCORE p={pval_score:.5f}, GEN p={pval_gen:.5f}")
	# 	score1 = np.array(data.query('exploration==@ind0')['score'])
	# 	gen1 = np.array(data.query('exploration==@ind0')['generosity'])
	# 	score2 = np.array(data.query('exploration==@ind1')['score'])
	# 	gen2 = np.array(data.query('exploration==@ind1')['generosity'])
	# 	ksval_score, pval_score = ks_2samp(score1, score2)
	# 	ksval_gen, pval_gen = ks_2samp(gen1, gen2)
	# 	print(f"overall distribution KS test: SCORE p={pval_score:.5f}, GEN p={pval_gen:.5f}")
	# 	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((6.5, 4)), sharex=True)
	# 	sns.kdeplot(data=data.query("exploration==@ind0"), x='game', y='generosity', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax)
	# 	sns.kdeplot(data=data.query("exploration==@ind0"), x='game', y='score', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax2)
	# 	sns.kdeplot(data=data.query("exploration==@ind1"), x='game', y='generosity', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax3)
	# 	sns.kdeplot(data=data.query("exploration==@ind1"), x='game', y='score', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax4)
	# 	ax.set(ylim=yLimsGen[i], yticks=yTicksGen[i], ylabel='', title='Generosity')
	# 	ax2.set(ylim=yLimsScore[i], yticks=yTicksScore[i], ylabel='', title='Score')
	# 	ax3.set(ylim=yLimsGen[i], yticks=yTicksGen[i], xticks=((1, 15)), xlabel='Game', ylabel='')
	# 	ax4.set(ylim=yLimsScore[i], yticks=yTicksScore[i], xticks=((1, 15)), xlabel='Game', ylabel='')
	# 	ax.legend(handles=[], title=f"{fourlabels[i]}, {ind_label[0]}", loc="upper center", frameon=False)
	# 	ax2.legend(handles=[], title=f"{fourlabels[i]}, {ind_label[0]}", loc="upper center", frameon=False)
	# 	ax3.legend(handles=[], title=f"{fourlabels[i]}, {ind_label[1]}", loc="upper center", frameon=False)
	# 	ax4.legend(handles=[], title=f"{fourlabels[i]}, {ind_label[1]}", loc="upper center", frameon=False)
	# 	plt.tight_layout()
	# 	fig.savefig(f'plots/ScoreGenDistribution_Human_Exploration_{fournames[i]}.pdf')
	# 	fig.savefig(f'plots/ScoreGenDistribution_Human_Exploration_{fournames[i]}.svg')


	# y1s = [
	# 	np.mean(dfLast.query("fourgroup==@four1 & exploration==@ind0")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four1 & exploration==@ind1")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four2 & exploration==@ind0")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four2 & exploration==@ind1")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four3 & exploration==@ind0")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four3 & exploration==@ind1")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four4 & exploration==@ind0")['generosity']),
	# 	np.mean(dfLast.query("fourgroup==@four4 & exploration==@ind1")['generosity']),
	# 	]
	# y2s = [
	# 	np.mean(dfLast.query("fourgroup==@four1 & exploration==@ind0")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four1 & exploration==@ind1")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four2 & exploration==@ind0")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four2 & exploration==@ind1")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four3 & exploration==@ind0")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four3 & exploration==@ind1")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four4 & exploration==@ind0")['score']),
	# 	np.mean(dfLast.query("fourgroup==@four4 & exploration==@ind1")['score']),
	# 	]
	# for i, fourgroup in enumerate(fourgroups):
	# 	data = dfLast.query("fourgroup==@fourgroup")
	# 	score1 = np.array(data.query('exploration==@ind0')['score'])
	# 	gen1 = np.array(data.query('exploration==@ind0')['generosity'])
	# 	score2 = np.array(data.query('exploration==@ind1')['score'])
	# 	gen2 = np.array(data.query('exploration==@ind1')['generosity'])
	# 	Tval_score, pval_score = ttest_ind(score1, score2, equal_var=False)
	# 	Tval_gen, pval_gen = ttest_ind(gen1, gen2, equal_var=False)
	# 	print(f"{fourlabels[i]}, Exploration Welsh T test: SCORE p={pval_score:.5f}")
	# 	print(f"{fourlabels[i]}, Exploration Welsh T test: GEN p={pval_gen:.5f}")
	# fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((6.5, 2)), sharex=True)
	# sns.barplot(data=dfLast, x='fourgroup', y='generosity', order=fourgroups, hue='exploration', hue_order=independent, ax=ax)
	# sns.barplot(data=dfLast, x='fourgroup', y='score', order=fourgroups, hue='exploration', hue_order=independent, ax=ax2)
	# add_stat_annotation(ax, data=dfLast, x='fourgroup', y='generosity', order=fourgroups, hue='exploration', hue_order=independent,
	# 	box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside', verbose=0, pvalue_thresholds=pvalue_thresholds)
	# add_stat_annotation(ax2, data=dfLast, x='fourgroup', y='score', order=fourgroups, hue='exploration', hue_order=independent,
	# 	box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside', verbose=0, pvalue_thresholds=pvalue_thresholds)
	# for i, v in enumerate(y1s):
	# 	plt.text(x=i/3, y=10*v, s=f"{v:.2f}", fontsize=8)
	# for i, v in enumerate(y2s):
	# 	plt.text(x=i/3, y=5+v/2, s=f"{v:.2f}", fontsize=8)
	# ax.set(xlabel='', ylabel='', title='Generosity', yticks=(()))
	# ax2.set(xlabel='', ylabel='', title='Score', yticks=(()))
	# ax2.get_legend().remove()
	# sns.despine(ax=ax, left=True, right=True, top=True)
	# sns.despine(ax=ax2, left=True, right=True, top=True)
	# plt.tight_layout()
	# fig.savefig(f'plots/ScoreGenBarplot_Human_Exploration.pdf')
	# fig.savefig(f'plots/ScoreGenBarplot_Human_Exploration.svg')


	# print("SPEED")
	# independent = ['fast', 'slow']
	# ind_label = ["Fast Speed", "Slow Speed"]
	# ind0, ind1 = independent[0], independent[1]
	# box_pairs = [
	# 	((four1, ind0), (four1, ind1)),
	# 	((four2, ind0), (four2, ind1)),
	# 	((four3, ind0), (four3, ind1)),
	# 	((four4, ind0), (four4, ind1)),
	# 	]

	# for i, fourgroup in enumerate(fourgroups):
	# 	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
	# 	data = df.query("fourgroup==@fourgroup")
	# 	score1 = np.array(data.query('speed==@ind0 & game<=@first_games')['score'])
	# 	gen1 = np.array(data.query('speed==@ind0 & game<=@first_games')['generosity'])
	# 	score2 = np.array(data.query('speed==@ind1 & game<=@first_games')['score'])
	# 	gen2 = np.array(data.query('speed==@ind1 & game<=@first_games')['generosity'])
	# 	ksval_score, pval_score = ks_2samp(score1, score2)
	# 	ksval_gen, pval_gen = ks_2samp(gen1, gen2)
	# 	print(f"initial distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
	# 	score1 = np.array(data.query('speed==@ind0 & game>=@last_turns')['score'])
	# 	gen1 = np.array(data.query('speed==@ind0 & game>=@last_turns')['generosity'])
	# 	score2 = np.array(data.query('speed==@ind1 & game>=@last_turns')['score'])
	# 	gen2 = np.array(data.query('speed==@ind1 & game>=@last_turns')['generosity'])
	# 	ksval_score, pval_score = ks_2samp(score1, score2)
	# 	ksval_gen, pval_gen = ks_2samp(gen1, gen2)
	# 	print(f"final distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
	# 	score1 = np.array(data.query('speed==@ind0')['score'])
	# 	gen1 = np.array(data.query('speed==@ind0')['generosity'])
	# 	score2 = np.array(data.query('speed==@ind1')['score'])
	# 	gen2 = np.array(data.query('speed==@ind1')['generosity'])
	# 	ksval_score, pval_score = ks_2samp(score1, score2)
	# 	ksval_gen, pval_gen = ks_2samp(gen1, gen2)
	# 	print(f"overall distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
	# 	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
	# 	sns.kdeplot(data=data.query("speed==@ind0"), x='game', y='generosity', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax)
	# 	sns.kdeplot(data=data.query("speed==@ind0"), x='game', y='score', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax2)
	# 	sns.kdeplot(data=data.query("speed==@ind1"), x='game', y='generosity', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax3)
	# 	sns.kdeplot(data=data.query("speed==@ind1"), x='game', y='score', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax4)
	# 	ax.set(ylim=((-0.1, 1.1)), yticks=((0, 1)))
	# 	ax2.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score')
	# 	ax3.set(ylim=((-0.1, 1.1)), yticks=((0, 1)), xticks=((0, 14)))
	# 	ax4.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score', xticks=((0, 14)))
	# 	ax.legend((f"{fourlabels[i]}, {ind_label[0]}",), loc="upper right", frameon=False)
	# 	ax2.legend((f"{fourlabels[i]}, {ind_label[0]}",), loc="upper right", frameon=False)
	# 	ax3.legend((f"{fourlabels[i]}, {ind_label[1]}",), loc="upper right", frameon=False)
	# 	ax4.legend((f"{fourlabels[i]}, {ind_label[1]}",), loc="upper right", frameon=False)
	# 	plt.tight_layout()
	# 	fig.savefig(f'plots/ScoreGenDistribution_Human_{fournames[i]}_Speed.pdf')
	# 	fig.savefig(f'plots/ScoreGenDistribution_Human_{fournames[i]}_Speed.svg')

	# y1s = [
	# 	np.mean(df.query("fourgroup==@four1 & speed==@ind0")['generosity']),
	# 	np.mean(df.query("fourgroup==@four1 & speed==@ind1")['generosity']),
	# 	np.mean(df.query("fourgroup==@four2 & speed==@ind0")['generosity']),
	# 	np.mean(df.query("fourgroup==@four2 & speed==@ind1")['generosity']),
	# 	np.mean(df.query("fourgroup==@four3 & speed==@ind0")['generosity']),
	# 	np.mean(df.query("fourgroup==@four3 & speed==@ind1")['generosity']),
	# 	np.mean(df.query("fourgroup==@four4 & speed==@ind0")['generosity']),
	# 	np.mean(df.query("fourgroup==@four4 & speed==@ind1")['generosity']),
	# 	]
	# y2s = [
	# 	np.mean(df.query("fourgroup==@four1 & speed==@ind0")['score']),
	# 	np.mean(df.query("fourgroup==@four1 & speed==@ind1")['score']),
	# 	np.mean(df.query("fourgroup==@four2 & speed==@ind0")['score']),
	# 	np.mean(df.query("fourgroup==@four2 & speed==@ind1")['score']),
	# 	np.mean(df.query("fourgroup==@four3 & speed==@ind0")['score']),
	# 	np.mean(df.query("fourgroup==@four3 & speed==@ind1")['score']),
	# 	np.mean(df.query("fourgroup==@four4 & speed==@ind0")['score']),
	# 	np.mean(df.query("fourgroup==@four4 & speed==@ind1")['score']),
	# 	]
	# fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)), sharex=True)
	# sns.barplot(data=df, x='fourgroup', y=y1, order=fourgroups, hue='speed', hue_order=independent, ax=ax)
	# sns.barplot(data=df, x='fourgroup', y=y2, order=fourgroups, hue='speed', hue_order=independent, ax=ax2)
	# add_stat_annotation(ax, data=df, x='fourgroup', y=y1, order=fourgroups, hue='speed', hue_order=independent, box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside')
	# add_stat_annotation(ax2, data=df, x='fourgroup', y=y2, order=fourgroups, hue='speed', hue_order=independent, box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside')
	# for i, v in enumerate(y1s):
	# 	plt.text(x=i/3, y=10*v, s=f"{v:.2f}")
	# for i, v in enumerate(y2s):
	# 	plt.text(x=i/3, y=5+v/2, s=f"{v:.2f}")
	# ax.set(xlabel='', ylabel='Generosity', yticks=(()))
	# ax2.set(xlabel='', ylabel='Score', yticks=(()))
	# ax2.get_legend().remove()
	# plt.tight_layout()
	# fig.savefig(f'plots/ScoreGenBarplot_Speed.pdf')
	# fig.savefig(f'plots/ScoreGenBarplot_Speed.svg')

plotScoreGenDistribution()