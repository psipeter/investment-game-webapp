import numpy as np
import random
import pandas as pd
from scipy import stats
from sklearn.neighbors import KernelDensity
from agents import *
from plotter import *

class Game():
	def __init__(self, A, B, capital, match, turns):
		self.A = A
		self.B = B
		assert self.A.player == "A", "player A not set"
		assert self.B.player == "B", "player B not set"
		self.capital = capital
		self.match = match
		self.turns = turns
		self.history = {
			'aGives': [],
			'aKeeps': [],
			'aGen': [],
			'aRewards': [],
			'aStates': [],
			'bGives': [],
			'bKeeps': [],
			'bGen': [],
			'bRewards': [],
			'bStates': [],
		}
	def play(self):
		self.A.reset()
		self.B.reset()
		for t in range(self.turns):
			aGive, aKeep = self.A.act(self.capital, self.history)
			self.history['aGives'].append(aGive)
			self.history['aKeeps'].append(aKeep)
			self.history['aGen'].append(aGive/(aGive+aKeep))
			self.history['aStates'].append(self.A.state)
			bGive, bKeep = self.B.act(aGive*self.match, self.history)
			self.history['bGives'].append(bGive)
			self.history['bKeeps'].append(bKeep)
			# self.history['bGen'].append(np.NaN if (bGive+bKeep)==0 else bGive/(bGive+bKeep))
			self.history['bGen'].append(0 if (bGive+bKeep)==0 else bGive/(bGive+bKeep))
			self.history['bStates'].append(self.B.state)
			self.history['aRewards'].append(aKeep+bGive)
			self.history['bRewards'].append(bKeep)
	def historyToDataframe(self, game):
		columns = ('A', 'B', 'game', 'turn',
			'aGives', 'aKeeps', 'aGen', 'aRewards', 'aStates', 'aScore',
			'bGives', 'bKeeps', 'bGen', 'bRewards', 'bStates', 'bScore')
		dfs = []
		for t in range(self.turns):
			dfs.append(pd.DataFrame([[
				self.A.ID,
				self.B.ID,
				game,
				t,
				self.history['aGives'][t],
				self.history['aKeeps'][t],
				self.history['aGen'][t],
				self.history['aRewards'][t],
				self.history['aStates'][t],
				np.mean(self.history['aRewards']),
				self.history['bGives'][t],
				self.history['bKeeps'][t],
				self.history['bGen'][t],
				self.history['bRewards'][t],
				self.history['bStates'][t],
				np.mean(self.history['bRewards']),
			]], columns=columns))
		df = pd.concat([df for df in dfs], ignore_index=True)
		return df


def OneVsOne(popA, popB, capital, match, turns, avg, rounds, games, seed):
	np.random.seed(seed)
	dfAll = []
	for A in popA:
		for B in popB:
			dfs = []
			for a in range(avg):
				print(f'{A.ID} vs {B.ID}: avg {a}')
				A.restart()
				B.restart()
				for r in range(rounds):
					histories = []
					for g in range(games):
						A.reset()
						B.reset()
						G = Game(A, B, capital, match, turns)
						G.play()
						dfs.append(G.historyToDataframe(r))
						histories.append({'A': A, 'B': B, 'hist': G.history})
					np.random.shuffle(histories)
					for hist in histories:
						hist['A'].learn(hist['hist'])
						hist['B'].learn(hist['hist'])
					A.reduceExploration(r)
					B.reduceExploration(r)
			df = pd.concat([df for df in dfs], ignore_index=True)
			dfAll.append(df)
	dfAll = pd.concat([df for df in dfAll], ignore_index=True)
	return dfAll

def ManyVsMany(popA, popB, capital, match, turns, avg, rounds, games, seed, name):
	np.random.seed(seed)
	dfs = []
	for a in range(avg):
		print(f'avg {a}')
		for A in popA:
			A.restart()
		for B in popB:
			B.restart()
		for r in range(rounds):
			np.random.shuffle(popA)
			np.random.shuffle(popB)
			histories = []
			for A in popA:
				for B in popB:
					for g in range(games):
						A.reset()
						B.reset()
						G = Game(A, B, capital, match, turns)
						G.play()
						dfs.append(G.historyToDataframe(r))
						histories.append({'A': A, 'B': B, 'hist': G.history})
			# batch learning
			np.random.shuffle(histories)
			for hist in histories:
				hist['A'].learn(hist['hist'])
				hist['B'].learn(hist['hist'])
			for A in popA:
				A.reduceExploration(r)
			for B in popB:
				B.reduceExploration(r)
	dfAll = pd.concat([df for df in dfs], ignore_index=True)
	return dfAll

