from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone

import pytz
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
	created = models.DateTimeField(auto_now_add=True)
	userGroup = models.CharField(max_length=10, null=True, blank=True)
	userRole = models.CharField(max_length=10, null=True, blank=True)
	blob = models.ForeignKey(Blob, on_delete=models.SET_NULL, null=True, blank=True)
	obj = None  # will store de-pickled blob, the python agent class

	def getObj(self, game):
		if self.userGroup=='generous' and self.userRole=='A':
			self.obj = T4TV("B", seed=game.seed, minO=0.3, maxO=0.5, minX=0.5, maxX=0.5, minF=0.4, maxF=0.6, minP=1.0, maxP=1.0, E=0)
		elif self.userGroup=='generous' and self.userRole=='B':
			self.obj = T4TV("A", seed=game.seed, minO=0.6, maxO=0.8, minX=0.5, maxX=0.5, minF=0.8, maxF=1.0, minP=1.0, maxP=1.0, E=0)
		elif self.userGroup=='greedy' and self.userRole=='A':
			self.obj = T4TV("B", seed=game.seed, minO=0.1, maxO=0.3, minX=0.5, maxX=0.5, minF=0.0, maxF=0.1, minP=0.2, maxP=0.2, E=0)
		elif self.userGroup=='greedy' and self.userRole=='B':
			self.obj = T4TV("A", seed=game.seed, minO=0.8, maxO=1.0, minX=0.5, maxX=0.5, minF=1.0, maxF=1.0, minP=0.1, maxP=0.3, E=0)
		elif self.userGroup=='tutorial' and self.userRole=="A":
			self.obj = T4T("B", O=1, X=0.5, F=1.0, P=0.4, E=0, S=0)
		elif self.userGroup=='tutorial' and self.userRole=="B":
			self.obj = T4T("A", O=1, X=0.5, F=1.0, P=0.4, E=0, S=0)
		else:
			raise Exception(f'userGroup {self.userGroup}, usreRole {self.userRole} not understood')
		self.blob = Blob.objects.create()
		self.blob.name = self.userGroup+self.userRole
		self.blob.blob = pickle.dumps(self.obj)
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
	userRole = models.CharField(max_length=1, null=True, blank=True)
	agentRole = models.CharField(max_length=1, null=True, blank=True)
	tutorial = models.BooleanField(default=False)
	complete = models.BooleanField(default=False)
	tStart = models.DateTimeField(null=True, blank=True)
	tEnd = models.DateTimeField(null=True, blank=True)
	turns = models.IntegerField(default=TURNS)
	capital = models.IntegerField(default=CAPITAL)
	match = models.FloatField(default=MATCH)
	seed = models.IntegerField(default=0)

	def start(self, user):
		self.user = user
		self.seed = self.user.nGames
		userGamesA = Game.objects.filter(user=user, userRole="A", complete=True).count()
		userGamesB = Game.objects.filter(user=user, userRole="B", complete=True).count()
		if userGamesA < userGamesB:
			self.userRole = "A"
			self.agentRole = "B"
		elif userGamesB < userGamesA:
			self.userRole = "B"
			self.agentRole = "A"
		else:
			switch = int(timezone.now().second)%2==0
			self.userRole = "A" if switch else "B"
			self.agentRole = "B" if switch else "A"
		self.save()
		self.setAgent()
		if self.agentRole == "A":
			self.goAgent(self.capital)
		self.user.currentGame = self
		self.user.save()
		self.tStart = timezone.now()
		self.save()

	def setAgent(self):
		self.agent = Agent.objects.create()
		self.agent.userGroup = self.user.group
		self.agent.userRole = self.userRole
		self.agent.save()
		self.save()

	def startTutorial(self, user, userRole, agentRole, agentName):
		self.user = user
		self.seed = self.user.nGames
		self.userRole = userRole
		self.agentRole = agentRole
		self.save()
		self.agent = Agent.objects.create()
		self.agent.userGroup = "tutorial"
		self.agent.userRole = self.userRole
		self.agent.save()
		self.save()
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
		if len(userGives) == self.turns and len(agentGives) == self.turns:
			self.complete = True
		if len(userGives) > self.turns or len(agentGives) > self.turns:
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
	def g(): return get_random_string(length=32)
	avatar = models.IntegerField(default=0)
	mturk = models.CharField(max_length=33, unique=True)
	currentGame = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name="currentGame")
	nGames = models.IntegerField(default=0)
	winnings = models.FloatField(default=0.00)
	doneConsent = models.DateTimeField(null=True, blank=True)
	doneSurvey = models.DateTimeField(null=True, blank=True)
	doneTutorial = models.DateTimeField(null=True, blank=True)
	doneGames = models.DateTimeField(null=True, blank=True)
	doneCash = models.DateTimeField(null=True, blank=True)
	doneExit = models.DateTimeField(null=True, blank=True)
	group = models.CharField(max_length=300, null=True, blank=True)
	code = models.CharField(max_length=300, default=g)
	age = models.CharField(max_length=300, null=True, blank=True)
	gender = models.CharField(max_length=300, null=True, blank=True)
	income = models.CharField(max_length=300, null=True, blank=True)
	education = models.CharField(max_length=300, null=True, blank=True)
	veteran = models.CharField(max_length=300, null=True, blank=True)
	empathy = models.CharField(max_length=300, null=True, blank=True)
	risk = models.CharField(max_length=300, null=True, blank=True)
	altruism = models.CharField(max_length=300, null=True, blank=True)
	compensation = models.CharField(max_length=300, null=True, blank=True)
	objective = models.CharField(max_length=300, null=True, blank=True)
	selfLearning = models.CharField(max_length=300, null=True, blank=True)
	otherIdentity = models.CharField(max_length=300, null=True, blank=True)
	otherStrategy = models.CharField(max_length=300, null=True, blank=True)
	otherNumber = models.CharField(max_length=300, null=True, blank=True)
	selfFeedback = models.CharField(max_length=4200, null=True, blank=True)

	def setGroup(self):
		# If there is a significant imbalance in number of users in each group, force a rebalance
		# Query database, count users in both groups, assign user to less common group
		greedyUsers = User.objects.filter(nGames__gte=1, group='greedy').count()
		generousUsers = User.objects.filter(nGames__gte=1, group='generous').count()
		print(greedyUsers, generousUsers, int(timezone.now().second))
		if generousUsers+2 < greedyUsers:
			self.group = 'generous'
		elif greedyUsers+2 < generousUsers:
			self.group = 'greedy'			
		else:
			self.group = 'generous' if int(timezone.now().second)%2==0 else 'greedy'
		self.save()

	def setProgress(self):
		allGames = Game.objects.filter(user=self).exclude(tutorial=True)
		completeGames = allGames.filter(complete=True)
		incompleteGames = allGames.filter(complete=False)
		self.nGames = completeGames.count()
		self.save()
		if self.doneGames == None and self.nGames >= REQUIRED:
			self.doneGames = timezone.now()
		self.save()
		winnings = 0.0
		for game in completeGames:
			score = sum(game.historyToArray("user", "reward"))
			winnings += BONUS_MIN + score*BONUS_RATE
		self.winnings = np.around(winnings, 2)
		self.save()

	def show_winnings(self):
		allGames = Game.objects.filter(user=self).exclude(tutorial=True)
		completeGames = allGames.filter(complete=True)
		winnings = 0.0
		for game in completeGames:
			score = sum(game.historyToArray("user", "reward"))
			winnings += BONUS_MIN + score*BONUS_RATE
		self.winnings = np.around(winnings, 2)
		self.save()
		return self.winnings