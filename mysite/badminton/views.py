from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView
from .models import Tournament, Team, Match
import random
from itertools import combinations
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms
from django.views.generic import CreateView
from .models import Player



class PlayerListView(ListView):
    model = Player
    template_name = 'badminton/player_list.html'
    context_object_name = 'players'


class TournamentListView(ListView):
    model = Tournament
    template_name = 'badminton/tournament_list.html'
    context_object_name = 'tournaments'


def create_tournament(request):
    if request.method == 'POST':
        selected_players = request.POST.getlist('players')
        if len(selected_players) < 4:
            messages.error(request, 'Need at least 4 players for a tournament')
            return redirect('player-list')

        tournament = Tournament.objects.create(
            name=f"Tournament {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        )

        # Add selected players to tournament
        players = Player.objects.filter(id__in=selected_players)
        tournament.players.set(players)

        # Create random teams
        player_list = list(players)
        random.shuffle(player_list)

        for i in range(0, len(player_list), 2):
            if i + 1 < len(player_list):
                Team.objects.create(
                    tournament=tournament,
                    player1=player_list[i],
                    player2=player_list[i + 1]
                )

        # Create matches in round-robin format
        teams = Team.objects.filter(tournament=tournament)
        for team1, team2 in combinations(teams, 2):
            Match.objects.create(
                tournament=tournament,
                team1=team1,
                team2=team2
            )

        return redirect('tournament-detail', pk=tournament.pk)

    return redirect('player-list')


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PlayerCreateView(CreateView):
    model = Player
    form_class = PlayerForm
    template_name = 'badminton/player_form.html'
    success_url = reverse_lazy('player-list')


def update_match_score(request, match_id):
    if request.method == 'POST':
        match = Match.objects.get(id=match_id)
        match.team1_score = request.POST.get('team1_score')
        match.team2_score = request.POST.get('team2_score')
        match.played_at = timezone.now()
        match.save()

        # Check if all round robin matches are complete
        if match.match_type == 'RR':
            rr_matches = Match.objects.filter(
                tournament=match.tournament,
                match_type='RR'
            )
            if all(m.played_at for m in rr_matches):
                match.tournament.start_knockout_stage()

        # Create final match if both semifinals are complete
        elif match.match_type == 'SF':
            match.create_final_match()

        # Update tournament winner if final match is complete
        elif match.match_type == 'F':
            match.update_tournament_winner()

        return redirect('tournament-detail', pk=match.tournament.pk)

    return redirect('tournament-list')


class TournamentDetailView(DetailView):
    model = Tournament
    template_name = 'badminton/tournament_detail.html'
    context_object_name = 'tournament'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = Team.objects.filter(tournament=self.object)
        context['standings'] = self.object.get_team_standings()

        # Separate matches by type
        context['round_robin_matches'] = Match.objects.filter(
            tournament=self.object,
            match_type='RR'
        )
        context['semifinal_matches'] = Match.objects.filter(
            tournament=self.object,
            match_type='SF'
        )
        context['final_match'] = Match.objects.filter(
            tournament=self.object,
            match_type='F'
        )

        return context