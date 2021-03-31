from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
from .models import Game, Agent, User, Blob, Feedback

# admin.site.register(Game)
@admin.register(Game)
class Game(admin.ModelAdmin):
	list_display = ('uuid', 'user', 'userRole', 'get_agent', 'agentRole', 'tStart', 'tEnd', 'userGives', 'userKeeps', 'userRewards', 'userTimes', 'agentGives', 'agentKeeps', 'agentRewards')
	ordering = ('-tStart',)
	def get_agent(self, obj):
		return obj.agent.name
	get_agent.short_description = "Agent"
	get_agent.admin_order_field = "agent__agentType"

@admin.register(Agent)
class Agent(admin.ModelAdmin):
	list_display = ('name', 'player', 'created')

@admin.register(User)
class User(UserAdmin):
	list_display = ('username', 'mturk', 'group', 'nGames', 'show_winnings', 'code', 'doneConsent',  'doneTutorial', 'doneCash')

@admin.register(Blob)
class Blob(admin.ModelAdmin):
	list_display = ('name',)

@admin.register(Feedback)
class Feedback(admin.ModelAdmin):
	list_display = ('text',)