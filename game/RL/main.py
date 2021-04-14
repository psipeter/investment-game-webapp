import numpy as np
from agents import *
from experiments import *
from plotter import *

capital = 10
match = 3
turns = 5

avg = 5
rounds = 30
games = 30
seed = np.random.randint(0, 1e6)

nAA = capital+1
nAB = capital*match+1
nS = 10
rO = 0.0
dT = 0.5
EPSILON = 0
SIGMA = 1

popA = [
	# T4T("A", turns, O=0.8, X=0.5, F=1.0, P=0.2, E=0.0, S=0.0),
	# Bandit("A", turns, nAA),
	QLearn("A", turns, nAA, nS),
	# Wolf("A", nAA, nS),
	# Hill("A", nAA, nS),
	# ModelBased("A", turns, nAA, nS)
	]

popB = [
	# T4T("B", turns, O=0.5, X=0.7, F=1.0, P=1.0, E=EPSILON, S=SIGMA),
	Fixed("B", M=0.5)
	# Bandit("B", turns, nAB),
	# QLearn("B", nAB, nS, rO=0.0, dT=0.7),
	# Wolf("B", nAB, nS),
	# Hill("B", nAB, nS),
	# ModelBased("B", nAB, nS, rO=0.0, dT=0.7)
	]

# df = OneVsOne(popA, popB, capital, match, turns, avg, rounds, games, seed)
# plotAll(df, popA, popB, capital, match, rounds, turns, "1v1")
# print(popA[0].Q)

dfs = []
columns = ('agent', 'group', 'player', 'game', 'turn', 'reward', 'generosity')
a1rl = [
	Bandit("A", turns, nAA, rO=rO, dT=dT),
	QLearn("A", turns, nAA, nS, rO=rO, dT=dT),
	ModelBased("A", turns, nAA, nS, rO=rO, dT=dT)
	]
a1t4t = [T4T("B", turns, O=0.5, X=0.7, F=0.2, P=1.0, E=EPSILON, S=SIGMA)]
b1rl = [
	Bandit("B", turns, nAB, rO=rO, dT=dT),
	QLearn("B", turns, nAB, nS, rO=rO, dT=dT),
	ModelBased("B", turns, nAB, nS, rO=rO, dT=dT)
	]
b1t4t = [T4T("A", turns, O=0.5, X=0.5, F=1.0, P=1.0, E=EPSILON, S=SIGMA)]
a2rl = [
	Bandit("A", turns, nAA, rO=rO, dT=dT),
	QLearn("A", turns, nAA, nS, rO=rO, dT=dT),
	ModelBased("A", turns, nAA, nS, rO=rO, dT=dT)
	]
a2t4t = [T4T("B", turns, O=0.3, X=0.7, F=0.1, P=0.2, E=EPSILON, S=SIGMA)]
b2rl = [
	Bandit("B", turns, nAB, rO=rO, dT=dT),
	QLearn("B", turns, nAB, nS, rO=rO, dT=dT),
	ModelBased("B", turns, nAB, nS, rO=rO, dT=dT)
	]
b2t4t = [T4T("A", turns, O=0.8, X=0.5, F=1.0, P=0.2, E=EPSILON, S=SIGMA)]

df = GreedyAndGenerous(a1rl, a1t4t, b1rl, b1t4t, a2rl, a2t4t, b2rl, b2t4t, capital, match, turns, avg, rounds, games, seed)
df.to_pickle("data/GreedyAndGenerous.pkl")
dfLoad = pd.read_pickle(f"data/GreedyAndGenerous.pkl")
print(dfLoad)
plotGreedyAndGenerous(dfLoad)

# for group in ['1', '2']:
# 	for player in ['A', 'B']:
# 		print(group, player)
# 		if group=='1' and player=="A":
# 			popA = [
# 				Bandit("A", turns, nAA, rO=rO, dT=dT),
# 				QLearn("A", turns, nAA, nS, rO=rO, dT=dT),
# 				ModelBased("A", turns, nAA, nS, rO=rO, dT=dT)
# 				]
# 			popB = [
# 				T4T("B", turns, O=0.5, X=0.7, F=0.2, P=1.0, E=EPSILON, S=SIGMA),
# 			]

# 		if group=='1' and player=="B":
# 			popA = [
# 				T4T("A", turns, O=0.5, X=0.5, F=1.0, P=1.0, E=EPSILON, S=SIGMA),
# 			]
# 			popB = [
# 				Bandit("B", turns, nAB, rO=rO, dT=dT),
# 				QLearn("B", turns, nAB, nS, rO=rO, dT=dT),
# 				ModelBased("B", turns, nAB, nS, rO=rO, dT=dT)
# 				]

