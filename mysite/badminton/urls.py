from django.urls import path
from . import views

urlpatterns = [
    path('players/', views.PlayerListView.as_view(), name='player-list'),
    path('players/add/', views.PlayerCreateView.as_view(), name='player-add'),
    path('tournaments/', views.TournamentListView.as_view(), name='tournament-list'),
    path('tournaments/create/', views.create_tournament, name='tournament-create'),
    path('tournaments/<int:pk>/', views.TournamentDetailView.as_view(), name='tournament-detail'),
    path('matches/<int:match_id>/update/', views.update_match_score, name='update-match'),
]