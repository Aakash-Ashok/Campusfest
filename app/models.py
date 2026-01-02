from django.db import models


class Event(models.Model):
    STAGE_TYPE_CHOICES = (
        ('ON_STAGE', 'On Stage'),
        ('OFF_STAGE', 'Off Stage'),
    )

    EVENT_TYPE_CHOICES = (
        ('SINGLE', 'Single'),
        ('GROUP', 'Group'),
    )

    name = models.CharField(max_length=200, unique=True)
    stage_type = models.CharField(
        max_length=10,
        choices=STAGE_TYPE_CHOICES
    )
    event_type = models.CharField(
        max_length=10,
        choices=EVENT_TYPE_CHOICES
    )
    min_team_size = models.PositiveIntegerField(default=1)
    max_team_size = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class Team(models.Model):
    team_name = models.CharField(max_length=150)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.team_name} ({self.department})"


class Participation(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    participant_name = models.CharField(max_length=150)

    class Meta:
        unique_together = ('event', 'team', 'participant_name')

    def __str__(self):
        return f"{self.participant_name} - {self.team.team_name}"


class Result(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='results'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='results'
    )
    position = models.PositiveIntegerField()
    points = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('event', 'team')
        ordering = ['position']

    def __str__(self):
        return f"{self.event.name} - {self.team.team_name} (Position {self.position})"
