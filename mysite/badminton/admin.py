from django.contrib import admin

from badminton.models import Tournament, Match, Team, Player

# Register your models here.

admin.site.register(Tournament)
admin.site.register(Match)
admin.site.register(Team)
admin.site.register(Player)

