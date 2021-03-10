from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list
from django.conf import settings
from django.utils.crypto import get_random_string
from datetime import datetime

import uuid
import numpy as np
import random
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import json
import pandas as pd

from .RL.agents import *
from .parameters import *


class Feedback(models.Model):
	text = models.CharField(max_length=4200, blank=True, null=True, default=str)

class Blob(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True, default=str)
	blob = models.BinaryField(null=True)  # for agent class

class Agent(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique agent ID")
	name = models.CharField(max_length=100, blank=True, null=True, default=str)
	created = models.DateTimeField(auto_now_add=True)
	player = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	blob = models.ForeignKey(Blob, on_delete=models.SET_NULL, null=True, blank=True)
	obj = None  # will store de-pickled blob, the python agent class

	def start(self, name, player):
		self.name = name
		self.player = player
		self.save()

	def getObj(self, game):
		name = self.name
		player = self.player
		# blobname = f"{name}{player}"
		blobname = name
		nA = int(game.capital+1) if player == "A" else int(game.capital*game.match+1)
		nS = 10
		# if Blob.objects.filter(name=blobname).exists():
		# 	self.blob = Blob.objects.get(name=blobname)
		# 	self.obj = pickle.loads(self.blob.blob)
		# else:
		if name=='Greedy':
			self.obj = Fixed(player, mean=0.2, E=EPSILON, S=SIGMA)
		elif name=="Even":
			self.obj = Fixed(player, mean=0.5, E=EPSILON, S=SIGMA)
		elif name=="Generous":
			self.obj = Fixed(player, mean=0.8, E=EPSILON, S=SIGMA)
		elif name=="T4T":
			self.obj = T4T(player, F=0.5, P=0.5, E=EPSILON, S=SIGMA)
		elif name=="Expect":
			self.obj = Expect(player, X=0.33, F=0.5, P=0.5, E=EPSILON, S=SIGMA)
		elif name=="Greedy2":
			self.obj = BecomeGreedy(player, start=0.75, step=0.15, E=EPSILON, S=SIGMA)
			# elif name=="Bandit":
			# 	self.obj = Bandit(player, nA)
			# elif name=="QLearn":
			# 	self.obj = QLearn(player, nA, nS)
			# elif name=="Wolf":
			# 	self.obj = Wolf(player, nA, nS)
			# elif name=="Hill":
			# 	self.obj = Hill(player, nA, nS)
			# elif name=="ModelBased":
			# 	self.obj = ModelBased(player, nA, nS)
		else:
			raise Exception(f'{name} is not a valid agent class')
		self.blob = Blob.objects.create()
		self.blob.name = blobname
		self.blob.blob = pickle.dumps(self.obj)
		# stop indent
		self.obj.loadArchive(file=f"{name}{player}.npz")
		self.obj.reset()
		agentStates = game.historyToArray("agent", "state")
		if len(agentStates) > 0:
			self.obj.state = agentStates[-1]
		self.blob.save()
		self.save()

	def learn(self, game):
		# update matrices in python object
		history = game.historyToDict()
		self.getObj(game, history)
		self.obj.learn(history)
		# update matricies in database
		self.blob.blob = pickle.dumps(self.obj)
		self.blob.save()
		self.save()


class Game(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique game ID")
	date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
	agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
	userGives = models.CharField(max_length=50, blank=True, null=True, default=str)
	userKeeps = models.CharField(max_length=50, blank=True, null=True, default=str)
	userRewards = models.CharField(max_length=50, blank=True, null=True, default=str)
	userTimes = models.CharField(max_length=50, blank=True, null=True, default=str)
	agentGives = models.CharField(max_length=50, blank=True, null=True, default=str)
	agentKeeps = models.CharField(max_length=50, blank=True, null=True, default=str)
	agentRewards = models.CharField(max_length=50, blank=True, null=True, default=str)
	agentStates = models.CharField(max_length=50, blank=True, null=True, default=str)
	userRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	agentRole = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B")), null=True, blank=True)
	complete = models.BooleanField(default=False)
	rounds = models.IntegerField(default=ROUNDS)
	capital = models.IntegerField(default=CAPITAL)
	match = models.FloatField(default=MATCH)
	seed = models.IntegerField(default=0)

	def setAgent(self):
		idx = int(self.user.nGames/2) # item 0 from list 1, item 0 from list 2, item 1 from list 1, ...
		if self.user.group == "1" and self.userRole == "A": name = AGENTS_F_B[idx]
		elif self.user.group == "1" and self.userRole == "B": name = AGENTS_F_A[idx]
		elif self.user.group == "2" and self.userRole == "A": name = AGENTS_P_B[idx]
		elif self.user.group == "2" and self.userRole == "B": name = AGENTS_P_A[idx]
		else: raise "agent not set"
		self.agent = Agent.objects.create()
		self.agent.start(name, self.agentRole)
		self.save()

	def start(self, user):
		self.user = user
		self.seed = np.random.randint(1e6)
		np.random.seed(self.seed)  # set random number seed
		idx = self.user.nGames
		self.userRole = PLAYERS[idx][0]
		self.agentRole = PLAYERS[idx][1]
		self.save()
		self.setAgent()
		if self.agentRole == "A":
			self.goAgent(self.capital)
		self.user.currentGame = self
		self.user.save()
		self.save()

	def step(self, userGive, userKeep, userTime):
		self.goUser(userGive, userKeep, userTime)
		if self.userRole == "A":
			invest = self.historyToArray("user", "give")[-1]
			self.goAgent(self.match*invest)
		elif not self.complete:
			self.goAgent(self.capital)
		self.rewards()

	def goUser(self, userGive, userKeep, userTime):
		self.userGives += f"{userGive:d},"
		self.userKeeps += f"{userKeep:d},"
		self.userTimes += f"{userTime:.2f},"
		self.checkComplete()

	def goAgent(self, money):
		history = self.historyToDict()
		self.agent.getObj(self)
		agentGive, agentKeep = self.agent.obj.act(money, history)
		agentState = self.agent.obj.state
		self.agentGives += f"{agentGive:d},"
		self.agentKeeps += f"{agentKeep:d},"
		self.agentStates += f"{agentState:.2f},"
		self.checkComplete()

	def checkComplete(self):
		userGives = self.historyToArray("user", "give")
		agentGives = self.historyToArray("agent", "give")
		if len(userGives) == self.rounds and len(agentGives) == self.rounds:
			self.complete = True
		if len(userGives) > self.rounds or len(agentGives) > self.rounds:
			raise Exception("Too many moves taken")
		self.save()

	def rewards(self):
		userGives = self.historyToArray("user", "give")
		userKeeps = self.historyToArray("user", "keep")
		agentGives = self.historyToArray("agent", "give")
		agentKeeps = self.historyToArray("agent", "keep")
		self.userRewards = ""
		self.agentRewards = ""
		self.save()
		for t in range(len(userGives)):
			if self.userRole == "A":
				self.userRewards += f"{userKeeps[t]+agentGives[t]:d},"
				self.agentRewards += f"{agentKeeps[t]:d},"
			else:
				self.agentRewards += f"{agentKeeps[t]+userGives[t]:d},"
				self.userRewards += f"{userKeeps[t]:d},"
		self.save()

	def historyToArray(self, player, entry):
		if player == "user":
			if entry == "give":
				return np.array(self.userGives.split(',')[:-1]).astype(np.int)
			elif entry == "keep":
				return np.array(self.userKeeps.split(',')[:-1]).astype(np.int)
			elif entry == "reward":
				return np.array(self.userRewards.split(',')[:-1]).astype(np.int)
			elif entry == "state":
				return np.array([])
		else:
			if entry == "give":
				return np.array(self.agentGives.split(',')[:-1]).astype(np.int)
			elif entry == "keep":
				return np.array(self.agentKeeps.split(',')[:-1]).astype(np.int)
			elif entry == "reward":
				return np.array(self.agentRewards.split(',')[:-1]).astype(np.int)
			elif entry == "state":
				return np.array(self.agentStates.split(',')[:-1]).astype(np.float)

	def historyToDict(self):
		A = "user" if self.userRole=="A" else "agent"
		B = "agent" if self.userRole=="A" else "user"
		history = {
			'aGives': self.historyToArray(A, "give"),
			'aKeeps': self.historyToArray(A, "keep"),
			'aRewards': self.historyToArray(A, "reward"),
			'aStates': self.historyToArray(A, "state"),
			'bGives': self.historyToArray(B, "give"),
			'bKeeps': self.historyToArray(B, "keep"),
			'bRewards': self.historyToArray(B, "reward"),
			'bStates': self.historyToArray(B, "state"),
		}
		return history


class User(AbstractUser):
	# assign to unique group
	def f():
		return 1 if np.random.rand() < 0.5 else 2
	def g():
		return get_random_string(length=32)
	mturk = models.CharField(max_length=33, null=True, blank=True)
	currentGame = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name="currentGame")
	nGames = models.IntegerField(default=0)
	winnings = models.IntegerField(default=0)
	doneConsent = models.DateTimeField(null=True, blank=True)
	doneSurvey = models.DateTimeField(null=True, blank=True)
	doneTutorial = models.DateTimeField(null=True, blank=True)
	doneRequired = models.DateTimeField(null=True, blank=True)
	doneMax = models.DateTimeField(null=True, blank=True)
	doneHIT = models.DateTimeField(null=True, blank=True)
	doneCash = models.DateTimeField(null=True, blank=True)
	group = models.CharField(max_length=300, choices=(("1", "forgive"), ("2", "punish")), default=f)
	code = models.CharField(max_length=300, help_text="MTurk Confirmation Code", default=g)
	age = models.CharField(max_length=300, null=True, blank=True)
	gender = models.CharField(max_length=300, null=True, blank=True)
	income = models.CharField(max_length=300, null=True, blank=True)
	education = models.CharField(max_length=300, null=True, blank=True)
	veteran = models.CharField(max_length=300, null=True, blank=True)
	empathy = models.CharField(max_length=300, null=True, blank=True)
	risk = models.CharField(max_length=300, null=True, blank=True)
	altruism = models.CharField(max_length=300, null=True, blank=True)

	def setProgress(self):
		self.nGames = Game.objects.filter(user=self, complete=True).count()
		self.save()
		if self.doneRequired == None and self.nGames >= REQUIRED:
			self.doneRequired = datetime.now()
		if self.doneMax == None and self.nGames >= MAX:
			self.doneMax = datetime.now()
		self.save()
		bonus = 0
		for game in Game.objects.filter(user=self, complete=True):
			gameBonus = 0
			score = sum(game.historyToArray("user", "reward"))
			for i in range(len(BONUS)):
				if score>= BONUS[i][0]:
					gameBonus = BONUS[i][1]
			bonus += gameBonus
		self.winnings = np.around(bonus, 2)
		self.save()