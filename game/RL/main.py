import numpy as np
from agents import *
from experiments import *
from plotter import *

capital = 10
match = 3
turns = 5

avg = 10
rounds = 100
games = 10
seed = np.random.randint(0, 1e6)

nAA = capital+1
nAB = capital*match+1
nS = 10

FA = 0.5
PA = 0.5
FB = 0.5
PB = 0.5

popA = [
	Fixed("A", M=0.5),
	Fixed("A", M=0.8),
	T4T("A", X=0.2, F=FA, P=PA),
	T4T("A", X=0.4, F=FA, P=PA),
	# T4T("A", X=0.4, F=FA, P=PA),
	# T4T("A", X=0.6, F=FA, P=PA),
	# Bandit("A", nAA, rO=rOA),
	# QLearn("A", nAA, nS, rO=rOA),
	# Wolf("A", nAA, nS),
	# Hill("A", nAA, nS),
	# ModelBased("A", nAA, nS)
	]

popB = [
	# T4T("B", F=FB, ID=str(FB)),
	# Bandit("B", nAB, rO=0.3, dT=0.9),
	# QLearn("B", nAB, nS, rO=0.3, dT=0.9),
	# Wolf("B", nAB, nS),
	# Hill("B", nAB, nS),
	ModelBased("B", nAB, nS, rO=0.3, dT=0.9)
	]

# df = OneVsOne(popA, popB, capital, match, turns, avg, rounds, games, seed)
# plotAll(df, popA, popB, capital, match, rounds, "1v1")

df = ManyVsMany(popA, popB, capital, match, turns, avg, rounds, games, seed, "all")
plotAll(df, popA, popB, capital, match, rounds, f"{popB[0].ID}_B_vs_2")
popB[0].saveArchive(f'{popB[0].ID}_B_2')

plotPolicy(f"{popB[0].ID}_B_2.npz", popB[0].ID, "B", "2", nS, nAB)

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