def XFriendliness(T4TAs, rlBs, capital, match, turns, avg, rounds, games, seed, dependent, endgames=5):
	end = rounds - endgames
	dfsAll = []
	if dependent == "Forgiveness":
		DV = 'F'
	if dependent == "Punishment":
		DV = 'P'
	if dependent == "Magnitude":
		DV = 'M'
	columns = (DV, 'rO', 'meanA', 'meanB', 'stdA', 'stdB')
	for t4t in T4TAs:
		for rl in rlBs:
			dfs = []
			for a in range(avg):
				print(f'{t4t.ID} F={t4t.F}, P={t4t.P} and {rl.ID} rO={rl.rO}, avg {a}')
				rl.restart()
				for r in range(rounds):
					histories = []
					for g in range(games):
						t4t.reset()
						rl.reset()
						G = Game(t4t, rl, capital, match, turns)
						G.play()
						dfs.append(G.historyToDataframe(r))
						histories.append({'A': t4t, 'B': rl, 'hist': G.history})
					np.random.shuffle(histories)
					for hist in histories:
						hist['A'].learn(hist['hist'])
						hist['B'].learn(hist['hist'])
					rl.reduceExploration(r)
			data = pd.concat([df for df in dfs], ignore_index=True)
			dataEnd = data.query("game >= @end")
			meanA = np.mean(dataEnd['aScore'])
			meanB = np.mean(dataEnd['bScore'])
			stdA = np.std(dataEnd['aScore'])
			stdB = np.std(dataEnd['bScore'])
			if dependent == "Forgiveness":
				DV = t4t.F
			if dependent == "Punishment":
				DV = t4t.P
			if dependent == "Magnitude":
				DV = t4t.F
			dfsAll.append(pd.DataFrame([[DV, rl.rO, meanA, meanB, stdA, stdB]], columns=columns))
	dfFinal = pd.concat([df for df in dfsAll], ignore_index=True)
	return dfFinal



def FriendlinessFriendliness(rlAs, rlBs, capital, match, turns, avg, rounds, games, seed, endgames=5):
	end = rounds - endgames
	dfsAll = []
	columns = ('rOA', 'rOB', 'meanA', 'meanB', 'stdA', 'stdB')
	for rlA in rlAs:
		for rlB in rlBs:
			dfs = []
			for a in range(avg):
				print(f'{rlA.ID} rO={rlA.rO} and {rlB.ID} rO={rlB.rO}, avg {a}')
				rlA.restart()
				rlB.restart()
				for r in range(rounds):
					histories = []
					for g in range(games):
						rlA.reset()
						rlB.reset()
						G = Game(rlA, rlB, capital, match, turns)
						G.play()
						dfs.append(G.historyToDataframe(r))
						histories.append({'A': rlA, 'B': rlB, 'hist': G.history})
					np.random.shuffle(histories)
					for hist in histories:
						hist['A'].learn(hist['hist'])
						hist['B'].learn(hist['hist'])
					rlA.reduceExploration(r)
					rlB.reduceExploration(r)
			data = pd.concat([df for df in dfs], ignore_index=True)
			dataEnd = data.query("game >= @end")
			meanA = np.mean(dataEnd['aScore'])
			meanB = np.mean(dataEnd['bScore'])
			stdA = np.std(dataEnd['aScore'])
			stdB = np.std(dataEnd['bScore'])
			dfsAll.append(pd.DataFrame([[rlA.rO, rlB.rO, meanA, meanB, stdA, stdB]], columns=columns))
	dfFinal = pd.concat([df for df in dfsAll], ignore_index=True)
	return dfFinal

def GreedyAndGenerous(a1rl, a1t4t, b1rl, b1t4t, a2rl, a2t4t, b2rl, b2t4t, capital, match, turns, avg, rounds, games, seed):
	np.random.seed(seed)
	dfs = []
	columns = ('agent', 'group', 'player', 'game', 'turn', 'reward', 'generosity')
	for group in ['1', '2']:
		for player in ['A', 'B']:
			if group=='1' and player=='A':
				popA = a1rl
				popB = a1t4t
			if group=='1' and player=='B':
				popB = b1rl
				popA = b1t4t
			if group=='2' and player=='A':
				popA = a2rl
				popB = a2t4t
			if group=='2' and player=='B':
				popB = b2rl
				popA = b2t4t				
			for a in range(avg):
				print(f'avg {a}')
				for A in popA:
					A.restart()
				for B in popB:
					B.restart()
				for r in range(rounds):
					np.random.shuffle(popA)
					np.random.shuffle(popB)
					histories = []
					for A in popA:
						for B in popB:
							for g in range(games):
								A.reset()
								B.reset()
								G = Game(A, B, capital, match, turns)
								G.play()
								for t in range(turns-1):  # don't include final move
									gen = G.history['aGen'][t] if player=='A' else G.history['bGen'][t]
									# if player=="B" and t==turns-2: gen = np.NaN  # exclude B's final greedy move
									reward = G.history['aRewards'][t] if player=='A' else G.history['bRewards'][t]
									dfs.append(pd.DataFrame([[
										A.ID if player=='A' else B.ID,
										"generous" if group=='1' else "greedy",
										player,
										r,
										t,
										reward,
										gen
									]], columns=columns))
								histories.append({'A': A, 'B': B, 'hist': G.history})
					# batch learning
					np.random.shuffle(histories)
					for hist in histories:
						hist['A'].learn(hist['hist'])
						hist['B'].learn(hist['hist'])
					for A in popA:
						A.reduceExploration(r)
					for B in popB:
						B.reduceExploration(r)
	dfAll = pd.concat([df for df in dfs], ignore_index=True)
	return dfAll

