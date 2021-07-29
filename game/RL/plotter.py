import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import time
from scipy.special import softmax
from scipy.spatial.distance import jensenshannon
from scipy.ndimage import histogram, gaussian_filter1d
from scipy.stats import ttest_ind, entropy, ks_2samp
from statannot import add_stat_annotation
from matplotlib.lines import Line2D
sns.set_context(rc = {'patch.linewidth': 0})
palette = sns.color_palette('deep')
sns.set(context='paper', style='white', font='CMU Serif',
    rc={'font.size':10, 'mathtext.fontset': 'cm', 'axes.labelpad':0, 'axes.linewidth': 0.5, 'axes.titlepad': 20, 'axes.titlesize': 14})
pvalue_thresholds = [[1e-3, "***"], [1e-2, "**"], [1e-1, "*"], [1e0, "ns"]]

def plotAll(dfAll, popA, popB, capital, match, rounds, turns, name, endgames=5):
	ylim = ((0, capital*match))
	yticks = (([0, 5, 10, 15, 20, 25, 30]))
	binsAG = np.linspace(0, 1, capital+1)
	binsAR = np.arange(0, match*capital+1, 2)
	binsBG = np.linspace(0, 1, capital+1)
	binsBR = np.arange(0, match*capital+1, 2)
	end = rounds - endgames

	for A in popA:
		AID = A.ID
		dfEnd = dfAll.query('game >= @end & A==@AID')

		fig, ax = plt.subplots()
		sns.histplot(data=dfEnd['aGen'], ax=ax, stat="probability", bins=binsAG)  
		ax.set(xlabel="Generosity Ratio", ylabel="Probability", xticks=((binsAG)),
			title=f"{AID} (A) Generosity \nMean={np.mean(dfEnd['aGen']):.2f}, Std={np.std(dfEnd['aGen']):.2f}")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/{name}_{AID}A_generosity.pdf")

		fig, ax = plt.subplots()
		sns.barplot(data=dfEnd, x='turn', y='aGen', ax=ax)  
		ax.set(ylabel="Generosity Ratio", xlabel="Turn", ylim=((0, 1)))
		fig.tight_layout()
		fig.savefig(f"plots/{name}_{AID}A_moves.pdf")

		fig, ax = plt.subplots()
		sns.histplot(data=dfEnd['aScore'], ax=ax, stat="probability", bins=binsAR)  
		ax.set(xlabel="Scores", ylabel="Probability", xticks=((binsAR)),
			title=f"{AID} (A) Scores \nMean={np.mean(dfEnd['aScore']):.2f}, Std={np.std(dfEnd['aScore']):.2f}")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/{name}_{AID}A_scores.pdf")
		plt.close('all')

	for B in popB:
		BID = B.ID
		dfEnd = dfAll.query('game >= @end & B==@BID')

		fig, ax = plt.subplots()
		sns.histplot(data=dfEnd['bGen'], ax=ax, stat="probability", bins=binsBG)  
		ax.set(xlabel="Generosity Ratio", ylabel="Probability", xticks=((binsBG)),
			title=f"{BID} (B) Generosity \nMean={np.mean(dfEnd['bGen']):.2f}, Std={np.std(dfEnd['bGen']):.2f}")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/{name}_{BID}B_generosity.pdf")

		fig, ax = plt.subplots()
		sns.barplot(data=dfEnd, x='turn', y='bGen', ax=ax)  
		ax.set(ylabel="Generosity Ratio", xlabel="Turn", ylim=((0, 1)))
		fig.tight_layout()
		fig.savefig(f"plots/{name}_{BID}B_moves.pdf")

		fig, ax = plt.subplots()
		sns.histplot(data=dfEnd['bScore'], ax=ax, stat="probability", bins=binsBR)  
		ax.set(xlabel="Score", ylabel="Probability", xticks=((binsBR)),
			title=f"{BID} (B) Score \nMean={np.mean(dfEnd['bScore']):.2f}, Std={np.std(dfEnd['bScore']):.2f}")
		ax.grid(True, axis='y')
		fig.tight_layout()
		fig.savefig(f"plots/{name}_{BID}B_scores.pdf")
		plt.close('all')

	# for A in popA:
	# 	for B in popB:
	# 		AID = A.ID
	# 		BID = B.ID
	# 		df = dfAll.query('A==@AID & B==@BID')
	# 		fig, ax = plt.subplots()
	# 		sns.lineplot(data=df, x='game', y='aScore', ax=ax, label=f"A: {AID}", ci="sd")
	# 		sns.lineplot(data=df, x='game', y='bScore', ax=ax, label=f"B: {BID}", ci="sd")
	# 		ax.set(xlabel="Episode", ylabel="Score", ylim=ylim, yticks=yticks, title=f"{AID} (A) vs {BID} (B) Learning")
	# 		ax.grid(True, axis='y')
	# 		leg = ax.legend(loc='upper left')
	# 		fig.tight_layout()
	# 		fig.savefig(f"plots/{name}_{AID}A_{BID}B_learning.pdf")
	# 		plt.close('all')

	fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
	sns.lineplot(data=dfAll, x='game', y='aScore', hue="A", ax=ax, ci="sd")
	sns.lineplot(data=dfAll, x='game', y='bScore', hue="B", ax=ax2, ci="sd")
	ax.set(ylabel="Score (A)", ylim=ylim, yticks=yticks, title=f"Overall Learning")
	ax2.set(xlabel="Episode", ylabel="Score (B)", ylim=ylim, yticks=yticks)
	ax.grid(True, axis='y')
	ax2.grid(True, axis='y')
	leg = ax.legend(loc='upper left')
	leg2 = ax.legend(loc='upper left')
	fig.tight_layout()
	fig.savefig(f"plots/{name}_overall_learning.pdf")


def plotForgiveness(dfAll, popA, popB, capital, match, rounds, endgames=5):
	ylim = ((0, capital*match))
	yticks = (([0, 5, 10, 15, 20, 25, 30]))
	end = rounds-endgames
	df = dfAll.query('game >= @end')
	fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
	sns.lineplot(data=df, x='A', y='aScore', hue="B", ax=ax, ci="sd")
	sns.lineplot(data=df, x='A', y='bScore', hue="B", ax=ax2, ci="sd")
	ax.set(ylabel="Agent Score", ylim=ylim, yticks=yticks, title=f"Final Score vs. T4T Forgiveness")
	ax2.set(xlabel="Forgiveness", ylabel="T4T Score", ylim=ylim, yticks=yticks)
	ax.grid(True, axis='y')
	ax2.grid(True, axis='y')
	leg = ax.legend(loc='upper left')
	leg2 = ax2.legend(loc='upper left')
	fig.tight_layout()
	fig.savefig(f"plots/Forgiveness.pdf")

