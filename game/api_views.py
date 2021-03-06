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
	data = {
		'username': request.user.username,
		'path': request.path,
		'nGames': request.user.nGames,
		'required': REQUIRED,
		'doneConsent': request.user.doneConsent,
		'doneSurvey': request.user.doneSurvey,
		'doneTutorial': request.user.doneTutorial,
		'doneRequired': request.user.doneRequired,
		'doneMax': request.user.doneMax,
		'doneHIT': request.user.doneCash,
		'doneCash': request.user.doneCash,
		'winnings': f"{request.user.winnings:.2f}",
		}
	return JsonResponse(data)


@login_required
def startGame(request):
	request.user.setProgress()
	if request.method != 'POST':
		return JsonResponse({
			"status": "error",
			"message": "Must use a POST request to start a new game",
		});

	if request.user.doneConsent and request.user.doneTutorial:
		game = Game.objects.create()
		game.start(request.user)
		data = {
			'username': game.user.username,
			'agentname': game.agent.name,
			'nGames': game.user.nGames,
			'winnings': f"{request.user.winnings:.2f}",
			'uuid': game.uuid,
			'userRole': game.userRole,
			'rounds': game.rounds,
			'capital': game.capital,
			'match': game.match,
			'bonus': BONUS,
			'doneRequired': game.user.doneRequired,
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
		data['complete'] = True
		request.user.currentGame = None
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
	elif request.user.doneTutorial and request.user.doneRequired and request.user.doneMax:
		data['doneGames'] = True
		data['message'] = "Bonus Games Complete!"
	else:
		data['doneGames'] = False
		data['message'] = None

	return JsonResponse(data, encoder=NpEncoder)
