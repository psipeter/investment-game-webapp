from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput
from django.core.validators import MaxValueValidator, MinValueValidator
from . import models
import numpy as np

class LoginForm(forms.Form):
	identifier = forms.CharField(label="Username or MTurk ID")
	password = forms.CharField(label='Password', widget=forms.PasswordInput)
	identifier.widget.attrs.update({'placeholder':'Username or MTurk ID'})	
	password.widget.attrs.update({'placeholder':'Password'})	
	identifier.widget.attrs.update({'autocomplete':'username'})	
	password.widget.attrs.update({'autocomplete':'password'})	
	class Meta:
		model = models.User
		fields = ('identifier', 'password')

class CreateForm(UserCreationForm):
	username = forms.CharField(label="Username")
	mturk = forms.CharField(label="Mechanical Turk ID")
	password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
	avatarChoices = (
		('1', 'Avatar 1'),
		('2', 'Avatar 2'),
		('3', 'Avatar 3'),
		('4', 'Avatar 4'))
	avatar = forms.ChoiceField(choices=avatarChoices)
	username.widget.attrs.update({'placeholder':'Username'})
	mturk.widget.attrs.update({'placeholder':'Mechanical Turk ID'})
	password1.widget.attrs.update({'placeholder':'Enter Password'})	
	password2.widget.attrs.update({'placeholder':'Confirm Password'})	
	password1.widget.attrs.update({'autocomplete':'password'})	
	password2.widget.attrs.update({'autocomplete':'password'})	
	class Meta:
		model = models.User
		fields = ('username', 'mturk', 'password1', 'password2', 'avatar')
		labels = {'username': 'Username', 'mturk': 'Mechanical Turk ID', 'password1': "Enter Password", 'password2': 'Confirm Password', 'avatar': 'Choose Avatar'}
		help_texts = {'username': None, 'password1': None, 'password2': None, 'avatar': None}