# 		if group=='2' and player=="A":
# 			popA = [
# 				Bandit("A", turns, nAA, rO=rO, dT=dT),
# 				QLearn("A", turns, nAA, nS, rO=rO, dT=dT),
# 				ModelBased("A", turns, nAA, nS, rO=rO, dT=dT)
# 				]
# 			popB = [
# 				T4T("B", turns, O=0.3, X=0.7, F=0.1, P=0.2, E=EPSILON, S=SIGMA),
# 			]

# 		if group=='2' and player=="B":
# 			popA = [
# 				T4T("A", turns, O=0.8, X=0.5, F=1.0, P=0.2, E=EPSILON, S=SIGMA),
# 			]
# 			popB = [
# 				Bandit("B", turns, nAB, rO=rO, dT=dT),
# 				QLearn("B", turns, nAB, nS, rO=rO, dT=dT),
# 				ModelBased("B", turns, nAB, nS, rO=rO, dT=dT)
# 				]
# 		df = ManyVsMany(popA, popB, capital, match, turns, avg, rounds, games, seed, "all")
# 		plotAll(df, popA, popB, capital, match, rounds, turns, f"{group}{player}")

# for agent in popB:
# 	agent.saveArchive(f'{agent.ID}_{player}_{group}')
# 	plotPolicy(f"{agent.ID}_{player}_{group}.npz", agent.ID, player, group, nS, nAB)

# FAs = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25]
# PAs = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
# MAs = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25]
# rOBs = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25]
# for agent in ['Bandit', 'QLearn', 'ModelBased']:
# 	for dependent in ['Forgiveness', 'Punishment', 'Magnitude']:
# 		print(f"{agent}, {dependent}")
# 		if dependent == "Forgiveness":
# 			T4TAs = [T4T("A", F=F) for F in FAs]
# 		if dependent == "Punishment":
# 			T4TAs = [T4T("A", P=P) for P in PAs]
# 		if dependent == "Magnitude":
# 			T4TAs = [T4T("A", F=M, P=M) for M in MAs]
# 		if agent == "Bandit":
# 			rlBs = [Bandit("B", nAB, rO=rO) for rO in rOBs]
# 		elif agent == "QLearn":
# 			rlBs = [QLearn("B", nAB, nS, rO=rO) for rO in rOBs]
# 		elif agent == "ModelBased":
# 			rlBs = [ModelBased("B", nAB, nS, rO=rO) for rO in rOBs]
# 		df = XFriendliness(T4TAs, rlBs, capital, match, turns, avg, rounds, games, seed, dependent)
# 		df.to_pickle(f"data/{agent}{dependent}Friendliness2.pkl")
# 		dfLoad = pd.read_pickle(f"data/{agent}{dependent}Friendliness2.pkl")
# 		print(dfLoad)
# 		plotXFriendliness(dfLoad, capital, match, agent, dependent)

# dependent = "Friendliness"
# rOAs = [0.0, 0.25, 0.5, 0.75, 1.0]
# rOBs = [0.0, 0.25, 0.5, 0.75, 1.0]
# for agentA in ['Bandit', 'QLearn', 'ModelBased']:
# 	for agentB in ['Bandit', 'QLearn', 'ModelBased']:
# 		print(f"{agentA} vs {agentB}")
# 		if agentA == "Bandit":
# 			rlAs = [Bandit("A", nAA, rO=rO) for rO in rOAs]
# 		elif agentA == "QLearn":
# 			rlAs = [QLearn("A", nAA, nS, rO=rO) for rO in rOAs]
# 		elif agentA == "ModelBased":
# 			rlAs = [ModelBased("A", nAA, nS, rO=rO) for rO in rOAs]
# 		if agentB == "Bandit":
# 			rlBs = [Bandit("B", nAB, rO=rO) for rO in rOBs]
# 		elif agentB == "QLearn":
# 			rlBs = [QLearn("B", nAB, nS, rO=rO) for rO in rOBs]
# 		elif agentB == "ModelBased":
# 			rlBs = [ModelBased("B", nAB, nS, rO=rO) for rO in rOBs]
# 		df = FriendlinessFriendliness(rlAs, rlBs, capital, match, turns, avg, rounds, games, seed)
# 		df.to_pickle(f"data/{agentA}{agentB}Friendliness.pkl")
# 		dfLoad = pd.read_pickle(f"data/{agentA}{agentB}Friendliness.pkl")
# 		print(dfLoad)
# 		plotXFriendliness(dfLoad, capital, match, agentA, dependent, agentB)