def GreedyAndGenerous2(nAgents, nAA, nAB, nS, rOmin, rOmax, dTmin, dTmax, epsilon, sigma, capital, match, turns, avg, rounds, games, seed):
	np.random.seed(seed)
	generousA = []
	greedyA = []
	generousB = []
	greedyB = []
	for n in range(nAgents):
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		generousA.append(Bandit("A", nAA, rO=rO, dT=dT, ID=f"Bandit rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		generousA.append(QLearn("A", nAA, nS, rO=rO, dT=dT, ID=f"QLearn rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		generousA.append(ModelBased("A", nAA, nS, rO=rO, dT=dT, ID=f"ModelBased rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		greedyA.append(Bandit("A", nAA, rO=rO, dT=dT, ID=f"Bandit rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		greedyA.append(QLearn("A", nAA, nS, rO=rO, dT=dT, ID=f"QLearn rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		greedyA.append(ModelBased("A", nAA, nS, rO=rO, dT=dT, ID=f"ModelBased rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		generousB.append(Bandit("B", nAB, rO=rO, dT=dT, ID=f"Bandit rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		generousB.append(QLearn("B", nAB, nS, rO=rO, dT=dT, ID=f"QLearn rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		generousB.append(ModelBased("B", nAB, nS, rO=rO, dT=dT, ID=f"ModelBased rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		greedyB.append(Bandit("B", nAB, rO=rO, dT=dT, ID=f"Bandit rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		greedyB.append(QLearn("B", nAB, nS, rO=rO, dT=dT, ID=f"QLearn rO={rO} dT={dT}"))
		rO, dT = np.around(np.random.uniform(rOmin, rOmax), decimals=2), np.around(np.random.uniform(dTmin, dTmax), decimals=2)
		greedyB.append(ModelBased("B", nAB, nS, rO=rO, dT=dT, ID=f"ModelBased rO={rO} dT={dT}"))		
	dfs = []
	columns = ('agent', 'group', 'player', 'game', 'turn', 'reward', 'generosity')
	for group in ['greedy', 'generous']:
		for player in ['A', 'B']:
			if group=='generous' and player=='A':
				popA = generousA
			if group=='generous' and player=='B':
				popB = generousB
			if group=='greedy' and player=='A':
				popA = greedyA
			if group=='greedy' and player=='B':
				popB = greedyB
			for a in range(avg):
				print(f'avg {a}')
				if group=='generous' and player=='A':
					popB = [T4TV("B", seed=a, minO=0.3, maxO=0.5, minX=0.5, maxX=0.5, minF=0.4, maxF=0.6, minP=1.0, maxP=1.0, E=epsilon)]
				if group=='generous' and player=='B':
					popA = [T4TV("A", seed=a, minO=0.6, maxO=0.8, minX=0.5, maxX=0.5, minF=0.8, maxF=1.0, minP=1.0, maxP=1.0, E=epsilon)]
				if group=='greedy' and player=='A':
					popB = [T4TV("B", seed=a, minO=0.1, maxO=0.3, minX=0.5, maxX=0.5, minF=0.0, maxF=0.1, minP=0.2, maxP=0.2, E=epsilon)]
				if group=='greedy' and player=='B':
					popA = [T4TV("A", seed=a, minO=0.8, maxO=1.0, minX=0.5, maxX=0.5, minF=1.0, maxF=1.0, minP=0.1, maxP=0.3, E=epsilon)]
				for A in popA:
					A.restart()
				for B in popB:
					B.restart()
				for r in range(rounds):
					np.random.shuffle(popA)
					np.random.shuffle(popB)
					histories = []
					for A in popA:
						for B in popB:
							for g in range(games):
								A.reset()
								B.reset()
								G = Game(A, B, capital, match, turns)
								G.play()
								for t in range(turns):
									gen = G.history['aGen'][t] if player=='A' else G.history['bGen'][t]
									reward = G.history['aRewards'][t] if player=='A' else G.history['bRewards'][t]
									dfs.append(pd.DataFrame([[
										A.ID if player=='A' else B.ID, group, player, r, t, reward, gen
									]], columns=columns))
								histories.append({'A': A, 'B': B, 'hist': G.history})
					# batch learning
					np.random.shuffle(histories)
					for hist in histories:
						hist['A'].learn(hist['hist'])
						hist['B'].learn(hist['hist'])
					for A in popA:
						A.reduceExploration(r)
					for B in popB:
						B.reduceExploration(r)
	dfAll = pd.concat([df for df in dfs], ignore_index=True)
	return dfAll


def Batch3(nAgents, nAA, nAB, nS, rOmin, rOmax, dTmin, dTmax, Gmin, Gmax, capital, match, turns, rounds, games, seed, agents, altruism_threshold=0.3):
	np.random.seed(seed)
	generousA = []
	greedyA = []
	generousB = []
	greedyB = []
	rOs = np.around(np.random.uniform(rOmin, rOmax, size=nAgents*12), decimals=2)
	dTs = np.around(np.random.uniform(dTmin, dTmax, size=nAgents*12), decimals=2)
	Gs = np.around(np.random.uniform(Gmin, Gmax, size=nAgents*12), decimals=2)
	for n in range(nAgents):
		if 'bandit' in agents:
			generousA.append(Bandit("A", nAA, rO=rOs[n], dT=dTs[n], ID=f"Bandit rO={rOs[n]} dT={dTs[n]}"))
			greedyA.append(Bandit("A", nAA, rO=rOs[n+1], dT=dTs[n+1], ID=f"Bandit rO={rOs[n+1]} dT={dTs[n+1]}"))
			generousB.append(Bandit("B", nAB, rO=rOs[n+2], dT=dTs[n+2], ID=f"Bandit rO={rOs[n+2]} dT={dTs[n+2]}"))
			greedyB.append(Bandit("B", nAB, rO=rOs[n+3], dT=dTs[n+3], ID=f"Bandit rO={rOs[n+3]} dT={dTs[n+3]}"))
		if 'qlearn' in agents:
			generousA.append(QLearn("A", nAA, nS, rO=rOs[n+4], dT=dTs[n+4], G=Gs[n+4], ID=f"QLearn rO={rOs[n+4]} dT={dTs[n+4]}, G={Gs[n+4]}"))
			greedyA.append(QLearn("A", nAA, nS, rO=rOs[n+6], dT=dTs[n+6], G=Gs[n+6], ID=f"QLearn rO={rOs[n+6]} dT={dTs[n+6]}, G={Gs[n+6]}"))
			generousB.append(QLearn("B", nAB, nS, rO=rOs[n+8], dT=dTs[n+8], G=Gs[n+8], ID=f"QLearn rO={rOs[n+8]} dT={dTs[n+8]}, G={Gs[n+8]}"))
			greedyB.append(QLearn("B", nAB, nS, rO=rOs[n+10], dT=dTs[n+10], G=Gs[n+10], ID=f"QLearn rO={rOs[n+10]} dT={dTs[n+10]}, G={Gs[n+10]}"))
		if 'modelbased' in agents:
			generousA.append(ModelBased("A", nAA, nS, rO=rOs[n+5], dT=dTs[n+5], G=Gs[n+5], ID=f"ModelBased rO={rOs[n+5]} dT={dTs[n+5]}, G={Gs[n+5]}"))
			greedyA.append(ModelBased("A", nAA, nS, rO=rOs[n+7], dT=dTs[n+7], G=Gs[n+7], ID=f"ModelBased rO={rOs[n+7]} dT={dTs[n+7]}, G={Gs[n+7]}"))
			generousB.append(ModelBased("B", nAB, nS, rO=rOs[n+9], dT=dTs[n+9], G=Gs[n+9], ID=f"ModelBased rO={rOs[n+9]} dT={dTs[n+9]}, G={Gs[n+9]}"))
			greedyB.append(ModelBased("B", nAB, nS, rO=rOs[n+11], dT=dTs[n+11], G=Gs[n+11], ID=f"ModelBased rO={rOs[n+11]} dT={dTs[n+11]}, G={Gs[n+11]}"))		

	dfs = []
	columns = ('agent', 'group', 'player', 'altruism', 'exploration', 'game', 'turn', 'reward', 'generosity')
	for group in ['greedy', 'generous']:
		for player in ['A', 'B']:
			if group=='generous' and player=='A':
				popA = generousA
				for A in popA:
					A.restart()
			if group=='generous' and player=='B':
				popB = generousB
				for B in popB:
					B.restart()
			if group=='greedy' and player=='A':
				popA = greedyA
				for A in popA:
					A.restart()
			if group=='greedy' and player=='B':
				popB = greedyB
				for B in popB:
					B.restart()
			for r in range(rounds):
				print(f"Round {r}")
				if group=='generous' and player=='A':
					popB = [T4TV("B", seed=r, minO=0.3, maxO=0.5, minX=0.5, maxX=0.5, minF=0.4, maxF=0.6, minP=1.0, maxP=1.0)]
					for B in popB:
						B.restart()
				if group=='generous' and player=='B':
					popA = [T4TV("A", seed=r, minO=0.6, maxO=0.8, minX=0.5, maxX=0.5, minF=0.8, maxF=1.0, minP=1.0, maxP=1.0)]
					for A in popA:
						A.restart()
				if group=='greedy' and player=='A':
					popB = [T4TV("B", seed=r, minO=0.1, maxO=0.3, minX=0.5, maxX=0.5, minF=0.0, maxF=0.1, minP=0.2, maxP=0.2)]
					for B in popB:
						B.restart()
				if group=='greedy' and player=='B':
					popA = [T4TV("A", seed=r, minO=0.8, maxO=1.0, minX=0.5, maxX=0.5, minF=1.0, maxF=1.0, minP=0.1, maxP=0.3)]
					for A in popA:
						A.restart()
				histories = []
				for A in popA:
					for B in popB:
						for g in range(games):
							A.reset()
							B.reset()
							G = Game(A, B, capital, match, turns)
							G.play()
							# altruism = A.rO if player=='A' else B.rO
							if player=='A':
								altruism = 'equal' if A.rO > altruism_threshold else 'self'
							else:
								altruism = 'equal' if B.rO > altruism_threshold else 'self'								
							exploration = A.dT if player=='A' else B.dT
							for t in range(turns):
								gen = G.history['aGen'][t] if player=='A' else G.history['bGen'][t]
								reward = G.history['aRewards'][t] if player=='A' else G.history['bRewards'][t]
								dfs.append(pd.DataFrame([[
									A.ID if player=='A' else B.ID, group, player, altruism, exploration, r, t, reward, gen
								]], columns=columns))
							histories.append({'A': A, 'B': B, 'hist': G.history})
				# batch learning
				np.random.shuffle(histories)
				for hist in histories:
					hist['A'].learn(hist['hist'])
					hist['B'].learn(hist['hist'])
				for A in popA:
					A.reduceExploration(r)
				for B in popB:
					B.reduceExploration(r)
	dfAll = pd.concat([df for df in dfs], ignore_index=True)
	return dfAll



def Single(nAgents, nAA, nAB, nS, rOmin, rOmax, dEmin, dEmax, Gmin, Gmax, capital, match, turns, rounds, games, seed, types, group):
	np.random.seed(seed)
	agents = []
	rOsFriendly = np.around(np.random.uniform(rOmin, rOmax, size=nAgents*12), decimals=3)
	rOs = [0 if np.random.randint(2)==0 else rOsFriendly[i] for i in range(nAgents*12)]
	dEs = np.around(np.random.uniform(dEmin, dEmax, size=nAgents*12), decimals=3)
	Gs = np.around(np.random.uniform(Gmin, Gmax, size=nAgents*12), decimals=3)
	for n in range(nAgents):
		if 'bandit' in types:
			if group=="InvestorGenerous":
				agents.append(Bandit("A", nAA, rO=rOs[n], dE=dEs[n], ID=f"Bandit rO={rOs[n]} dE={dEs[n]}"))
			if group=="InvestorGreedy":
				agents.append(Bandit("A", nAA, rO=rOs[n+1], dE=dEs[n+1], ID=f"Bandit rO={rOs[n+1]} dE={dEs[n+1]}"))
			if group=="TrusteeGenerous":
				agents.append(Bandit("B", nAB, rO=rOs[n+2], dE=dEs[n+2], ID=f"Bandit rO={rOs[n+2]} dE={dEs[n+2]}"))
			if group=="TrusteeGreedy":
				agents.append(Bandit("B", nAB, rO=rOs[n+3], dE=dEs[n+3], ID=f"Bandit rO={rOs[n+3]} dE={dEs[n+3]}"))
		if 'qlearn' in types:
			if group=="InvestorGenerous":
				agents.append(QLearn("A", nAA, nS, rO=rOs[n+4], dE=dEs[n+4], G=Gs[n+4], ID=f"QLearn rO={rOs[n+4]} dE={dEs[n+4]}, G={Gs[n+4]}"))
			if group=="InvestorGreedy":
				agents.append(QLearn("A", nAA, nS, rO=rOs[n+6], dE=dEs[n+6], G=Gs[n+6], ID=f"QLearn rO={rOs[n+6]} dE={dEs[n+6]}, G={Gs[n+6]}"))
			if group=="TrusteeGenerous":
				agents.append(QLearn("B", nAB, nS, rO=rOs[n+8], dE=dEs[n+8], G=Gs[n+8], ID=f"QLearn rO={rOs[n+8]} dE={dEs[n+8]}, G={Gs[n+8]}"))
			if group=="TrusteeGreedy":
				agents.append(QLearn("B", nAB, nS, rO=rOs[n+10], dE=dEs[n+10], G=Gs[n+10], ID=f"QLearn rO={rOs[n+10]} dE={dEs[n+10]}, G={Gs[n+10]}"))
		if 'modelbased' in types:
			if group=="InvestorGenerous":
				agents.append(ModelBased("A", nAA, nS, rO=rOs[n+5], dE=dEs[n+5], G=Gs[n+5], ID=f"ModelBased rO={rOs[n+5]} dE={dEs[n+5]}, G={Gs[n+5]}"))
			if group=="InvestorGreedy":
				agents.append(ModelBased("A", nAA, nS, rO=rOs[n+7], dE=dEs[n+7], G=Gs[n+7], ID=f"ModelBased rO={rOs[n+7]} dE={dEs[n+7]}, G={Gs[n+7]}"))
			if group=="TrusteeGenerous":
				agents.append(ModelBased("B", nAB, nS, rO=rOs[n+9], dE=dEs[n+9], G=Gs[n+9], ID=f"ModelBased rO={rOs[n+9]} dE={dEs[n+9]}, G={Gs[n+9]}"))
			if group=="TrusteeGreedy":
				agents.append(ModelBased("B", nAB, nS, rO=rOs[n+11], dE=dEs[n+11], G=Gs[n+11], ID=f"ModelBased rO={rOs[n+11]} dE={dEs[n+11]}, G={Gs[n+11]}"))		

	dfs = []
	columns = ('agent', 'game', 'turn', 'reward', 'generosity', 'rO', 'dE', 'G')
	if group=='InvestorGenerous':
		popA = agents
		for A in popA: A.restart()
	if group=='TrusteeGenerous':
		popB = agents
		for B in popB: B.restart()
	if group=='InvestorGreedy':
		popA = agents
		for A in popA: A.restart()
	if group=='TrusteeGreedy':
		popB = agents
		for B in popB: B.restart()
	for r in range(rounds):
		print(f"Round {r}")
		if group=='InvestorGenerous':
			popB = [T4TV("B", seed=r, minO=0.3, maxO=0.5, minX=0.5, maxX=0.5, minF=0.4, maxF=0.6, minP=1.0, maxP=1.0)]
			for B in popB: B.restart()
		if group=='TrusteeGenerous':
			popA = [T4TV("A", seed=r, minO=0.6, maxO=0.8, minX=0.5, maxX=0.5, minF=0.8, maxF=1.0, minP=1.0, maxP=1.0)]
			for A in popA: A.restart()
		if group=='InvestorGreedy':
			popB = [T4TV("B", seed=r, minO=0.1, maxO=0.3, minX=0.5, maxX=0.5, minF=0.0, maxF=0.1, minP=0.2, maxP=0.2)]
			for B in popB: B.restart()
		if group=='TrusteeGreedy':
			popA = [T4TV("A", seed=r, minO=0.8, maxO=1.0, minX=0.5, maxX=0.5, minF=1.0, maxF=1.0, minP=0.1, maxP=0.3)]
			for A in popA: A.restart()
		histories = []
		for A in popA:
			for B in popB:
				for g in range(games):
					A.reset()
					B.reset()
					G = Game(A, B, capital, match, turns)
					G.play()
					for t in range(turns):
						name = A.ID if (group=='InvestorGenerous' or group=="InvestorGreedy") else B.ID
						gen = G.history['aGen'][t] if (group=='InvestorGenerous' or group=="InvestorGreedy") else G.history['bGen'][t]
						reward = G.history['aRewards'][t] if (group=='InvestorGenerous' or group=="InvestorGreedy") else G.history['bRewards'][t]
						ro = A.rO if (group=='InvestorGenerous' or group=="InvestorGreedy") else B.rO
						de = A.dE if (group=='InvestorGenerous' or group=="InvestorGreedy") else B.dE
						gamma = A.G if (group=='InvestorGenerous' or group=="InvestorGreedy") else B.G
						dfs.append(pd.DataFrame([[name, r, t, reward, gen, ro, de, gamma]], columns=columns))
					histories.append({'A': A, 'B': B, 'hist': G.history})
		# batch learning
		np.random.shuffle(histories)
		for hist in histories:
			hist['A'].learn(hist['hist'])
			hist['B'].learn(hist['hist'])
		for A in popA:
			A.reduceExploration(r)
		for B in popB:
			B.reduceExploration(r)
	dfAll = pd.concat([df for df in dfs], ignore_index=True)
	dfAll.to_pickle(f"data/{group}.pkl")
	return dfAll


def HumanVsAgentKDE(group, xmin=0, xmax=15, ymin=0, ymax=30):
	dfAgent = pd.read_pickle(f"data/{group}.pkl")
	if group=="InvestorGreedy":
		dfHuman = pd.read_pickle(f"data/human.pkl").query("group=='greedy' & player=='Investor'")
	if group=="TrusteeGreedy":
		dfHuman = pd.read_pickle(f"data/human.pkl").query("group=='greedy' & player=='Trustee'")
	if group=="InvestorGenerous":
		dfHuman = pd.read_pickle(f"data/human.pkl").query("group=='generous' & player=='Investor'")
	if group=="TrusteeGenerous":
		dfHuman = pd.read_pickle(f"data/human.pkl").query("group=='generous' & player=='Trustee'")

	# print(dfHuman)
	# scoreHuman = dfHuman.drop(['user', 'group', 'player', 'turn', 'generosity', 'compensation', 'objective', 'selfLearning', 'otherIdentity', 'otherStrategy', 'otherNumber', 'empathy', 'risk', 'altruism'], axis=1).to_numpy()
	# genHuman = dfHuman.drop(['user', 'group', 'player', 'turn', 'reward', 'compensation', 'objective', 'selfLearning', 'otherIdentity', 'otherStrategy', 'otherNumber', 'empathy', 'risk', 'altruism'], axis=1).to_numpy()
	# print(scoreHuman.shape)
	# print(genHuman.shape)

	# 1D sample
	# scoreHuman = dfHuman['reward'].to_numpy().reshape(-1, 1)
	# print(scoreHuman.shape)
	# kde = KernelDensity(kernel='gaussian', bandwidth=0.1).fit(scoreHuman)
	# x = np.arange(0, 20, 1).reshape(-1, 1)
	# log_density_values = kde.score_samples(x)
	# density = np.exp(log_density_values)
	# fig, ax = plt.subplots()
	# ax.plot(density)
	# fig.savefig('plots/kdeTest.pdf')


	# eval_points = np.mgrid[0:15:1, 0:20:1].reshape(2, -1).T

	# 2D sample
	dx, dy = 1, 1
	scoreHuman = dfHuman.drop(['user', 'group', 'player', 'turn', 'generosity', 'compensation', 'objective', 'selfLearning', 'otherIdentity', 'otherStrategy', 'otherNumber', 'empathy', 'risk', 'altruism'], axis=1).to_numpy()
	scoreAgent = dfAgent.drop(['agent', 'turn', 'generosity', 'rO', 'dT', 'G'], axis=1).to_numpy()
	x, y = np.mgrid[xmin:xmax:dx, ymin:ymax:dy]
	eval_points = np.vstack([x.ravel(), y.ravel()])

	# kde = stats.gaussian_kde(scoreHuman.T, bw_method=0.1)
	# z = np.reshape(kde(eval_points).T, x.shape)
	# z2 = np.exp(z)
	# fig, ax = plt.subplots()
	# ax.plot(z2[0])
	# ax.plot(z2[1])
	# fig.savefig('plots/kdeTestScipy.pdf')

	kdeHuman = KernelDensity(kernel='gaussian', bandwidth=0.1).fit(scoreHuman)
	kdeAgent = KernelDensity(kernel='gaussian', bandwidth=0.1).fit(scoreAgent)
	densityHuman = np.reshape(np.exp(kdeHuman.score_samples(eval_points.T)), y.shape)
	densityAgent = np.reshape(np.exp(kdeAgent.score_samples(eval_points.T)), y.shape)


	fig, ax = plt.subplots()
	ax.plot(y[0], densityHuman[0], label='human', color='b')
	ax.plot(y[0], densityAgent[0], label='agent', linestyle='--', color='b')
	ax.set(xlabel='score', ylabel='density', title=f"Chi-Squared Distance: {chi2_distance(densityHuman[0], densityAgent[0]):.3f}")
	fig.savefig('plots/kdeTest.pdf')
	fig, ax = plt.subplots()
	ax.plot(y[0], densityHuman[-1], label='human', color='b')
	ax.plot(y[0], densityAgent[-1], label='agent', linestyle='--', color='b')
	ax.set(xlabel='score', ylabel='density', title=f"Chi-Squared Distance: {chi2_distance(densityHuman[-1], densityAgent[-1]):.3f}")
	fig.savefig('plots/kdeTest2.pdf')
	fig, ax = plt.subplots()
	ax.plot(y, densityHuman, label='human', color='b')
	ax.plot(y, densityAgent, label='agent', linestyle='--', color='b')
	ax.set(xlabel='score', ylabel='density', title=f"Chi-Squared Distance: {chi2_distance(densityHuman, densityAgent):.3f}")
	fig.savefig('plots/kdeTest3.pdf')

def chi2_distance(x, y):
	assert x.shape == y.shape
	S = 0
	if len(x.shape)==1:
		for i in range(x.shape[0]):
			if x[i] + y[i] > 0:
				S += np.square(x[i] - y[i]) / (x[i] + y[i])
	if len(x.shape)==2:
		for i in range(x.shape[0]):
			for j in range(x.shape[1]):
				if x[i,j] + y[i,j] > 0:
					S += np.square(x[i,j] - y[i,j]) / (x[i,j] + y[i,j])
	return 0.5 * S



def runFourGroups(rOA, rOB, dEmin, dEmax, Gmin, Gmax, architecture, capital, match, turns, trials, repetitions, games, seed, nS=10):
	rng = np.random.RandomState(seed=seed)
	# rOsFriendly = np.around(rng.uniform(rOmin, rOmax, size=trials), decimals=3)
	# rOs = [rOmin if rng.randint(2)==0 else rOmax for i in range(trials)]
	# rOs = np.around(rng.uniform(rOmin, rOmax, size=trials), decimals=3)
	rOAs = [0 if rng.randint(2)==0 else rOA for a in range(trials)]
	rOBs = [0 if rng.randint(2)==0 else rOB for a in range(trials)]
	dEs = np.around(rng.uniform(dEmin, dEmax, size=trials), decimals=3)
	Gs = np.around(rng.uniform(Gmin, Gmax, size=trials), decimals=3)
	dfs = []
	columns = ('group', 'player', 'agent', 'trial', 'repetition', 'game', 'turn', 'score', 'generosity', 'rO', 'dE', 'G')
	for group in ['greedy', 'generous']:
		for player in ['A', 'B']:
			rOs = rOAs.copy() if player=="A" else rOBs.copy()
			nActions = capital+1 if player=="A" else capital*match+1
			for a in range(trials):
				print(f"Group {group}, Player {player}, Trial {a}")			
				if architecture=='bandit':
					agent = Bandit(player, nActions, rO=rOs[a], dE=dEs[a], ID=f"Bandit #{a}")
				if architecture=='qlearn':
					agent = QLearn(player, nActions, nS, rO=rOs[a], dE=dEs[a], G=Gs[a], ID=f"QLearn #{a}")
				if architecture=='modelbased':
					agent = ModelBased(player, nActions, nS, rO=rOs[a], dE=dEs[a], G=Gs[a], ID=f"ModelBased #{a}")
				agent.restart()
				for g in range(games):
					agent.reset()
					histories = []
					for r in range(repetitions):  # agent plays this t4t multiples times
						if group=='greedy' and player=='A':
							t4t = T4TV("B", seed=g, minO=0.1, maxO=0.3, minX=0.5, maxX=0.5, minF=0.0, maxF=0.1, minP=0.2, maxP=0.2)
						if group=='greedy' and player=='B':
							t4t = T4TV("A", seed=g, minO=0.8, maxO=1.0, minX=0.5, maxX=0.5, minF=1.0, maxF=1.0, minP=0.1, maxP=0.3)
						if group=='generous' and player=='A':
							t4t = T4TV("B", seed=g, minO=0.3, maxO=0.5, minX=0.5, maxX=0.5, minF=0.4, maxF=0.6, minP=1.0, maxP=1.0)
						if group=='generous' and player=='B':
							t4t = T4TV("A", seed=g, minO=0.6, maxO=0.8, minX=0.5, maxX=0.5, minF=0.8, maxF=1.0, minP=1.0, maxP=1.0)
						t4t.reset()
						if player=="A":
							G = Game(agent, t4t, capital, match, turns)
							G.play()
							scores, generosities = G.history['aRewards'], G.history['aGen']
						else:
							G = Game(t4t, agent, capital, match, turns)					
							G.play()
							scores, generosities = G.history['bRewards'], G.history['bGen']
						for t in range(turns):
							dfs.append(pd.DataFrame([[
								group, player, agent.ID, a, r, g, t, scores[t], generosities[t], agent.rO, agent.dE, agent.G
								]], columns=columns))
						histories.append(G.history)
					np.random.shuffle(histories)
					for hist in histories:
						agent.learn(hist)
					agent.reduceExploration(g)
	df = pd.concat([df for df in dfs], ignore_index=True)
	df.to_pickle(f"data/runFourGroups_{architecture}.pkl")
	return