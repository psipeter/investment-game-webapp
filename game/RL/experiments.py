import numpy as np
import random
import pandas as pd
from agents import *

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
			self.history['bGen'].append(np.NaN if (bGive+bKeep)==0 else bGive/(bGive+bKeep))
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