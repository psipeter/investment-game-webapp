from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Game, User, Feedback
from .parameters import *


import json
import numpy as np

# https://stackoverflow.com/a/57915246
class NpEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


@login_required
def status(request):
	request.user.setProgress()

	bonusGames = Game.objects.filter(user=request.user, complete=True).exclude(agent__name__in=REQUIRED_AGENTS)
	performanceGames = 0
	for game in bonusGames:
		if sum(game.historyToArray("user", "reward")) >= PERFORMANCE_THR:
			performanceGames+= 1
	bonusReward = BONUS_RATE*bonusGames.count() + PERFORMANCE_RATE*performanceGames

	data = {
		'username': request.user.username,
		'path': request.path,
		'N_REQUIRED': N_REQUIRED,
		'N_BONUS': N_BONUS,
		'nRequired': request.user.nRequired,
		'nBonus': request.user.nBonus,
		'doneConsent': request.user.doneConsent,
		'doneSurvey': request.user.doneSurvey,
		'doneTutorial': request.user.doneTutorial,
		'doneRequired': request.user.doneRequired,
		'doneBonus': request.user.doneBonus,
		'doneHIT': request.user.doneCash,
		'doneCash': request.user.doneCash,
		'fixedReward': FIXED_REWARD,
		'bonusReward': bonusReward,
		}
	return JsonResponse(data)


@login_required
def startGame(request):
	if request.method != 'POST':
		return JsonResponse({
			"status": "error",
			"message": "Must use a POST request to start a new game",
		});

	if request.user.doneConsent and request.user.doneTutorial:
		game = Game.objects.create()
		game.start(request.user)
		data = {
			'uuid': game.uuid,
			'userRole': game.userRole,
			'capital': game.capital,
			'match': game.match,
			'userName': game.user.username,
			'agentName': game.agent.name,
			'doneRequired': request.user.doneRequired,
			'userGives': list(game.historyToArray("user", "give")),
			'userKeeps': list(game.historyToArray("user", "keep")),
			'userRewards': list(game.historyToArray("user", "reward")),
			'agentGives': list(game.historyToArray("agent", "give")),
			'agentKeeps': list(game.historyToArray("agent", "keep")),
			'agentRewards': list(game.historyToArray("agent", "reward")),
		}
		return JsonResponse(data, encoder=NpEncoder);
	else:
		return JsonResponse({
			"status": "error",
			"message": "You must complete the tutorial before playing the required games",
		});


@login_required
def updateGame(request):
	userGive = int(request.POST.get('userGive'))
	userKeep = int(request.POST.get('userKeep'))
	userTime = float(request.POST.get('userTime'))/1000
	game = request.user.currentGame
	game.step(userGive, userKeep, userTime)
	data = {
		'userGives': list(game.historyToArray("user", "give")),
		'userKeeps': list(game.historyToArray("user", "keep")),
		'userRewards': list(game.historyToArray("user", "reward")),
		'agentGives': list(game.historyToArray("agent", "give")),
		'agentKeeps': list(game.historyToArray("agent", "keep")),
		'agentRewards': list(game.historyToArray("agent", "reward")),
	}
	if game.complete:
		request.user.currentGame = None
		request.user.save()
		data['complete'] = True
		request.user.setProgress()
	else:
		data['complete'] = False

	# update message to user if they finished the last game in a batch
	if game.agent.name == "tutorial" and request.user.doneTutorial:
		data['doneGames'] = True
		data['message'] = "Tutorial Games Complete!"
	elif game.agent.name == "required" and request.user.doneRequired:
		data['doneGames'] = True
		data['message'] = "Required Games Complete!"
	elif request.user.doneTutorial and request.user.doneRequired and request.user.doneBonus:
		data['doneGames'] = True
		data['message'] = "Bonus Games Complete!"
	else:
		data['doneGames'] = False
		data['message'] = None

	return JsonResponse(data, encoder=NpEncoder)
