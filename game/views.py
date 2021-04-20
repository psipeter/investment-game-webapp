from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import Game, User, Feedback
from game.forms import LoginForm, CreateForm, ProfileForm, ResetForm, CashForm, FeedbackForm, TutorialForm
import pytz
from .parameters import *

# Authentication

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			identifier = request.POST['identifier']
			password = request.POST['password']
			if User.objects.filter(username=identifier).exists():
				username = identifier
			elif User.objects.filter(mturk=identifier).exists():
				username = User.objects.filter(mturk=identifier)[0]
			else:
				form.add_error('identifier', "Username does not exist")
				return render(request, 'login.html', {'form':form})
			user = authenticate(username=username, password=password)
			if user: # and user.is_active:
				auth_login(request, user)
				return redirect(reverse('home'))
			else:
				form.add_error('password', "Password incorrect")
				return render(request, 'login.html', {'form':form})
	else:
		form = LoginForm()
		if 'next' in request.GET:
			context = {'form':form, 'next': request.GET['next']}
		# todo: added "logged out" message
		# todo: added "password reset" message
		else:
			context = {'form':form}
		return render(request, 'login.html', context)

def logout(request):
	auth_logout(request)
	return redirect('login')
	# return render(request, 'logout.html')

def reset(request):
	if request.method == 'POST':
		form = ResetForm(request.POST)
		if form.is_valid():
			identifier = request.POST['identifier']
			password = request.POST['password1']
			if User.objects.filter(username=identifier).exists():
				user = User.objects.get(username=identifier)
			elif User.objects.filter(mturk=identifier).exists():
				user = User.objects.get(mturk=identifier)
			user.set_password(password)
			user.save()
			return redirect('login')
	else:
		form = ResetForm()
	return render(request, 'reset.html', {'form': form})


# Account Creation

def information(request):
	return render(request, "information.html")

def consent(request):
	if request.method == 'POST':
		form = CreateForm(request.POST)
		username = request.POST['username']
		password1 = request.POST['password1']
		password2 = request.POST['password2']
		if form.is_valid():
			user = form.save()
			user.save()
			auth_login(request, user)
			user.doneConsent = timezone.now()
			user.save()
			return redirect('home')
	else:
		form = CreateForm()
	return render(request, 'consent.html', {'form': form})

# Main Page Links

@login_required
def survey(request):
	if request.method == 'POST':
		form = ProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			request.user.doneSurvey = timezone.now()
			request.user.save()
			return redirect('home')
	else:
		form = ProfileForm(instance=request.user)
	return render(request, 'survey.html', {'form': form})

@login_required
def cash(request):
	request.user.setProgress()
	if not (request.user.doneConsent and request.user.nGames > 0):
		error(request, 'You must complete the required games before cashing out')
		return redirect('home')
	else:
		request.user.doneCash = timezone.now()
		request.user.save()
		context = {'winnings': f"{request.user.winnings:.2f}",}
		return render(request, "cash.html", context=context)

@login_required
def feedback(request):
	if request.method == 'POST':
		form = FeedbackForm(request.POST)
		if form.is_valid():
			text = request.POST.get('feedback')
			feedback = Feedback.objects.create()
			feedback.text = text
			feedback.save()
			return redirect('home')
	else:
		form = FeedbackForm()
	return render(request, "feedback.html", {'form': form})

@login_required
def home(request):
	return render(request, 'home.html')

# Game Links

@login_required
def startGame(request):
	if request.user.nGames > REQUIRED:
		error(request, 'You have already played the maximum number of games')
		return redirect('home')		
	if request.user.doneConsent and request.user.doneTutorial:
		return render(request, "game.html")
	else:
		error(request, 'You must complete the tutorial before playing the required games')
		return redirect('home')

@login_required
def startTutorial(request):
	context = {
		'bonus_min': f"{BONUS_MIN:.2f}",
		'bonus_rate': f"{BONUS_RATE:.3f}",
	}
	return render(request, "tutorial.html", context=context)

@login_required
def startTutorial2(request):
	context = {
		'required': REQUIRED,
		'minBonus': f'{BONUS_MIN:.2f}',
		'maxBonus': f'{BONUS_MIN+BONUS_RATE*CAPITAL*MATCH*ROUNDS:.2f}',
	}
	return render(request, "tutorial2.html", context=context)

@login_required
def slider(request):
	return render(request, "slider.html")
