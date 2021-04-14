import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import time
from scipy.special import softmax


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

def plotGreedyAndGenerous(df):
	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((16,16)))
	dfGenerousA = df.query("group == 'generous' & player == 'A'")
	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
	dfGenerousB = df.query("group == 'generous' & player == 'B'")
	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
	sns.lineplot(data=dfGenerousA, x='game', y='generosity', hue='agent', ax=ax)
	sns.lineplot(data=dfGreedyA, x='game', y='generosity', hue='agent', ax=ax2)
	sns.lineplot(data=dfGenerousB, x='game', y='generosity', hue='agent', ax=ax3)
	sns.lineplot(data=dfGreedyB, x='game', y='generosity', hue='agent', ax=ax4)
	ax.set(title="Learn to be Generous, Investor", ylabel='Generosity', xlabel="", ylim=((0, 1)))
	ax2.set(title="Learn to be Greedy, Investor", xlabel="", ylim=((0, 1)))
	ax3.set(title="Learn to be Generous, Trustee", xlabel='Game', ylabel='Generosity', ylim=((0, 1)))
	ax4.set(title="Learn to be Greedy, Trustee", xlabel='Game', ylim=((0, 1)))
	fig.savefig("plots/Generosity_vs_Time.pdf")

	fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=((16,16)))
	dfGenerousA = df.query("group == 'generous' & player == 'A'")
	dfGreedyA = df.query("group == 'greedy' & player == 'A'")
	dfGenerousB = df.query("group == 'generous' & player == 'B'")
	dfGreedyB = df.query("group == 'greedy' & player == 'B'")
	sns.lineplot(data=dfGenerousA, x='game', y='reward', hue='agent', ax=ax)
	sns.lineplot(data=dfGreedyA, x='game', y='reward', hue='agent', ax=ax2)
	sns.lineplot(data=dfGenerousB, x='game', y='reward', hue='agent', ax=ax3)
	sns.lineplot(data=dfGreedyB, x='game', y='reward', hue='agent', ax=ax4)
	ax.set(title="Learn to be Generous, Investor", ylabel='Score', xlabel="", ylim=((0, 30)))
	ax2.set(title="Learn to be Greedy, Investor", xlabel="", ylim=((0, 30)))
	ax3.set(title="Learn to be Generous, Trustee", xlabel='Game', ylabel='Score', ylim=((0, 30)))
	ax4.set(title="Learn to be Greedy, Trustee", xlabel='Game', ylim=((0, 30)))
	fig.savefig("plots/Score_vs_Time.pdf")
