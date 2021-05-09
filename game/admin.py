from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
from .models import Game, Agent, User, Blob, Feedback

# admin.site.register(Game)
@admin.register(Game)
class Game(admin.ModelAdmin):
	list_display = ('uuid', 'user', 'get_userGroup', 'userRole', 'agentRole', 'seed', 'tStart', 'tEnd', 'userGives', 'userKeeps', 'userRewards', 'userTimes', 'agentGives', 'agentKeeps', 'agentRewards')
	ordering = ('-tStart',)
	def get_userGroup(self, obj):
		return obj.agent.userGroup  # displays 'tutorial'
	get_userGroup.short_description = "userGroup"

@admin.register(Agent)
class Agent(admin.ModelAdmin):
	list_display = ('userGroup', 'userRole', 'created')

@admin.register(User)
class User(UserAdmin):
	list_display = ('username', 'mturk', 'group', 'nGames', 'show_winnings', 'doneTutorial', 'doneCash', 'code', 'selfFeedback')

@admin.register(Blob)
class Blob(admin.ModelAdmin):
	list_display = ('name',)

@admin.register(Feedback)
class Feedback(admin.ModelAdmin):
	list_display = ('text',)