def plotXFriendliness(df, capital, match, agent, dependent, agent2=None):
	if dependent == "Forgiveness":
		DV = 'F'
		DV2 = 'rO'
	if dependent == "Punishment":
		DV = 'P'
		DV2 = 'rO'
	if dependent == "Magnitude":
		DV = 'M'
		DV2 = 'rO'
	if dependent == "Friendliness":
		DV = "rOA"
		DV2 = 'rOB'
	dfMeanA = df.drop(columns=['meanB', 'stdA', 'stdB']).set_index([DV, DV2])
	dfMeanB = df.drop(columns=['meanA', 'stdA', 'stdB']).set_index([DV, DV2])
	dfStdA = df.drop(columns=['meanA', 'meanB', 'stdB']).set_index([DV, DV2])
	dfStdB = df.drop(columns=['meanA', 'meanB', 'stdA']).set_index([DV, DV2])
	tableMeanA = dfMeanA.unstack(level=0)
	tableMeanB = dfMeanB.unstack(level=0)
	tableStdA = dfStdA.unstack(level=0)
	tableStdB = dfStdB.unstack(level=0)

	xticks = np.array(df.set_index([DV, DV2]).unstack(level=0).index)
	yticks = np.array(df.set_index([DV2, DV]).unstack(level=0).index)
	rx = (xticks[1]-xticks[0])/2
	ry = (yticks[1]-yticks[0])/2
	viridis = plt.get_cmap('viridis', 256)

	# normalize mean and std 0 to 1
	A = np.array(tableMeanA) / (capital*match)
	B = 1 - np.array(tableStdA) / (capital*match/2)
	# convert means to RGB spectrum and set alpha equal to std
	RGBA = viridis(A.T)
	RGBA[...,-1] = B.T
	fig, ax = plt.subplots()
	c = ax.imshow(RGBA,
		vmin=0, vmax=1,
		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
		interpolation='nearest',
		origin='lower',
		cmap='viridis')
	ax.set_aspect('auto')
	plt.colorbar(c)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	posx = np.linspace(start=xticks[0]-rx, stop=xticks[-1]+rx, num=A.shape[0], endpoint=False)
	posy = np.linspace(start=yticks[0]-ry, stop=yticks[-1]+ry, num=A.shape[1], endpoint=False)
	for yi, y in enumerate(posy):
		for xi, x in enumerate(posx):
			label = f"{A.T[yi, xi]:.2f}"
			tx = x + rx
			ty = y + ry
			ax.text(tx, ty, label, color='black', ha='center', va='center')
	if not agent2:
		plt.xlabel(f"{agent} Friendliness")
		plt.ylabel(f"T4T {dependent}")
		plt.title("T4T Score")
		fig.savefig(f"plots/{dependent}Friendliness/{agent}_T4T.pdf")
	else:
		plt.xlabel(f"{agent} Friendliness")
		plt.ylabel(f"{agent2} Friendliness")
		plt.title(f"{agent2} Score")
		fig.savefig(f"plots/FriendlinessFriendliness/{agent}_{agent2}_B.pdf")


	A = np.array(tableMeanB) / (capital*match)
	B = 1 - np.array(tableStdB) / (capital*match/2)
	RGBA = viridis(A.T)
	RGBA[...,-1] = B.T
	fig, ax = plt.subplots()
	c = ax.imshow(RGBA,
		vmin=0, vmax=1,
		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
		interpolation='nearest',
		origin='lower',
		cmap='viridis')
	ax.set_aspect('auto')
	plt.colorbar(c)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	posx = np.linspace(start=xticks[0]-rx, stop=xticks[-1]+rx, num=A.shape[0], endpoint=False)
	posy = np.linspace(start=yticks[0]-ry, stop=yticks[-1]+ry, num=A.shape[1], endpoint=False)
	for yi, y in enumerate(posy):
		for xi, x in enumerate(posx):
			label = f"{A.T[yi, xi]:.2f}"
			tx = x + rx
			ty = y + ry
			ax.text(tx, ty, label, color='black', ha='center', va='center')
	if not agent2:
		plt.xlabel(f"{agent} Friendliness")
		plt.ylabel(f"T4T {dependent}")
		plt.title(f"{agent} Score")
		fig.savefig(f"plots/{dependent}Friendliness/{agent}_agent.pdf")
	else:
		plt.xlabel(f"{agent} Friendliness")
		plt.ylabel(f"{agent2} Friendliness")
		plt.title(f"{agent} Score")
		fig.savefig(f"plots/FriendlinessFriendliness/{agent}_{agent2}_A.pdf")

	A = (np.array(tableMeanA) + np.array(tableMeanB)) / (capital*match)
	B = 1 - (np.array(tableStdA) + np.array(tableStdB)) / (capital*match)
	RGBA = viridis(A.T)
	RGBA[...,-1] = B.T
	fig, ax = plt.subplots()
	c = ax.imshow(RGBA,
		vmin=0, vmax=1,
		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
		interpolation='nearest',
		origin='lower',
		cmap='viridis')
	ax.set_aspect('auto')
	plt.colorbar(c)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	posx = np.linspace(start=xticks[0]-rx, stop=xticks[-1]+rx, num=A.shape[0], endpoint=False)
	posy = np.linspace(start=yticks[0]-ry, stop=yticks[-1]+ry, num=A.shape[1], endpoint=False)
	for yi, y in enumerate(posy):
		for xi, x in enumerate(posx):
			label = f"{A.T[yi, xi]:.2f}"
			tx = x + rx
			ty = y + ry
			ax.text(tx, ty, label, color='black', ha='center', va='center')
	if not agent2:
		plt.xlabel(f"{agent} Friendliness")
		plt.ylabel(f"T4T {dependent}")
		plt.title("Total Score")
		fig.savefig(f"plots/{dependent}Friendliness/{agent}_total.pdf")
	else:
		plt.xlabel(f"{agent} Friendliness")
		plt.ylabel(f"{agent2} Friendliness")
		plt.title(f"Total Score")
		fig.savefig(f"plots/FriendlinessFriendliness/{agent}_{agent2}_total.pdf")

	if agent2:
		A = 1 - np.abs(np.array(tableMeanA) - np.array(tableMeanB)) / (capital*match)
		RGBA = viridis(A.T)
		fig, ax = plt.subplots()
		c = ax.imshow(RGBA,
			vmin=0, vmax=1,
			extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
			interpolation='nearest',
			origin='lower',
			cmap='viridis')
		ax.set_aspect('auto')
		plt.colorbar(c)
		ax.set_xticks(xticks)
		ax.set_yticks(yticks)
		posx = np.linspace(start=xticks[0]-rx, stop=xticks[-1]+rx, num=A.shape[0], endpoint=False)
		posy = np.linspace(start=yticks[0]-ry, stop=yticks[-1]+ry, num=A.shape[1], endpoint=False)
		for yi, y in enumerate(posy):
			for xi, x in enumerate(posx):
				label = f"{A.T[yi, xi]:.2f}"
				tx = x + rx
				ty = y + ry
				ax.text(tx, ty, label, color='black', ha='center', va='center')
		plt.xlabel(f"{agent} Friendliness")
		plt.ylabel(f"{agent2} Friendliness")
		plt.title(f"Cooperation")
		fig.savefig(f"plots/FriendlinessFriendliness/{agent}_{agent2}_cooperation.pdf")

def plotPolicy(file, agent, player, group, nS, nA):
	data = np.load(file)
	if agent=='Bandit':
		policy = np.zeros((2+nS, nA))
		for s in range(2+nS):
			policy[s] = data['Q']
	elif agent=='QLearn':
		policy = data['Q']
	elif agent=="ModelBased":
		policy = data['pi']

	xticks = np.arange(0, nA)
	yticks = np.linspace(0, 1, 2+nS)
	ytickLabels = []
	ytickLabels.append("Turn 1")
	ytickLabels.append("Opponent Skipped")
	for s in np.linspace(0, 1, nS):
		ytickLabels.append(np.around(s, 2))

	rx = (xticks[1]-xticks[0])/2
	ry = (yticks[1]-yticks[0])/2
	viridis = plt.get_cmap('viridis', 256)

	# normalize by dividing by max Q value in each state
	# rowMax = np.max(policy, axis=1)
	# for r in range(2+nS):
	# 	if rowMax[r]==0: rowMax[r] = 1;
	# policy /= rowMax[:, np.newaxis]

	# normalize with softmax
	policy = softmax(policy/10, axis=1)

	RGB = viridis(policy)
	fig, ax = plt.subplots(figsize=((16, 8)))
	c = ax.imshow(RGB,
		vmin=0, vmax=1,
		extent=[xticks[0]-rx, xticks[-1]+rx, yticks[0]-ry, yticks[-1]+ry],
		interpolation='nearest',
		origin='lower',
		cmap='viridis')
	ax.set_aspect('auto')
	plt.colorbar(c)
	ax.set_xticks(xticks)
	ax.set_yticks(yticks)
	ax.set_yticklabels(ytickLabels)
	posx = np.linspace(start=xticks[0]-rx, stop=xticks[-1]+rx, num=nA, endpoint=False)
	posy = np.linspace(start=yticks[0]-ry, stop=yticks[-1]+ry, num=2+nS, endpoint=False)
	plt.xlabel("Action")
	plt.ylabel("State (Opponent Generosity)")
	plt.title(f"{agent} {player} {group} Policy")
	fig.savefig(f"plots/{agent}_{player}_{group}_Policy")

def plotGreedyAndGenerous1D(df, byAgent=False):
	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((16,16)))
	dfGenerousA = df.query("group == 'generous' & player == 'A'")
	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
	dfGenerousB = df.query("group == 'generous' & player == 'B'")
	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
	if byAgent:
		sns.lineplot(data=dfGenerousA, x='game', y='generosity', hue='agent', ax=ax)
		sns.lineplot(data=dfGreedyA, x='game', y='generosity', hue='agent', ax=ax2)
		sns.lineplot(data=dfGenerousB, x='game', y='generosity', hue='agent', ax=ax3)
		sns.lineplot(data=dfGreedyB, x='game', y='generosity', hue='agent', ax=ax4)
	else:
		sns.lineplot(data=dfGenerousA, x='game', y='generosity', ax=ax)
		sns.lineplot(data=dfGreedyA, x='game', y='generosity', ax=ax2)
		sns.lineplot(data=dfGenerousB, x='game', y='generosity', ax=ax3)
		sns.lineplot(data=dfGreedyB, x='game', y='generosity', ax=ax4)		
	ax.set(title="Learn to be Generous, Investor", ylabel='Generosity', xlabel="", ylim=((0, 1)))
	ax2.set(title="Learn to be Greedy, Investor", xlabel="", ylim=((0, 1)))
	ax3.set(title="Learn to be Generous, Trustee", xlabel='Game', ylabel='Generosity', ylim=((0, 1)))
	ax4.set(title="Learn to be Greedy, Trustee", xlabel='Game', ylim=((0, 1)))
	if byAgent:
		fig.savefig("plots/Generosity_vs_Time_byAgent.pdf")
	else:
		fig.savefig("plots/Generosity_vs_Time_mean.pdf")

	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((16,16)))
	dfGenerousA = df.query("group == 'generous' & player == 'A'")
	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
	dfGenerousB = df.query("group == 'generous' & player == 'B'")
	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
	if byAgent:
		sns.lineplot(data=dfGenerousA, x='game', y='reward', hue='agent', ax=ax)
		sns.lineplot(data=dfGreedyA, x='game', y='reward', hue='agent', ax=ax2)
		sns.lineplot(data=dfGenerousB, x='game', y='reward', hue='agent', ax=ax3)
		sns.lineplot(data=dfGreedyB, x='game', y='reward', hue='agent', ax=ax4)
	else:
		sns.lineplot(data=dfGenerousA, x='game', y='reward', ax=ax)
		sns.lineplot(data=dfGreedyA, x='game', y='reward', ax=ax2)
		sns.lineplot(data=dfGenerousB, x='game', y='reward', ax=ax3)
		sns.lineplot(data=dfGreedyB, x='game', y='reward', ax=ax4)
	ax.set(title="Learn to be Generous, Investor", ylabel='Score', xlabel="", ylim=((0, 30)))
	ax2.set(title="Learn to be Greedy, Investor", xlabel="", ylim=((0, 30)))
	ax3.set(title="Learn to be Generous, Trustee", xlabel='Game', ylabel='Score', ylim=((0, 30)))
	ax4.set(title="Learn to be Greedy, Trustee", xlabel='Game', ylim=((0, 30)))
	if byAgent:
		fig.savefig("plots/Score_vs_Time_byAgent.pdf")
	else:
		fig.savefig("plots/Score_vs_Time_mean.pdf")