class ResetForm(forms.Form):
	identifier = forms.CharField(label="Identifier")
	password1 = forms.CharField(label='New password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
	identifier.widget.attrs.update({'placeholder':'Username or MTurk ID'})	
	password1.widget.attrs.update({'placeholder':'Enter Password'})	
	password2.widget.attrs.update({'placeholder':'Confirm Password'})	
	password1.widget.attrs.update({'autocomplete':'password'})	
	password2.widget.attrs.update({'autocomplete':'password'})	
	def clean_identifier(self):
		identifier = self.cleaned_data['identifier']
		if models.User.objects.filter(username=identifier).exists():
			return self.cleaned_data['identifier']
		elif models.User.objects.filter(mturk=identifier).exists():
			return self.cleaned_data['identifier']
		else:
			print(self.cleaned_data['identifier'])
			raise ValidationError("Username or MTurk ID not found")
	def clean_password2(self):
		password1 = self.cleaned_data['password1']
		password2 = self.cleaned_data['password2']
		if password1 == password2:
			return self.cleaned_data['password2']
		else:
			raise ValidationError("Passwords do not match")

class SurveyForm(forms.ModelForm):
	ageChoices = tuple([(str(n), str(n)) for n in np.arange(18, 121)])
	ageChoices = (('', '---'),) + ageChoices
	age = forms.ChoiceField(choices=ageChoices, required=False)
	genderChoices = (
		('', '---'),
		('m', 'Male'),
		('f', 'Female'),
		('o', 'Non-Binary'))
	gender = forms.ChoiceField(choices=genderChoices, required=False)
	incomeChoices = (
		('', '---'),
		('20k', 'Less than $20,000'),
		('40k', '$20,000 - 40,000'),
		('60k', '$40,000 - 60,000'),
		('80k', '$60,000 - 80,000'),
		('100k', '$80,000 - 100,000'),
		('>100k', 'Greater than $100,000'))
	income = forms.ChoiceField(
		# label="Yearly Household Income (combined before tax income of all working members of the household)",
		label="Yearly Household Income",
		choices=incomeChoices, required=False)
	educationChoices = (
		('', '---'),
		('primary', 'Primary (middle) school'),
		('secondary', 'Secondary (high) school'),
		('undergrad', 'Undergraduate degree'),
		('grad', 'Graduate degree'),
		('other', 'Other'))
	education = forms.ChoiceField(choices=educationChoices, required=False)
	veteranChoices = (
		('', '---'),
		('yes', 'Yes'),
		('no', 'No'))
	veteran = forms.ChoiceField(
		label="Have you ever played the Prisoner's Dilemma?",
		choices=veteranChoices,
		required=False)
	empathyLabel = "I am confident that I understand what others are thinking or feeling during conversation"
	riskLabel = "A coworker approaches you and asks for a $1000 loan, promising to return you the money, plus 20% interest, in a month. I would trust them and loan them the money"
	altruismLabel = "I win a million dollars in the lottery. I would keep the money for myself rather than giving it away to friends, family, or charity"
	likertScale = (
		('', '---'),
		('D!', 'Strongly Disagree'),
		('D', 'Disagree'),
		('U', 'Undecided'),
		('A', 'Agree'),
		('A!', 'Strongly Agree'))
	empathy = forms.ChoiceField(choices=likertScale, label=empathyLabel, required=False)
	risk = forms.ChoiceField(choices=likertScale, label=riskLabel, required=False)
	altruism = forms.ChoiceField(choices=likertScale, label=altruismLabel, required=False)

	class Meta:
		model = models.User
		fields = ('age', 'gender', 'income', 'education', 'veteran', 'empathy', 'risk', 'altruism')

class ExitSurveyForm(forms.ModelForm):
	compensationChoices = (
		('', '---'),
		('<', 'I should have earned more for the time I spent'),
		('=', 'I earned a reasonable amount for the time I spent'),
		('>', 'I earned more than I usually do for the time I spent'))
	compensationLabel = 'Was the money you earned for completing this HIT appropriate?'
	compensation = forms.ChoiceField(choices=compensationChoices, label=compensationLabel, required=False)
	objectiveChoices = (
		('', '---'),
		('self', 'I tried to earn as many points for myself as possible, without considering my opponent’s score'),
		('equal', 'I tried to achieve a high score for both myself and my opponent'),
		('random', 'I chose behaviors at random, playing as quickly as possible'))
	objectiveLabel = 'What was your objective when playing the investment game?'
	objective = forms.ChoiceField(choices=objectiveChoices, label=objectiveLabel, required=False)
	selfLearningChoices = (
		('', '---'),
		('slow', 'I needed to play more games to develop a good strategy'),
		('good', 'I learned a good strategy by the end, but didn’t get bored'),
		('fast', 'I learned a good strategy quickly, and playing the remaining games was boring'),
		('random', 'I chose behaviors at random, playing as quickly as possible'))
	selfLearningLabel = 'Were you able to learn an effective strategy?'
	selfLearning = forms.ChoiceField(choices=selfLearningChoices, label=selfLearningLabel, required=False)
	otherIdentityChoices = (
		('', '---'),
		('human', 'I played against human opponents'),
		('computer', 'I played against computer opponents'),
		('mix', 'I played against a mix of human and computer opponents'))
	otherIdentityLabel = 'What were your beliefs about the identity of your opponents?'
	otherIdentity = forms.ChoiceField(choices=otherIdentityChoices, label=otherIdentityLabel, required=False)
	otherStrategyChoices = (
		('', '---'),
		('generous', 'They were always generous'),
		('mix-random', 'They were sometimes generous and sometimes greedy, in a random pattern'),
		('mix-adaptive', 'They were sometimes generous and sometimes greedy, depending on my moves'),
		('greedy', 'They were always greedy'))
	otherStrategyLabel = 'How would you describe the strategies of your opponents?'
	otherStrategy = forms.ChoiceField(choices=otherStrategyChoices, label=otherStrategyLabel, required=False)
	otherNumberChoices = (
		('', '---'),
		('same', 'I played the same opponent in every game'),
		('mix', 'I sometimes played the same opponent and sometimes played a different opponent'),
		('unique', 'I played a different opponent in every game'))
	otherNumberLabel = 'What were your beliefs about the number of opponents you played?'
	otherNumber = forms.ChoiceField(choices=otherNumberChoices, label=otherNumberLabel, required=False)
	selfFeedbackLabel = 'How could we improve the user experience in the investment game?'
	selfFeedback = forms.CharField(max_length=4200, label=selfFeedbackLabel,
		widget=forms.Textarea(attrs={'rows': 6, 'cols': 60, 'placeholder': "Your feedback here...",}))

	class Meta:
		model = models.User
		fields = ('compensation', 'objective', 'selfLearning', 'otherIdentity', 'otherStrategy', 'otherNumber', 'selfFeedback')


class FeedbackForm(forms.Form):
	feedback = forms.CharField(
		max_length=4200,
		label=None,
		widget=forms.Textarea(attrs={
			'rows': 4, 'cols': 40,
			'placeholder': "Your feedback here...questions, comments, suggestions, etc.",
			}))

class CashForm(forms.Form):
	btn = forms.CharField(label=None)

class TutorialForm(forms.Form):
	btn = forms.CharField(label=None)
