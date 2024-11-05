# models.py
from django.db import models
from django.utils import timezone

MATCH_TYPE_CHOICES = [
    ('RR', 'Round Robin'),
    ('SF', 'Semi Final'),
    ('F', 'Final')
]


class Player(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    players = models.ManyToManyField(Player)
    is_knockout_stage = models.BooleanField(default=False)
    # Use string reference to Team model to avoid circular import
    winner = models.ForeignKey('Team', null=True, blank=True, on_delete=models.SET_NULL, related_name='tournaments_won')

    def __str__(self):
        return self.name

    def get_team_standings(self):
        teams = Team.objects.filter(tournament=self)
        standings = []

        for team in teams:
            wins = 0
            points_won = 0
            points_lost = 0

            # Get all round robin matches for this team
            team1_matches = Match.objects.filter(team1=team, match_type='RR')
            team2_matches = Match.objects.filter(team2=team, match_type='RR')

            # Calculate wins and points for team1 matches
            for match in team1_matches:
                if match.played_at:
                    points_won += match.team1_score
                    points_lost += match.team2_score
                    if match.team1_score > match.team2_score:
                        wins += 1

            # Calculate wins and points for team2 matches
            for match in team2_matches:
                if match.played_at:
                    points_won += match.team2_score
                    points_lost += match.team1_score
                    if match.team2_score > match.team1_score:
                        wins += 1

            standings.append({
                'team': team,
                'wins': wins,
                'points_won': points_won,
                'points_lost': points_lost,
                'point_difference': points_won - points_lost
            })

        return sorted(standings,
                      key=lambda x: (x['wins'], x['point_difference']),
                      reverse=True)

    def start_knockout_stage(self):
        if not self.is_knockout_stage:
            standings = self.get_team_standings()[:4]
            if len(standings) < 3:
                return False

            if len(standings) == 3:
                Match.objects.create(
                    tournament=self,
                    team1=standings[0]['team'],
                    team2=standings[1]['team'],
                    match_type='F'
                )
                return True

            Match.objects.create(
                tournament=self,
                team1=standings[0]['team'],
                team2=standings[1]['team'],
                match_type='SF')
            Match.objects.create(
                tournament=self,
                team1=standings[2]['team'],
                team2=standings[3]['team'],
                match_type='SF'
            )
            Match.objects.create(
                tournament=self,
                team1='loser of sf1',
                team2='winner of sf2',
                match_type='SF'
            )
            Match.objects.create(
                tournament=self,
                team1='winner of sf1',
                team2='winner of sf3',
                match_type='F'
            )
            return True
        return False


class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team_player1')
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team_player2')

    def __str__(self):
        return f"{self.player1.name} & {self.player2.name}"


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1_matches')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2_matches')
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)
    played_at = models.DateTimeField(null=True, blank=True)
    match_type = models.CharField(max_length=2, choices=MATCH_TYPE_CHOICES, default='RR')

    def __str__(self):
        return f"{self.get_match_type_display()}: {self.team1} vs {self.team2}"

    def create_final_match(self):
        if self.match_type == 'SF' and self.played_at:
            other_semi = Match.objects.filter(
                tournament=self.tournament,
                match_type='SF'
            ).exclude(id=self.id).first()

            if other_semi and other_semi.played_at:
                winner1 = self.team1 if self.team1_score > self.team2_score else self.team2
                winner2 = other_semi.team1 if other_semi.team1_score > other_semi.team2_score else other_semi.team2

                Match.objects.create(
                    tournament=self.tournament,
                    team1=winner1,
                    team2=winner2,
                    match_type='F'
                )
                return True
        return False

    def update_tournament_winner(self):
        if self.match_type == 'F' and self.played_at:
            winner = self.team1 if self.team1_score > self.team2_score else self.team2
            self.tournament.winner = winner
            self.tournament.end_date = timezone.now()
            self.tournament.save()