def plotScoreGenContour(df, REQUIRED, altruism_threshold=0.2):
	xticks = np.arange(0, int(REQUIRED))
	genA = df.query("group=='generous' & player=='A'")
	genB = df.query("group=='generous' & player=='B'")
	gredA = df.query("group=='greedy' & player=='A'")
	gredB = df.query("group=='greedy' & player=='B'")

	fig, ((ax, ax3), (ax2, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((12, 12)))
	sns.kdeplot(data=genA, x='game', y='reward', bw_method=0.1, fill=True, ax=ax)
	sns.kdeplot(data=genB, x='game', y='reward', bw_method=0.1, fill=True, ax=ax2)
	sns.kdeplot(data=gredA, x='game', y='reward', bw_method=0.1, fill=True, ax=ax3)
	sns.kdeplot(data=gredB, x='game', y='reward', bw_method=0.1, fill=True, ax=ax4)
	ax.set(xlim=((0, int(REQUIRED))), ylim=((5, 16)), xlabel='', title='Player A, Group Generous')
	ax2.set(xlim=((0, int(REQUIRED))), ylim=((0, 14)), title='Player B, Group Generous')
	ax3.set(xlim=((0, int(REQUIRED))), ylim=((2, 11)), xticks=xticks, ylabel='', title='Player A, Group Greedy')
	ax4.set(xlim=((0, int(REQUIRED))), ylim=((5, 30)), xticks=xticks, ylabel='', title='Player B, Group Greedy')
	fig.savefig('plots/ScoreContourAgent.pdf')
	fig, ((ax, ax3), (ax2, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((12, 12)))
	sns.kdeplot(data=genA, x='game', y='generosity', bw_method=0.1, fill=True, ax=ax)
	sns.kdeplot(data=genB, x='game', y='generosity', bw_method=0.1, fill=True, ax=ax2)
	sns.kdeplot(data=gredA, x='game', y='generosity', bw_method=0.1, fill=True, ax=ax3)
	sns.kdeplot(data=gredB, x='game', y='generosity', bw_method=0.1, fill=True, ax=ax4)
	ax.set(xlim=((0, int(REQUIRED))), ylim=((-0.1, 1)), xlabel='', title='Player A, Group Generous')
	ax2.set(xlim=((0, int(REQUIRED))), ylim=((-0.1, 1)), title='Player B, Group Generous')
	ax3.set(xlim=((0, int(REQUIRED))), ylim=((-0.1, 1)), xticks=xticks, ylabel='', title='Player A, Group Greedy')
	ax4.set(xlim=((0, int(REQUIRED))), ylim=((-0.1, 1)), xticks=xticks, ylabel='', title='Player B, Group Greedy')
	fig.savefig('plots/GenContourAgent.pdf')

	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2)
	sns.barplot(data=df, x='altruism', y='generosity', hue='group', order=['self', 'equal'], ax=ax)
	sns.barplot(data=df, x='altruism', y='reward', hue='group', order=['self', 'equal'], ax=ax2)
	plt.tight_layout()
	fig.savefig(f'plots/ScoreGenVsAltruismAgent.pdf')


	# fig, ((ax, ax3), (ax2, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((12, 12)))
	# sns.kdeplot(data=genA.query("altruism>=@altruism_threshold"), x='game', y='reward', bw_method=0.1, fill=True, ax=ax)
	# sns.kdeplot(data=genB.query("altruism>=@altruism_threshold"), x='game', y='reward', bw_method=0.1, fill=True, ax=ax2)
	# sns.kdeplot(data=gredA.query("altruism>=@altruism_threshold"), x='game', y='reward', bw_method=0.1, fill=True, ax=ax3)
	# sns.kdeplot(data=gredB.query("altruism>=@altruism_threshold"), x='game', y='reward', bw_method=0.1, fill=True, ax=ax4)
	# ax.set(xlim=((0, int(REQUIRED/2))), ylim=((5, 16)), xlabel='', title='Player A, Group Generous')
	# ax2.set(xlim=((0, int(REQUIRED/2))), ylim=((0, 14)), title='Player B, Group Generous')
	# ax3.set(xlim=((0, int(REQUIRED/2))), ylim=((2, 11)), xticks=xticks, ylabel='', title='Player A, Group Greedy')
	# ax4.set(xlim=((0, int(REQUIRED/2))), ylim=((5, 30)), xticks=xticks, ylabel='', title='Player B, Group Greedy')
	# fig.savefig('plots/ScoreContourEqual.pdf')
	# fig, ((ax, ax3), (ax2, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((12, 12)))
	# sns.kdeplot(data=genA.query("altruism>=@altruism_threshold"), x='game', y='generosity', bw_method=0.1, fill=True, ax=ax)
	# sns.kdeplot(data=genB.query("altruism>=@altruism_threshold"), x='game', y='generosity', bw_method=0.1, fill=True, ax=ax2)
	# sns.kdeplot(data=gredA.query("altruism>=@altruism_threshold"), x='game', y='generosity', bw_method=0.1, fill=True, ax=ax3)
	# sns.kdeplot(data=gredB.query("altruism>=@altruism_threshold"), x='game', y='generosity', bw_method=0.1, fill=True, ax=ax4)
	# ax.set(xlim=((0, int(REQUIRED/2))), ylim=((-0.1, 1)), xlabel='', title='Player A, Group Generous')
	# ax2.set(xlim=((0, int(REQUIRED/2))), ylim=((-0.1, 1)), title='Player B, Group Generous')
	# ax3.set(xlim=((0, int(REQUIRED/2))), ylim=((-0.1, 1)), xticks=xticks, ylabel='', title='Player A, Group Greedy')
	# ax4.set(xlim=((0, int(REQUIRED/2))), ylim=((-0.1, 1)), xticks=xticks, ylabel='', title='Player B, Group Greedy')
	# fig.savefig('plots/GenContourEqual.pdf')

	# fig, ((ax, ax3), (ax2, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((12, 12)))
	# sns.kdeplot(data=genA.query("altruism<@altruism_threshold"), x='game', y='reward', bw_method=0.1, fill=True, ax=ax)
	# sns.kdeplot(data=genB.query("altruism<@altruism_threshold"), x='game', y='reward', bw_method=0.1, fill=True, ax=ax2)
	# sns.kdeplot(data=gredA.query("altruism<@altruism_threshold"), x='game', y='reward', bw_method=0.1, fill=True, ax=ax3)
	# sns.kdeplot(data=gredB.query("altruism<@altruism_threshold"), x='game', y='reward', bw_method=0.1, fill=True, ax=ax4)
	# ax.set(xlim=((0, int(REQUIRED/2))), ylim=((5, 16)), xlabel='', title='Player A, Group Generous')
	# ax2.set(xlim=((0, int(REQUIRED/2))), ylim=((0, 14)), title='Player B, Group Generous')
	# ax3.set(xlim=((0, int(REQUIRED/2))), ylim=((2, 11)), xticks=xticks, ylabel='', title='Player A, Group Greedy')
	# ax4.set(xlim=((0, int(REQUIRED/2))), ylim=((5, 30)), xticks=xticks, ylabel='', title='Player B, Group Greedy')
	# fig.savefig('plots/ScoreContourSelf.pdf')
	# fig, ((ax, ax3), (ax2, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=True, figsize=((12, 12)))
	# sns.kdeplot(data=genA.query("altruism<@altruism_threshold"), x='game', y='generosity', bw_method=0.1, fill=True, ax=ax)
	# sns.kdeplot(data=genB.query("altruism<@altruism_threshold"), x='game', y='generosity', bw_method=0.1, fill=True, ax=ax2)
	# sns.kdeplot(data=gredA.query("altruism<@altruism_threshold"), x='game', y='generosity', bw_method=0.1, fill=True, ax=ax3)
	# sns.kdeplot(data=gredB.query("altruism<@altruism_threshold"), x='game', y='generosity', bw_method=0.1, fill=True, ax=ax4)
	# ax.set(xlim=((0, int(REQUIRED/2))), ylim=((-0.1, 1)), xlabel='', title='Player A, Group Generous')
	# ax2.set(xlim=((0, int(REQUIRED/2))), ylim=((-0.1, 1)), title='Player B, Group Generous')
	# ax3.set(xlim=((0, int(REQUIRED/2))), ylim=((-0.1, 1)), xticks=xticks, ylabel='', title='Player A, Group Greedy')
	# ax4.set(xlim=((0, int(REQUIRED/2))), ylim=((-0.1, 1)), xticks=xticks, ylabel='', title='Player B, Group Greedy')
	# fig.savefig('plots/GenContourSelf.pdf')

def plotScoreGenContourSingle(df, turns, group, ylim):
	xticks = np.arange(0, int(turns))
	final = turns-1
	palette = sns.color_palette()

	# initial_values_score = np.array(df.query('game==0')['reward'])
	# initial_values_gen = np.array(df.query('game==0')['generosity'])
	# final_values_score = np.array(df.query('game==@final')['reward'])
	# final_values_gen = np.array(df.query('game==@final')['generosity'])
	# pval_score = ks_2samp(initial_values_score, final_values_score)[1]
	# pval_gen = ks_2samp(initial_values_gen, final_values_gen)[1]
	# if pval_score < 1e-4:
	# 	pval_score = 1e-4
	# 	sym_score = "<"
	# else:
	# 	sym_score = "="
	# if pval_gen < 1e-4:
	# 	pval_gen = 1e-4
	# 	sym_gen = "<"
	# else:
	# 	sym_gen = "="
	# fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)), sharex=True)
	# sns.kdeplot(data=df, x='game', y='reward', bw_method=0.1, fill=True, ax=ax)
	# sns.kdeplot(data=df, x='game', y='generosity', bw_method=0.1, fill=True, ax=ax2)
	# ax.set(ylim=ylim, ylabel='score', title=f"{group}\nKS-test(initial, final): p{sym_score}{pval_score:.4f}")
	# ax2.set(ylim=((-0.1, 1.1)), title=f"{group}\nKS-test(initial, final): p{sym_gen}{pval_gen:.4f}")
	# fig.savefig(f'plots/ScoreGenVsTime_Agent_Contour_{group}.pdf')


	unfriendly_values_score = np.array(df.query('game==@final & rO==0')['reward'])
	unfriendly_values_gen = np.array(df.query('game==@final & rO==0')['generosity'])
	friendly_values_score = np.array(df.query('game==@final & rO>0')['reward'])
	friendly_values_gen = np.array(df.query('game==@final & rO>0')['generosity'])
	pval_score = ks_2samp(unfriendly_values_score, friendly_values_score)[1]
	pval_gen = ks_2samp(unfriendly_values_gen, friendly_values_gen)[1]
	if pval_score < 1e-4:
		pval_score = 1e-4
		sym_score = "<"
	else:
		sym_score = "="
	if pval_gen < 1e-4:
		pval_gen = 1e-4
		sym_gen = "<"
	else:
		sym_gen = "="


	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
	sns.kdeplot(data=df.query('rO==0'), x='game', y='generosity', bw_method=0.1, color=palette[1], fill=True, ax=ax)
	sns.kdeplot(data=df.query('rO==0'), x='game', y='reward', bw_method=0.1, color=palette[1], fill=True, ax=ax2)
	sns.kdeplot(data=df.query('rO>0'), x='game', y='generosity', bw_method=0.1, color=palette[1], fill=True, ax=ax3)
	sns.kdeplot(data=df.query('rO>0'), x='game', y='reward', bw_method=0.1, color=palette[1], fill=True, ax=ax4)
	ax.set(ylim=((-0.1, 1.1)), title=f"{group_text}, Self-Oriented")
	ax2.set(ylim=ylim, ylabel='score', title=f"{group_text}, Self-Oriented")
	ax3.set(ylim=((-0.1, 1.1)), xticks=xticks, title=f'{group_text}, Socially-Oriented')
	ax4.set(ylim=ylim, ylabel='score', xticks=xticks, title=f'{group_text}, Socially-Oriented')
	ax.legend((f"p{sym_score}{pval_score:.4f}",), fontsize="x-small")
	ax2.legend((f"p{sym_gen}{pval_gen:.4f}",), fontsize="x-small")
	plt.tight_layout()
	fig.savefig(f'plots/ScoreGenVsTime_Agent_Contour_{group}_Orientation.pdf')
	fig.savefig(f'plots/ScoreGenVsTime_Agent_Contour_{group}_Orientation.svg')


def plotScoreGenAll(games=15, load=True, orientation_thr=0, exploration_thr=0.6):
	final = games-1
	last_three = games-3
	first_three = 3
	xticks = np.array([0, final])
	xlim = np.array([-1, final+1])
	palette = sns.color_palette()
	x = 'group'
	y1 = 'generosity'
	y2 = 'score'
	groups = ['greedy', 'generous']
	players = ["A", "B"]
	groups_label = ['Greedy', 'Generous']
	players_label = ["Investor", "Trustee"]
	fourgroups = ["Investor\nGreedy", "Investor\nGenerous", "Trustee\nGreedy", "Trustee\nGenerous"]
	fourlabels = ["Investor, Greedy", "Investor, Generous", "Trustee, Greedy", "Trustee, Generous"]
	fournames = ["InvestorGreedy", "InvestorGenerous", "TrusteeGreedy", "TrusteeGenerous"]
	four1 = fourgroups[0]
	four2 = fourgroups[1]
	four3 = fourgroups[2]
	four4 = fourgroups[3]

	# rebuild dataframe to include entries for orientation and group
	if load:
		df = pd.read_pickle("plots/plotScoreGenDistribution_Agent.pkl")
	else:
		groupsAgent = ['InvestorGreedy', 'TrusteeGreedy', 'InvestorGenerous', 'TrusteeGenerous']
		columns = ('ID', 'group', 'player', 'fourgroup',
			'game', 'turn', 'score', 'generosity',
			'orientation', 'exploration', 'gamma')
		dfs = []
		for group in groupsAgent:
			opp_group = "greedy" if group=='InvestorGreedy' or group=='TrusteeGreedy' else 'generous'
			player = 'A' if group=='InvestorGreedy' or group=='InvestorGenerous' else 'B'
			if opp_group=='greedy' and player=='A': fourgroup = "Investor\nGreedy"
			if opp_group=='greedy' and player=='B': fourgroup = "Trustee\nGreedy"
			if opp_group=='generous' and player=='A': fourgroup = "Investor\nGenerous"
			if opp_group=='generous' and player=='B': fourgroup = "Trustee\nGenerous"
			dfIn = pd.read_pickle(f"data/{group}.pkl")
			for index, row in dfIn.iterrows():
				orientation = 'self' if row['rO'] <= orientation_thr else 'social'
				exploration = 'low' if row['dE'] <= exploration_thr else 'high'
				horizon = row['G']
				if np.isnan(row['generosity']):
					continue
				else:
					gen = row['generosity']
					newRow = pd.DataFrame([[
						row['agent'], opp_group, player, fourgroup,
						row['game'], row['turn'], row['reward'], gen,
						orientation, exploration, horizon
						]], columns=columns)
					dfs.append(newRow)
		df = pd.concat([df for df in dfs], ignore_index=True)
		df.to_pickle("plots/plotScoreGenDistribution_Agent.pkl")


	print("ORIENTATION")
	independent = ['self', 'social']
	ind_label = ["Self-Oriented", "Socially-Oriented"]
	ind0, ind1 = independent[0], independent[1]
	box_pairs = [
		((four1, ind0), (four1, ind1)),
		((four2, ind0), (four2, ind1)),
		((four3, ind0), (four3, ind1)),
		((four4, ind0), (four4, ind1)),
		]

	for i, fourgroup in enumerate(fourgroups):
		fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
		data = df.query("fourgroup==@fourgroup")
		score1 = np.array(data.query('orientation==@ind0 & game<@first_three')['score'])
		gen1 = np.array(data.query('orientation==@ind0 & game<@first_three')['generosity'])
		score2 = np.array(data.query('orientation==@ind1 & game<=@first_three')['score'])
		gen2 = np.array(data.query('orientation==@ind1 & game<@first_three')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"initial distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		score1 = np.array(data.query('orientation==@ind0 & game>=@last_games')['score'])
		gen1 = np.array(data.query('orientation==@ind0 & game>=@last_games')['generosity'])
		score2 = np.array(data.query('orientation==@ind1 & game>=@last_games')['score'])
		gen2 = np.array(data.query('orientation==@ind1 & game>=@last_games')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"final distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		score1 = np.array(data.query('orientation==@ind0')['score'])
		gen1 = np.array(data.query('orientation==@ind0')['generosity'])
		score2 = np.array(data.query('orientation==@ind1')['score'])
		gen2 = np.array(data.query('orientation==@ind1')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"overall distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
		sns.kdeplot(data=data.query("orientation==@ind0"), x='game', y='generosity', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax)
		sns.kdeplot(data=data.query("orientation==@ind0"), x='game', y='score', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax2)
		sns.kdeplot(data=data.query("orientation==@ind1"), x='game', y='generosity', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax3)
		sns.kdeplot(data=data.query("orientation==@ind1"), x='game', y='score', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax4)
		ax.set(ylim=((-0.1, 1.1)), yticks=((0, 1)))
		ax2.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score')
		ax3.set(ylim=((-0.1, 1.1)), yticks=((0, 1)), xticks=((0, 14)))
		ax4.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score', xticks=((0, 14)))
		ax.legend((f"{fourlabels[i]}, {ind_label[0]}",), loc="upper right", frameon=False)
		ax2.legend((f"{fourlabels[i]}, {ind_label[0]}",), loc="upper right", frameon=False)
		ax3.legend((f"{fourlabels[i]}, {ind_label[1]}",), loc="upper right", frameon=False)
		ax4.legend((f"{fourlabels[i]}, {ind_label[1]}",), loc="upper right", frameon=False)
		plt.tight_layout()
		fig.savefig(f'plots/ScoreGenDistribution_Agent_{fournames[i]}_Orientation.pdf')
		fig.savefig(f'plots/ScoreGenDistribution_Agent_{fournames[i]}_Orientation.svg')

	y1s = [
		np.mean(df.query("fourgroup==@four1 & orientation==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four1 & orientation==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four2 & orientation==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four2 & orientation==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four3 & orientation==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four3 & orientation==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four4 & orientation==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four4 & orientation==@ind1")['generosity']),
		]
	y2s = [
		np.mean(df.query("fourgroup==@four1 & orientation==@ind0")['score']),
		np.mean(df.query("fourgroup==@four1 & orientation==@ind1")['score']),
		np.mean(df.query("fourgroup==@four2 & orientation==@ind0")['score']),
		np.mean(df.query("fourgroup==@four2 & orientation==@ind1")['score']),
		np.mean(df.query("fourgroup==@four3 & orientation==@ind0")['score']),
		np.mean(df.query("fourgroup==@four3 & orientation==@ind1")['score']),
		np.mean(df.query("fourgroup==@four4 & orientation==@ind0")['score']),
		np.mean(df.query("fourgroup==@four4 & orientation==@ind1")['score']),
		]
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)), sharex=True)
	sns.barplot(data=df, x='fourgroup', y=y1, order=fourgroups, hue='orientation', hue_order=independent, ax=ax)
	sns.barplot(data=df, x='fourgroup', y=y2, order=fourgroups, hue='orientation', hue_order=independent, ax=ax2)
	add_stat_annotation(ax, data=df, x='fourgroup', y=y1, order=fourgroups, hue='orientation', hue_order=independent, box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside')
	add_stat_annotation(ax2, data=df, x='fourgroup', y=y2, order=fourgroups, hue='orientation', hue_order=independent, box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside')
	for i, v in enumerate(y1s):
		plt.text(x=i/3, y=10*v, s=f"{v:.2f}")
	for i, v in enumerate(y2s):
		plt.text(x=i/3, y=5+v/2, s=f"{v:.2f}")
	ax.set(xlabel='', ylabel='Generosity', yticks=(()))
	ax2.set(xlabel='', ylabel='Score', yticks=(()))
	ax2.get_legend().remove()
	plt.tight_layout()
	fig.savefig(f'plots/ScoreGenBarplot_Agent_Orientation.pdf')
	fig.savefig(f'plots/ScoreGenBarplot_Agent_Orientation.svg')


	print("EXPLORATION")
	independent = ['low', 'high']
	ind_label = ["Low Exploration", "High Exploration"]
	ind0, ind1 = independent[0], independent[1]
	box_pairs = [
		((four1, ind0), (four1, ind1)),
		((four2, ind0), (four2, ind1)),
		((four3, ind0), (four3, ind1)),
		((four4, ind0), (four4, ind1)),
		]

	for i, fourgroup in enumerate(fourgroups):
		fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
		data = df.query("fourgroup==@fourgroup")
		score1 = np.array(data.query('exploration==@ind0 & game<@first_three')['score'])
		gen1 = np.array(data.query('exploration==@ind0 & game<@first_three')['generosity'])
		score2 = np.array(data.query('exploration==@ind1 & game<=@first_three')['score'])
		gen2 = np.array(data.query('exploration==@ind1 & game<@first_three')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"initial distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		score1 = np.array(data.query('exploration==@ind0 & game>=@last_games')['score'])
		gen1 = np.array(data.query('exploration==@ind0 & game>=@last_games')['generosity'])
		score2 = np.array(data.query('exploration==@ind1 & game>=@last_games')['score'])
		gen2 = np.array(data.query('exploration==@ind1 & game>=@last_games')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"final distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		score1 = np.array(data.query('exploration==@ind0')['score'])
		gen1 = np.array(data.query('exploration==@ind0')['generosity'])
		score2 = np.array(data.query('exploration==@ind1')['score'])
		gen2 = np.array(data.query('exploration==@ind1')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"overall distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
		sns.kdeplot(data=data.query("exploration==@ind0"), x='game', y='generosity', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax)
		sns.kdeplot(data=data.query("exploration==@ind0"), x='game', y='score', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax2)
		sns.kdeplot(data=data.query("exploration==@ind1"), x='game', y='generosity', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax3)
		sns.kdeplot(data=data.query("exploration==@ind1"), x='game', y='score', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax4)
		ax.set(ylim=((-0.1, 1.1)), yticks=((0, 1)))
		ax2.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score')
		ax3.set(ylim=((-0.1, 1.1)), yticks=((0, 1)), xticks=((0, 14)))
		ax4.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score', xticks=((0, 14)))
		ax.legend((f"{fourlabels[i]}, {ind_label[0]}",), loc="upper right", frameon=False)
		ax2.legend((f"{fourlabels[i]}, {ind_label[0]}",), loc="upper right", frameon=False)
		ax3.legend((f"{fourlabels[i]}, {ind_label[1]}",), loc="upper right", frameon=False)
		ax4.legend((f"{fourlabels[i]}, {ind_label[1]}",), loc="upper right", frameon=False)
		plt.tight_layout()
		fig.savefig(f'plots/ScoreGenDistribution_Agent_{fournames[i]}_Exploration.pdf')
		fig.savefig(f'plots/ScoreGenDistribution_Agent_{fournames[i]}_Exploration.svg')

	y1s = [
		np.mean(df.query("fourgroup==@four1 & exploration==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four1 & exploration==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four2 & exploration==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four2 & exploration==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four3 & exploration==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four3 & exploration==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four4 & exploration==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four4 & exploration==@ind1")['generosity']),
		]
	y2s = [
		np.mean(df.query("fourgroup==@four1 & exploration==@ind0")['score']),
		np.mean(df.query("fourgroup==@four1 & exploration==@ind1")['score']),
		np.mean(df.query("fourgroup==@four2 & exploration==@ind0")['score']),
		np.mean(df.query("fourgroup==@four2 & exploration==@ind1")['score']),
		np.mean(df.query("fourgroup==@four3 & exploration==@ind0")['score']),
		np.mean(df.query("fourgroup==@four3 & exploration==@ind1")['score']),
		np.mean(df.query("fourgroup==@four4 & exploration==@ind0")['score']),
		np.mean(df.query("fourgroup==@four4 & exploration==@ind1")['score']),
		]
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)), sharex=True)
	sns.barplot(data=df, x='fourgroup', y=y1, order=fourgroups, hue='exploration', hue_order=independent, ax=ax)
	sns.barplot(data=df, x='fourgroup', y=y2, order=fourgroups, hue='exploration', hue_order=independent, ax=ax2)
	add_stat_annotation(ax, data=df, x='fourgroup', y=y1, order=fourgroups, hue='exploration', hue_order=independent, box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside')
	add_stat_annotation(ax2, data=df, x='fourgroup', y=y2, order=fourgroups, hue='exploration', hue_order=independent, box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside')
	for i, v in enumerate(y1s):
		plt.text(x=i/3, y=10*v, s=f"{v:.2f}")
	for i, v in enumerate(y2s):
		plt.text(x=i/3, y=5+v/2, s=f"{v:.2f}")
	ax.set(xlabel='', ylabel='Generosity', yticks=(()))
	ax2.set(xlabel='', ylabel='Score', yticks=(()))
	ax2.get_legend().remove()
	plt.tight_layout()
	fig.savefig(f'plots/ScoreGenBarplot_Agent_Exploration.pdf')
	fig.savefig(f'plots/ScoreGenBarplot_Agent_Exploration.svg')





def plotScoreGenFourGroups(architecture, load=False, orientation_thr=0, exploration_thr=2.0, first_last_games=3):
	REQUIRED = 30
	TURNS = 5
	dfIn = pd.read_pickle(f"data/runFourGroups_{architecture}.pkl")
	final = int(REQUIRED/2)-1
	first_games = first_last_games
	last_games = int(REQUIRED/2)-first_last_games
	first_turns = first_games*TURNS
	last_turns = last_games*TURNS
	xticks = np.array([0, final])
	xlim = np.array([-1, final+1])
	palette = sns.color_palette()
	y1 = 'generosity'
	y2 = 'score'
	groups = ['greedy', 'generous']
	groups_label = ['Greedy', 'Generous']
	players = ["A", "B"]
	players_label = ["Investor", "Trustee"]
	fourgroups = ["Investor\nGreedy", "Investor\nGenerous", "Trustee\nGreedy", "Trustee\nGenerous"]
	fourlabels = ["Investor, Greedy", "Investor, Generous", "Trustee, Greedy", "Trustee, Generous"]
	fournames = ["InvestorGreedy", "InvestorGenerous", "TrusteeGreedy", "TrusteeGenerous"]
	four1 = fourgroups[0]
	four2 = fourgroups[1]
	four3 = fourgroups[2]
	four4 = fourgroups[3]
	if architecture == "bandit": architecture_label = "A-agent"
	if architecture == "qlearn": architecture_label = "SA-agent"
	if architecture == "modelbased": architecture_label = "SAS-agent"

	# rebuild dataframe to include entries for orientation and group
	if load:
		df = pd.read_pickle(f"plots/plotScoreGenDistribution_{architecture}.pkl")
	else:
		# collect average data about the agent
		dfsAgent = []
		columns = ('agent', 'group', 'player', 'orientation', 'exploration', 'gamma')
		agents = dfIn['agent'].unique()
		for agent in agents:
			for group in groups:
				for player in players:
					data = dfIn.query("agent==@agent & player==@player & group==@group")
					gens = data['generosity'].to_numpy()
					scores = data['score'].to_numpy()
					# exploration = 'low' if np.std(gens[:first_turns]) < exploration_thr else 'high'
					orientation = "self" if data['rO'].values[0] <= orientation_thr else "social"
					exploration = 'low' if entropy(gens[:first_turns]) < exploration_thr else 'high'
					gamma = data['G'].values[0]
					dfsAgent.append(pd.DataFrame([[agent, group, player, orientation, exploration, gamma]], columns=columns))			
		dfAgent = pd.concat([df for df in dfsAgent], ignore_index=True)
		# create the main dataframe (per-turn score/gen info), appending user data
		columns = ('ID', 'group', 'player', 'fourgroup',
			'game', 'turn', 'score', 'generosity',
			'orientation', 'exploration', 'gamma')
		dfs = []
		for index, row in dfIn.iterrows():
			agent = row['agent']
			group = row['group']
			player = row['player']
			if group=='greedy' and player=='A': fourgroup = "Investor\nGreedy"
			if group=='greedy' and player=='B': fourgroup = "Trustee\nGreedy"
			if group=='generous' and player=='A': fourgroup = "Investor\nGenerous"
			if group=='generous' and player=='B': fourgroup = "Trustee\nGenerous"
			data = dfAgent.query("agent==@agent & group==@group & player==@player")
			orientation = data['orientation'].values[0]
			exploration = data['exploration'].values[0]
			gamma = data['gamma'].values[0]
			newRow = pd.DataFrame([[
				row['agent'], group, player, fourgroup,
				row['game'], row['turn'], row['score'], row['generosity'],
				orientation, exploration, gamma
				]], columns=columns)
			dfs.append(newRow)
		df = pd.concat([df for df in dfs], ignore_index=True)
		df.to_pickle(f"plots/plotScoreGenDistribution_{architecture}.pkl")

	for i, fourgroup in enumerate(fourgroups):
		fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 2)))
		data = df.query("fourgroup==@fourgroup")
		score1 = np.array(data.query('game<@first_games')['score'])
		gen1 = np.array(data.query('game<@first_games')['generosity'])
		score2 = np.array(data.query('game>=@last_games')['score'])
		gen2 = np.array(data.query('game>=@last_games')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"{fourlabels[i]}, Learning KS test: SCORE p={pval_score}")
		print(f"{fourlabels[i]}, Learning KS test: GEN p={pval_gen}")
		sns.kdeplot(data=data, x='game', y='generosity', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax)
		sns.kdeplot(data=data, x='game', y='score', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax2)
		ax.set(xticks=((0, 14)), ylim=((-0.1, 1.1)), yticks=((0, 1)))
		ax2.set(xticks=((0, 14)), ylim=((-1, 31)), yticks=((0, 30)), ylabel='score')
		ax.legend((f"{fourlabels[i]}, {architecture_label}",), loc="upper right", frameon=False)
		ax2.legend((f"{fourlabels[i]}, {architecture_label}",), loc="upper right", frameon=False)	
		plt.tight_layout()
		fig.savefig(f'plots/ScoreGenDistribution_{architecture}_{fournames[i]}.pdf')
		fig.savefig(f'plots/ScoreGenDistribution_{architecture}_{fournames[i]}.svg')

	print("ORIENTATION")
	ind0, ind1 = 'self', 'social'
	ind0_label, ind1_label = 'Self-Oriented', 'Socially-Oriented'
	box_pairs = [
		((four1, ind0), (four1, ind1)),
		((four2, ind0), (four2, ind1)),
		((four3, ind0), (four3, ind1)),
		((four4, ind0), (four4, ind1)),
		]

	for i, fourgroup in enumerate(fourgroups):
		fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
		data = df.query("fourgroup==@fourgroup")
		score1 = np.array(data.query('orientation==@ind0 & game<@first_games')['score'])
		gen1 = np.array(data.query('orientation==@ind0 & game<@first_games')['generosity'])
		score2 = np.array(data.query('orientation==@ind1 & game<=@first_games')['score'])
		gen2 = np.array(data.query('orientation==@ind1 & game<@first_games')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"initial distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		score1 = np.array(data.query('orientation==@ind0 & game>=@last_games')['score'])
		gen1 = np.array(data.query('orientation==@ind0 & game>=@last_games')['generosity'])
		score2 = np.array(data.query('orientation==@ind1 & game>=@last_games')['score'])
		gen2 = np.array(data.query('orientation==@ind1 & game>=@last_games')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"final distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		score1 = np.array(data.query('orientation==@ind0')['score'])
		gen1 = np.array(data.query('orientation==@ind0')['generosity'])
		score2 = np.array(data.query('orientation==@ind1')['score'])
		gen2 = np.array(data.query('orientation==@ind1')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"overall distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
		sns.kdeplot(data=data.query("orientation==@ind0"), x='game', y='generosity', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax)
		sns.kdeplot(data=data.query("orientation==@ind0"), x='game', y='score', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax2)
		sns.kdeplot(data=data.query("orientation==@ind1"), x='game', y='generosity', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax3)
		sns.kdeplot(data=data.query("orientation==@ind1"), x='game', y='score', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax4)
		ax.set(ylim=((-0.1, 1.1)), yticks=((0, 1)))
		ax2.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score')
		ax3.set(ylim=((-0.1, 1.1)), yticks=((0, 1)), xticks=((0, 14)))
		ax4.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score', xticks=((0, 14)))
		ax.legend((f"{fourlabels[i]}, {ind0}",), loc="upper right", frameon=False)
		ax2.legend((f"{fourlabels[i]}, {ind0}",), loc="upper right", frameon=False)
		ax3.legend((f"{fourlabels[i]}, {ind1}",), loc="upper right", frameon=False)
		ax4.legend((f"{fourlabels[i]}, {ind1}",), loc="upper right", frameon=False)
		plt.tight_layout()
		fig.savefig(f'plots/ScoreGenDistribution_{architecture}_{fournames[i]}_Orientation.pdf')
		fig.savefig(f'plots/ScoreGenDistribution_{architecture}_{fournames[i]}_Orientation.svg')

	y1s = [
		np.mean(df.query("fourgroup==@four1 & orientation==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four1 & orientation==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four2 & orientation==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four2 & orientation==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four3 & orientation==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four3 & orientation==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four4 & orientation==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four4 & orientation==@ind1")['generosity']),
		]
	y2s = [
		np.mean(df.query("fourgroup==@four1 & orientation==@ind0")['score']),
		np.mean(df.query("fourgroup==@four1 & orientation==@ind1")['score']),
		np.mean(df.query("fourgroup==@four2 & orientation==@ind0")['score']),
		np.mean(df.query("fourgroup==@four2 & orientation==@ind1")['score']),
		np.mean(df.query("fourgroup==@four3 & orientation==@ind0")['score']),
		np.mean(df.query("fourgroup==@four3 & orientation==@ind1")['score']),
		np.mean(df.query("fourgroup==@four4 & orientation==@ind0")['score']),
		np.mean(df.query("fourgroup==@four4 & orientation==@ind1")['score']),
		]
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)), sharex=True)
	sns.barplot(data=df, x='fourgroup', y=y1, order=fourgroups, hue='orientation', hue_order=[ind0, ind1], ax=ax)
	sns.barplot(data=df, x='fourgroup', y=y2, order=fourgroups, hue='orientation', hue_order=[ind0, ind1], ax=ax2)
	add_stat_annotation(ax, data=df, x='fourgroup', y=y1, order=fourgroups, hue='orientation', hue_order=[ind0, ind1], box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside', verbose=0)
	add_stat_annotation(ax2, data=df, x='fourgroup', y=y2, order=fourgroups, hue='orientation', hue_order=[ind0, ind1], box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside', verbose=0)
	for i, v in enumerate(y1s):
		plt.text(x=i/3, y=10*v, s=f"{v:.2f}")
	for i, v in enumerate(y2s):
		plt.text(x=i/3, y=5+v/2, s=f"{v:.2f}")
	ax.set(xlabel='', ylabel='Generosity', yticks=(()))
	ax2.set(xlabel='', ylabel='Score', yticks=(()))
	ax2.get_legend().remove()
	plt.tight_layout()
	fig.savefig(f'plots/ScoreGenBarplot_{architecture}_Orientation.pdf')
	fig.savefig(f'plots/ScoreGenBarplot_{architecture}_Orientation.svg')


	print("EXPLORATION")
	ind0, ind1 = 'low', 'high'
	ind0_label, ind1_label = 'Low Exploration', 'High Exploration'
	box_pairs = [
		((four1, ind0), (four1, ind1)),
		((four2, ind0), (four2, ind1)),
		((four3, ind0), (four3, ind1)),
		((four4, ind0), (four4, ind1)),
		]

	for i, fourgroup in enumerate(fourgroups):
		try:
			fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
			data = df.query("fourgroup==@fourgroup")
			score1 = np.array(data.query('exploration==@ind0 & game<@first_games')['score'])
			gen1 = np.array(data.query('exploration==@ind0 & game<@first_games')['generosity'])
			score2 = np.array(data.query('exploration==@ind1 & game<=@first_games')['score'])
			gen2 = np.array(data.query('exploration==@ind1 & game<@first_games')['generosity'])
			ksval_score, pval_score = ks_2samp(score1, score2)
			ksval_gen, pval_gen = ks_2samp(gen1, gen2)
			print(f"initial distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
			score1 = np.array(data.query('exploration==@ind0 & game>=@last_games')['score'])
			gen1 = np.array(data.query('exploration==@ind0 & game>=@last_games')['generosity'])
			score2 = np.array(data.query('exploration==@ind1 & game>=@last_games')['score'])
			gen2 = np.array(data.query('exploration==@ind1 & game>=@last_games')['generosity'])
			ksval_score, pval_score = ks_2samp(score1, score2)
			ksval_gen, pval_gen = ks_2samp(gen1, gen2)
			print(f"final distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
			score1 = np.array(data.query('exploration==@ind0')['score'])
			gen1 = np.array(data.query('exploration==@ind0')['generosity'])
			score2 = np.array(data.query('exploration==@ind1')['score'])
			gen2 = np.array(data.query('exploration==@ind1')['generosity'])
			ksval_score, pval_score = ks_2samp(score1, score2)
			ksval_gen, pval_gen = ks_2samp(gen1, gen2)
			print(f"overall distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
			fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
			sns.kdeplot(data=data.query("exploration==@ind0"), x='game', y='generosity', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax)
			sns.kdeplot(data=data.query("exploration==@ind0"), x='game', y='score', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax2)
			sns.kdeplot(data=data.query("exploration==@ind1"), x='game', y='generosity', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax3)
			sns.kdeplot(data=data.query("exploration==@ind1"), x='game', y='score', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax4)
			ax.set(ylim=((-0.1, 1.1)), yticks=((0, 1)))
			ax2.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score')
			ax3.set(ylim=((-0.1, 1.1)), yticks=((0, 1)), xticks=((0, 14)))
			ax4.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score', xticks=((0, 14)))
			ax.legend((f"{fourlabels[i]}, {ind0}",), loc="upper right", frameon=False)
			ax2.legend((f"{fourlabels[i]}, {ind0}",), loc="upper right", frameon=False)
			ax3.legend((f"{fourlabels[i]}, {ind1}",), loc="upper right", frameon=False)
			ax4.legend((f"{fourlabels[i]}, {ind1}",), loc="upper right", frameon=False)
			plt.tight_layout()
			fig.savefig(f'plots/ScoreGenDistribution_{architecture}_{fournames[i]}_Exploration.pdf')
			fig.savefig(f'plots/ScoreGenDistribution_{architecture}_{fournames[i]}_Exploration.svg')
		except:
			continue

	y1s = [
		np.mean(df.query("fourgroup==@four1 & exploration==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four1 & exploration==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four2 & exploration==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four2 & exploration==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four3 & exploration==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four3 & exploration==@ind1")['generosity']),
		np.mean(df.query("fourgroup==@four4 & exploration==@ind0")['generosity']),
		np.mean(df.query("fourgroup==@four4 & exploration==@ind1")['generosity']),
		]
	y2s = [
		np.mean(df.query("fourgroup==@four1 & exploration==@ind0")['score']),
		np.mean(df.query("fourgroup==@four1 & exploration==@ind1")['score']),
		np.mean(df.query("fourgroup==@four2 & exploration==@ind0")['score']),
		np.mean(df.query("fourgroup==@four2 & exploration==@ind1")['score']),
		np.mean(df.query("fourgroup==@four3 & exploration==@ind0")['score']),
		np.mean(df.query("fourgroup==@four3 & exploration==@ind1")['score']),
		np.mean(df.query("fourgroup==@four4 & exploration==@ind0")['score']),
		np.mean(df.query("fourgroup==@four4 & exploration==@ind1")['score']),
		]
	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)), sharex=True)
	sns.barplot(data=df, x='fourgroup', y=y1, order=fourgroups, hue='exploration', hue_order=[ind0, ind1], ax=ax)
	sns.barplot(data=df, x='fourgroup', y=y2, order=fourgroups, hue='exploration', hue_order=[ind0, ind1], ax=ax2)
	add_stat_annotation(ax, data=df, x='fourgroup', y=y1, order=fourgroups, hue='exploration', hue_order=[ind0, ind1], box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside', verbose=0)
	add_stat_annotation(ax2, data=df, x='fourgroup', y=y2, order=fourgroups, hue='exploration', hue_order=[ind0, ind1], box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside', verbose=0)
	for i, v in enumerate(y1s):
		plt.text(x=i/3, y=10*v, s=f"{v:.2f}")
	for i, v in enumerate(y2s):
		plt.text(x=i/3, y=5+v/2, s=f"{v:.2f}")
	ax.set(xlabel='', ylabel='Generosity', yticks=(()))
	ax2.set(xlabel='', ylabel='Score', yticks=(()))
	ax2.get_legend().remove()
	plt.tight_layout()
	fig.savefig(f'plots/ScoreGenBarplot_{architecture}_Exploration.pdf')
	fig.savefig(f'plots/ScoreGenBarplot_{architecture}_Exploration.svg')

def plotScoreGenFourGroupsAll(load=True, orientation_thr=0, exploration_thr=2.0, first_last_games=3):
	REQUIRED = 30
	TURNS = 5
	final = int(REQUIRED/2)-1
	first_games = first_last_games
	last_games = int(REQUIRED/2)-first_last_games
	first_turns = first_games*TURNS
	last_turns = last_games*TURNS
	xticks = np.array([0, final])
	xlim = np.array([-1, final+1])
	palette = sns.color_palette()
	y1 = 'generosity'
	y2 = 'score'
	groups = ['greedy', 'generous']
	groups_label = ['Greedy', 'Generous']
	players = ["A", "B"]
	players_label = ["Investor", "Trustee"]
	fourgroups = ["Investor\nGreedy", "Investor\nGenerous", "Trustee\nGreedy", "Trustee\nGenerous"]
	fourlabels = ["Investor, Greedy", "Investor, Generous", "Trustee, Greedy", "Trustee, Generous"]
	fournames = ["InvestorGreedy", "InvestorGenerous", "TrusteeGreedy", "TrusteeGenerous"]
	four1 = fourgroups[0]
	four2 = fourgroups[1]
	four3 = fourgroups[2]
	four4 = fourgroups[3]

	if load:
		df = pd.concat([
			pd.read_pickle(f"plots/plotScoreGenDistribution_bandit.pkl"),
			pd.read_pickle(f"plots/plotScoreGenDistribution_qlearn.pkl"),
			pd.read_pickle(f"plots/plotScoreGenDistribution_modelbased.pkl")],ignore_index=True)
	else:
		for architecture in ['bandit', 'qlearn', 'modelbased']:
			# collect average data about the agent
			dfIn = pd.read_pickle(f"data/runFourGroups_{architecture}.pkl")
			dfsAgent = []
			columns = ('agent', 'group', 'player', 'orientation', 'exploration', 'gamma')
			agents = dfIn['agent'].unique()
			for agent in agents:
				for group in groups:
					for player in players:
						data = dfIn.query("agent==@agent & player==@player & group==@group")
						gens = data['generosity'].to_numpy()
						scores = data['score'].to_numpy()
						# exploration = 'low' if np.std(gens[:first_turns]) < exploration_thr else 'high'
						orientation = "self" if data['rO'].values[0] <= orientation_thr else "social"
						exploration = 'low' if entropy(gens[:first_turns]) < exploration_thr else 'high'
						gamma = data['G'].values[0]
						dfsAgent.append(pd.DataFrame([[agent, group, player, orientation, exploration, gamma]], columns=columns))			
			dfAgent = pd.concat([df for df in dfsAgent], ignore_index=True)
			# create the main dataframe (per-turn score/gen info), appending user data
			columns = ('ID', 'group', 'player', 'fourgroup',
				'game', 'turn', 'score', 'generosity',
				'orientation', 'exploration', 'gamma')
			dfs = []
			for index, row in dfIn.iterrows():
				agent = row['agent']
				group = row['group']
				player = row['player']
				if group=='greedy' and player=='A': fourgroup = "Investor\nGreedy"
				if group=='greedy' and player=='B': fourgroup = "Trustee\nGreedy"
				if group=='generous' and player=='A': fourgroup = "Investor\nGenerous"
				if group=='generous' and player=='B': fourgroup = "Trustee\nGenerous"
				data = dfAgent.query("agent==@agent & group==@group & player==@player")
				orientation = data['orientation'].values[0]
				exploration = data['exploration'].values[0]
				gamma = data['gamma'].values[0]
				newRow = pd.DataFrame([[
					row['agent'], group, player, fourgroup,
					row['game'], row['turn'], row['score'], row['generosity'],
					orientation, exploration, gamma
					]], columns=columns)
				dfs.append(newRow)
			df = pd.concat([df for df in dfs], ignore_index=True)
			df.to_pickle(f"plots/plotScoreGenDistribution_{architecture}.pkl")
		df = pd.concat([
			pd.read_pickle(f"plots/plotScoreGenDistribution_bandit.pkl"),
			pd.read_pickle(f"plots/plotScoreGenDistribution_qlearn.pkl"),
			pd.read_pickle(f"plots/plotScoreGenDistribution_modelbased.pkl")],ignore_index=True)


	# for i, fourgroup in enumerate(fourgroups):
	# 	fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 2)))
	# 	data = df.query("fourgroup==@fourgroup")
	# 	score1 = np.array(data.query('game<@first_games')['score'])
	# 	gen1 = np.array(data.query('game<@first_games')['generosity'])
	# 	score2 = np.array(data.query('game>=@last_games')['score'])
	# 	gen2 = np.array(data.query('game>=@last_games')['generosity'])
	# 	ksval_score, pval_score = ks_2samp(score1, score2)
	# 	ksval_gen, pval_gen = ks_2samp(gen1, gen2)
	# 	print(f"{fourlabels[i]}, Learning KS test: SCORE p={pval_score}")
	# 	print(f"{fourlabels[i]}, Learning KS test: GEN p={pval_gen}")
	# 	sns.kdeplot(data=data, x='game', y='generosity', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax)
	# 	sns.kdeplot(data=data, x='game', y='score', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax2)
	# 	ax.set(xticks=((0, 14)), ylim=((-0.1, 1.1)), yticks=((0, 1)))
	# 	ax2.set(xticks=((0, 14)), ylim=((-1, 31)), yticks=((0, 30)), ylabel='score')
	# 	ax.legend((f"{fourlabels[i]}, Agents",), loc="upper right", frameon=False)
	# 	ax2.legend((f"{fourlabels[i]}, Agents",), loc="upper right", frameon=False)	
	# 	plt.tight_layout()
	# 	fig.savefig(f'plots/ScoreGenDistribution_all_{fournames[i]}.pdf')
	# 	fig.savefig(f'plots/ScoreGenDistribution_all_{fournames[i]}.svg')

	print("ORIENTATION")
	ind0, ind1 = 'self', 'social'
	ind0_label, ind1_label = 'Self-Oriented', 'Socially-Oriented'
	box_pairs = [
		((four1, ind0), (four1, ind1)),
		((four2, ind0), (four2, ind1)),
		((four3, ind0), (four3, ind1)),
		((four4, ind0), (four4, ind1)),
		]

	for i, fourgroup in enumerate(fourgroups):
		fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
		data = df.query("fourgroup==@fourgroup")
		score1 = np.array(data.query('orientation==@ind0 & game<@first_games')['score'])
		gen1 = np.array(data.query('orientation==@ind0 & game<@first_games')['generosity'])
		score2 = np.array(data.query('orientation==@ind1 & game<=@first_games')['score'])
		gen2 = np.array(data.query('orientation==@ind1 & game<@first_games')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"initial distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		score1 = np.array(data.query('orientation==@ind0 & game>=@last_games')['score'])
		gen1 = np.array(data.query('orientation==@ind0 & game>=@last_games')['generosity'])
		score2 = np.array(data.query('orientation==@ind1 & game>=@last_games')['score'])
		gen2 = np.array(data.query('orientation==@ind1 & game>=@last_games')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"final distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		score1 = np.array(data.query('orientation==@ind0')['score'])
		gen1 = np.array(data.query('orientation==@ind0')['generosity'])
		score2 = np.array(data.query('orientation==@ind1')['score'])
		gen2 = np.array(data.query('orientation==@ind1')['generosity'])
		ksval_score, pval_score = ks_2samp(score1, score2)
		ksval_gen, pval_gen = ks_2samp(gen1, gen2)
		print(f"overall distribution KS test: SCORE p={pval_score:.4f}, GEN p={pval_gen:.4f}")
		fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=((8, 4)), sharex=True)
		sns.kdeplot(data=data.query("orientation==@ind0"), x='game', y='generosity', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax)
		sns.kdeplot(data=data.query("orientation==@ind0"), x='game', y='score', bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax2)
		sns.kdeplot(data=data.query("orientation==@ind1"), x='game', y='generosity', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax3)
		sns.kdeplot(data=data.query("orientation==@ind1"), x='game', y='score', color=palette[1], bw_method=0.1, levels=4, thresh=0.15, fill=True, ax=ax4)
		ax.set(ylim=((-0.1, 1.1)), yticks=((0, 1)))
		ax2.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score')
		ax3.set(ylim=((-0.1, 1.1)), yticks=((0, 1)), xticks=((0, 14)))
		ax4.set(ylim=((-1, 31)), yticks=((0, 30)), ylabel='score', xticks=((0, 14)))
		ax.legend((f"{fourlabels[i]}, {ind0_label}, Agent",), loc="upper right", frameon=False)
		ax2.legend((f"{fourlabels[i]}, {ind0_label}, Agent",), loc="upper right", frameon=False)
		ax3.legend((f"{fourlabels[i]}, {ind1_label}, Agent",), loc="upper right", frameon=False)
		ax4.legend((f"{fourlabels[i]}, {ind1_label}, Agent",), loc="upper right", frameon=False)
		plt.tight_layout()
		fig.savefig(f'plots/ScoreGenDistribution_all_{fournames[i]}_Orientation.pdf')
		fig.savefig(f'plots/ScoreGenDistribution_all_{fournames[i]}_Orientation.svg')

	# y1s = [
	# 	np.mean(df.query("fourgroup==@four1 & orientation==@ind0")['generosity']),
	# 	np.mean(df.query("fourgroup==@four1 & orientation==@ind1")['generosity']),
	# 	np.mean(df.query("fourgroup==@four2 & orientation==@ind0")['generosity']),
	# 	np.mean(df.query("fourgroup==@four2 & orientation==@ind1")['generosity']),
	# 	np.mean(df.query("fourgroup==@four3 & orientation==@ind0")['generosity']),
	# 	np.mean(df.query("fourgroup==@four3 & orientation==@ind1")['generosity']),
	# 	np.mean(df.query("fourgroup==@four4 & orientation==@ind0")['generosity']),
	# 	np.mean(df.query("fourgroup==@four4 & orientation==@ind1")['generosity']),
	# 	]
	# y2s = [
	# 	np.mean(df.query("fourgroup==@four1 & orientation==@ind0")['score']),
	# 	np.mean(df.query("fourgroup==@four1 & orientation==@ind1")['score']),
	# 	np.mean(df.query("fourgroup==@four2 & orientation==@ind0")['score']),
	# 	np.mean(df.query("fourgroup==@four2 & orientation==@ind1")['score']),
	# 	np.mean(df.query("fourgroup==@four3 & orientation==@ind0")['score']),
	# 	np.mean(df.query("fourgroup==@four3 & orientation==@ind1")['score']),
	# 	np.mean(df.query("fourgroup==@four4 & orientation==@ind0")['score']),
	# 	np.mean(df.query("fourgroup==@four4 & orientation==@ind1")['score']),
	# 	]
	# fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=((8, 4)), sharex=True)
	# sns.barplot(data=df, x='fourgroup', y=y1, order=fourgroups, hue='orientation', hue_order=[ind0, ind1], ax=ax)
	# sns.barplot(data=df, x='fourgroup', y=y2, order=fourgroups, hue='orientation', hue_order=[ind0, ind1], ax=ax2)
	# add_stat_annotation(ax, data=df, x='fourgroup', y=y1, order=fourgroups, hue='orientation', hue_order=[ind0, ind1], box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside', verbose=0)
	# add_stat_annotation(ax2, data=df, x='fourgroup', y=y2, order=fourgroups, hue='orientation', hue_order=[ind0, ind1], box_pairs=box_pairs, test='t-test_ind', text_format='star', loc='outside', verbose=0)
	# for i, v in enumerate(y1s):
	# 	plt.text(x=i/3, y=10*v, s=f"{v:.2f}")
	# for i, v in enumerate(y2s):
	# 	plt.text(x=i/3, y=5+v/2, s=f"{v:.2f}")
	# ax.set(xlabel='', ylabel='Generosity', yticks=(()))
	# ax2.set(xlabel='', ylabel='Score', yticks=(()))
	# ax2.get_legend().remove()
	# plt.tight_layout()
	# fig.savefig(f'plots/ScoreGenBarplot_all_Orientation.pdf')
	# fig.savefig(f'plots/ScoreGenBarplot_all_Orientation.svg')


def plotScoreGenDistribution(architecture, load=True, orientation_thr=0, exploration_thr=2.0, first_last_games=3):
	REQUIRED = 30
	TURNS = 5
	first_games = first_last_games
	last_games = int(REQUIRED/2)-first_last_games
	first_turns = first_games*TURNS
	last_turns = last_games*TURNS
	players = ["A", "B"]
	groups = ['greedy', 'generous']
	fourgroups = ["Investor\nGreedy", "Investor\nGenerous", "Trustee\nGreedy", "Trustee\nGenerous"]
	fourlabels = ["Investor, Greedy", "Investor, Generous", "Trustee, Greedy", "Trustee, Generous"]
	fournames = ["InvestorGreedy", "InvestorGenerous", "TrusteeGreedy", "TrusteeGenerous"]
	four1 = fourgroups[0]
	four2 = fourgroups[1]
	four3 = fourgroups[2]
	four4 = fourgroups[3]

	if load:
		df =pd.read_pickle(f"plots/plotScoreGenDistribution_{architecture}.pkl")
	else:
		# collect average data about the agent
		dfIn = pd.read_pickle(f"data/runFourGroups_{architecture}.pkl")
		dfsAgent = []
		columns = ('agent', 'group', 'player', 'orientation', 'exploration', 'gamma')
		agents = dfIn['agent'].unique()
		for agent in agents:
			for group in groups:
				for player in players:
					data = dfIn.query("agent==@agent & player==@player & group==@group")
					gens = data['generosity'].to_numpy()
					scores = data['score'].to_numpy()
					# exploration = 'low' if np.std(gens[:first_turns]) < exploration_thr else 'high'
					orientation = "self" if data['rO'].values[0] <= orientation_thr else "social"
					exploration = 'low' if entropy(gens[:first_turns]) < exploration_thr else 'high'
					gamma = data['G'].values[0]
					dfsAgent.append(pd.DataFrame([[agent, group, player, orientation, exploration, gamma]], columns=columns))			
		dfAgent = pd.concat([df for df in dfsAgent], ignore_index=True)
		# create the main dataframe (per-turn score/gen info), appending user data
		columns = ('ID', 'group', 'player', 'fourgroup',
			'game', 'turn', 'score', 'generosity',
			'orientation', 'exploration', 'gamma')
		dfs = []
		for index, row in dfIn.iterrows():
			agent = row['agent']
			group = row['group']
			player = row['player']
			if group=='greedy' and player=='A': fourgroup = "Investor\nGreedy"
			if group=='greedy' and player=='B': fourgroup = "Trustee\nGreedy"
			if group=='generous' and player=='A': fourgroup = "Investor\nGenerous"
			if group=='generous' and player=='B': fourgroup = "Trustee\nGenerous"
			data = dfAgent.query("agent==@agent & group==@group & player==@player")
			orientation = data['orientation'].values[0]
			exploration = data['exploration'].values[0]
			gamma = data['gamma'].values[0]
			newRow = pd.DataFrame([[
				row['agent'], group, player, fourgroup,
				row['game']+1, row['turn'], row['score'], row['generosity'],
				orientation, exploration, gamma
				]], columns=columns)
			dfs.append(newRow)
		df = pd.concat([df for df in dfs], ignore_index=True)
		df.to_pickle(f"plots/plotScoreGenDistribution_{architecture}.pkl")
	dfLast = df.query('game>@last_games')


	# print("ALL")
	# yLimsGen = [((-0.1, 1.1)), ((-0.1, 1.1)), ((-0.1, 0.8)), ((-0.1, 0.6))]
	# yTicksGen = [((0, 1)), ((0, 1)), ((0, 0.6)), ((0, 0.6))]
	# yLimsScore = [((2, 11)), ((6, 16)), ((5, 33)), ((-1.5, 24))]
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
	# fig.savefig(f'plots/ScoreGenDistribution_{architecture}.pdf')
	# fig.savefig(f'plots/ScoreGenDistribution_{architecture}.svg')

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

	yLimsGen = [((-0.1, 1.1)), ((-0.1, 1.1)), ((-0.1, 0.9)), ((-0.1, 0.6))]
	yTicksGen = [((0, 1)), ((0, 1)), ((0, 0.6)), ((0, 0.6))]
	yLimsScore = [((2, 11)), ((6, 16)), ((3, 33)), ((-1.5, 24))]
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
		fig.savefig(f'plots/ScoreGenDistribution_{architecture}_Orientation_{fournames[i]}.pdf')
		fig.savefig(f'plots/ScoreGenDistribution_{architecture}_Orientation_{fournames[i]}.svg')

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
	# fig.savefig(f'plots/ScoreGenBarplot_{architecture}_Orientation.pdf')
	# fig.savefig(f'plots/ScoreGenBarplot_{architecture}_Orientation.svg')


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
	# 	fig.savefig(f'plots/ScoreGenDistribution_{architecture}_Exploration_{fournames[i]}.pdf')
	# 	fig.savefig(f'plots/ScoreGenDistribution_{architecture}_Exploration_{fournames[i]}.svg')


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
	# fig.savefig(f'plots/ScoreGenBarplot_{architecture}_Exploration.pdf')
	# fig.savefig(f'plots/ScoreGenBarplot_{architecture}_Exploration.svg')