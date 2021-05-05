import numpy as np
from agents import *
from experiments import *
from plotter import *

capital = 10
match = 3
turns = 5

avg = 5
rounds = 30
games = 20
seed = np.random.randint(0, 1e6)

nAA = capital+1
nAB = capital*match+1
nS = 10
rO = 0.0
dT = 0.7
EPSILON = 0
SIGMA = 0

# popA = [
	# T4T("A", O=0.8, X=0.5, F=1.0, P=0.2, E=0.0, S=0.0),
	# Bandit("A", nAA),
	# QLearn("A", nAA, nS),
	# Wolf("A", nAA, nS),
	# Hill("A", nAA, nS),
	# ModelBased("A", nAA, nS)
	# ]

# popB = [
# 	T4T("B", O=0.5, X=0.5, F=0.5, P=1.0, E=EPSILON, S=SIGMA),
	# Fixed("B", M=0.5)
	# Bandit("B", nAB),
	# QLearn("B", nAB, nS, rO=0.0, dT=0.7),
	# Wolf("B", nAB, nS),
	# Hill("B", nAB, nS),
	# ModelBased("B", nAB, nS, rO=0.0, dT=0.7)
	# ]

# df = OneVsOne(popA, popB, capital, match, turns, avg, rounds, games, seed)
# df = ManyVsMany(popA, popB, capital, match, turns, avg, rounds, games, seed, "all")
# plotAll(df, popA, popB, capital, match, rounds, turns, "1v1")

# generousA_rl = [
# 	Bandit("A", nAA, rO=rO, dT=dT, ID="Bandit"),
# 	QLearn("A", nAA, nS, rO=rO, dT=dT, ID="QLearn"),
# 	ModelBased("A", nAA, nS, rO=rO, dT=dT, ID="ModelBased"),
# 	]
# generousA_t4t = [T4TV("B", seed=0, minO=0.3, maxO=0.5, minX=0.5, maxX=0.5, minF=0.5, maxF=0.7, minP=1.0, maxP=1.0, E=EPSILON)]
# generousB_rl = [
# 	Bandit("B", nAB, rO=rO, dT=dT, ID="Bandit"),
# 	QLearn("B", nAB, nS, rO=rO, dT=dT, ID="QLearn"),
# 	ModelBased("B", nAB, nS, rO=rO, dT=dT, ID="ModelBased"),
# 	]
# generousB_t4t = [T4TV("A", seed=0, minO=0.5, maxO=0.7, minX=0.5, maxX=0.5, minF=0.8, maxF=1.0, minP=1.0, maxP=1.0, E=EPSILON)]
# greedyA_rl = [
# 	Bandit("A", nAA, rO=rO, dT=dT, ID="Bandit"),
# 	QLearn("A", nAA, nS, rO=rO, dT=dT, ID="QLearn"),
# 	ModelBased("A", nAA, nS, rO=rO, dT=dT, ID="ModelBased"),
# 	]
# greedyA_t4t = [T4TV("B", seed=0, minO=0.2, maxO=0.4, minX=0.5, maxX=0.5, minF=0.0, maxF=0.2, minP=0.2, maxP=0.2, E=EPSILON)]
# greedyB_rl = [
# 	Bandit("B", nAB, rO=rO, dT=dT, ID="Bandit"),
# 	QLearn("B", nAB, nS, rO=rO, dT=dT, ID="QLearn"),
# 	ModelBased("B", nAB, nS, rO=rO, dT=dT, ID="ModelBased"),
# 	]
# greedyB_t4t = [T4TV("A", seed=0, minO=0.8, maxO=1.0, minX=0.5, maxX=0.5, minF=1.0, maxF=1.0, minP=0.1, maxP=0.3, E=EPSILON)]

# df = GreedyAndGenerous(
# 	generousA_rl, generousA_t4t, generousB_rl, generousB_t4t, greedyA_rl, greedyA_t4t, greedyB_rl, greedyB_t4t,
# 	capital, match, turns, avg, rounds, games, seed)
# df.to_pickle("data/GreedyAndGenerous_batch2.pkl")

# dfLoad = pd.read_pickle(f"data/GreedyAndGenerous_batch2.pkl")
# plotGreedyAndGenerous(dfLoad)
# plotGreedyAndGenerous(dfLoad, byAgent=True)

nAgents = 5
rOmin = 0
rOmax = 0.2
dTmin = 0.5
dTmax = 0.8
df = GreedyAndGenerous2(nAgents, nAA, nAB, nS, rOmin, rOmax, dTmin, dTmax, EPSILON, SIGMA,
	capital, match, turns, avg, rounds, games, seed)
df.to_pickle("data/GreedyAndGenerous2_batch2.pkl")

dfLoad = pd.read_pickle(f"data/GreedyAndGenerous2_batch2.pkl")
plotGreedyAndGenerous(dfLoad)
plotGreedyAndGenerous(dfLoad, byAgent=True)

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