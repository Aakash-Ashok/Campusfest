from django import forms
from django.core.exceptions import ValidationError

from .models import Event, Team, Participation, Result


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name',
            'stage_type',
            'event_type',
            'min_team_size',
            'max_team_size',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'stage_type': forms.Select(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'min_team_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_team_size': forms.NumberInput(attrs={'class': 'form-control'}),
        }



class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'team_name',
            'department',
        ]






class ParticipationForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = ['event', 'team', 'participant_name']

    def __init__(self, *args, **kwargs):
        self.fixed_event = kwargs.pop('event', None)
        self.fixed_team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)

        if self.fixed_event:
            self.fields['event'].disabled = True
            self.initial['event'] = self.fixed_event

        # 🔒 Hide team field for GROUP forms
        if self.fixed_team:
            self.fields['team'].disabled = True
            self.initial['team'] = self.fixed_team

    def clean(self):
        cleaned_data = super().clean()

        # Always resolve event & team safely
        event = self.fixed_event or cleaned_data.get('event')
        team = self.fixed_team or cleaned_data.get('team')

        if not event or not team:
            return cleaned_data




from django.forms import modelformset_factory


ParticipationFormSet = modelformset_factory(
    Participation,
    form=ParticipationForm,
    extra=3,          # number of participant rows shown initially
    can_delete=False
)


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = [
            'event',
            'team',
            'position',
            'points',
        ]

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get('event')
        team = cleaned_data.get('team')

        if event and team:
            # Ensure team actually participated in the event
            participated = Participation.objects.filter(
                event=event,
                team=team
            ).exists()

            if not participated:
                raise ValidationError(
                    "This team has not participated in the selected event."
                )

        return cleaned_data
