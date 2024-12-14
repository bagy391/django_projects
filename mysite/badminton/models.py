# models.py
from django.db import models
from django.utils import timezone

MATCH_TYPE_CHOICES = [
    ('RR', 'Round Robin'),
    ('Q', 'Qualifier'),
    ('E', 'Eliminator'),
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
    TYPE_CHOICES = [
        ('Qualifier/Eliminator', 'Qualifier/Eliminator'),
        ('1V4|2V3', '1V4|2V3')
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Qualifier/Eliminator')
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
            if self.type == '1V4|2V3':
                Match.objects.create(
                    tournament=self,
                    team1=standings[0]['team'],
                    team2=standings[3]['team'],
                    match_type='SF')
                Match.objects.create(
                    tournament=self,
                    team1=standings[1]['team'],
                    team2=standings[2]['team'],
                    match_type='SF'
                )
            else:
                Match.objects.create(
                    tournament=self,
                    team1=standings[0]['team'],
                    team2=standings[1]['team'],
                    match_type='Q')
                Match.objects.create(
                    tournament=self,
                    team1=standings[2]['team'],
                    team2=standings[3]['team'],
                    match_type='E'
                )
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

    @property
    def winner(self):
        if int(self.team1_score) > int(self.team2_score):
            return self.team1
        return self.team2

    def __str__(self):
        return f"{self.get_match_type_display()}: {self.team1} vs {self.team2}"

    def create_semis(self):
        if self.match_type == 'E' and self.played_at:
            qualifier = Match.objects.filter(
                tournament=self.tournament,
                match_type='Q'
            ).first()
            if qualifier.played_at:
                lost_team = qualifier.team2 if qualifier.winner == qualifier.team1 else qualifier.team1
                Match.objects.create(
                    tournament=self.tournament,
                    team1=lost_team,
                    team2=self.winner,
                    match_type='SF'
                )

    def check_semis(self):
        if self.match_type == 'Q' and self.played_at:
            eliminator_match = Match.objects.filter(
                tournament=self.tournament,
                match_type='E'
            ).first()
            lost_team = self.team2 if self.winner == self.team1 else self.team1
            if eliminator_match.played_at:
                Match.objects.create(
                    tournament=self.tournament,
                    team1=lost_team,
                    team2=eliminator_match.winner,
                    match_type='SF'
                )

    def create_final_match(self):
        if self.tournament.type == '1V4|2V3':
            if all(m.played_at for m in Match.objects.filter(tournament=self.tournament, match_type='SF')):
                Match.objects.create(
                    tournament=self.tournament,
                    team1=Match.objects.filter(tournament=self.tournament, match_type='SF').first().winner,
                    team2=Match.objects.filter(tournament=self.tournament, match_type='SF').last().winner,
                    match_type='F'
                )
        elif self.played_at:
            qualifier_winner = Match.objects.filter(
                tournament=self.tournament,
                match_type='Q'
            ).first().winner
            Match.objects.create(
                tournament=self.tournament,
                team1=qualifier_winner,
                team2=self.winner,
                match_type='F'
            )
        return False

    def update_tournament_winner(self):
        if self.match_type == 'F' and self.played_at:
            winner = self.winner
            self.tournament.winner = winner
            self.tournament.end_date = timezone.now()
            self.tournament.save()