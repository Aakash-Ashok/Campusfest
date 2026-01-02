from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.forms import modelformset_factory


from .models import Event, Team, Participation, Result
from .forms import (
    EventForm,
    TeamForm,
    ParticipationForm,
    ResultForm,
    ParticipationFormSet,
)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('admin_dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


from django.db.models import Sum
from django.db.models.functions import Coalesce

@login_required
def admin_dashboard(request):
    points = (
        Team.objects
        .annotate(
            total_points=Coalesce(
                Sum('results__points'),
                0
            )
        )
        .values(
            'id',
            'team_name',
            'department',
            'total_points'
        )
        .order_by('-total_points', 'team_name')
    )

    return render(request, 'dashboard.html', {
        'points': points
    })



@login_required
def event_list(request):
    stage = request.GET.get('stage')

    events = Event.objects.all().order_by('stage_type', 'name')

    if stage in ['ON_STAGE', 'OFF_STAGE']:
        events = events.filter(stage_type=stage)

    return render(request, 'event_list.html', {
        'events': events,
        'selected_stage': stage
    })



@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully")
            return redirect('event_list')
    else:
        form = EventForm()

    return render(request, 'event_form.html', {'form': form})


@login_required
def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully")
            return redirect('event_list')
    else:
        form = EventForm(instance=event)

    return render(request, 'event_form.html', {'form': form})

@login_required
def event_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully")
        return redirect('event_list')

    return render(request, 'event_confirm_delete.html', {'event': event})


@login_required
def team_list(request):
    teams = Team.objects.all().order_by('department')
    return render(request, 'team_list.html', {'teams': teams})


@login_required
def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Team created successfully")
            return redirect('team_list')
    else:
        form = TeamForm()

    return render(request, 'team_form.html', {'form': form})


@login_required
def team_edit(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, "Team updated successfully")
            return redirect('team_list')
    else:
        form = TeamForm(instance=team)

    return render(request, 'team_form.html', {'form': form})


@login_required
def team_delete(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.method == 'POST':
        team.delete()
        messages.success(request, "Team deleted successfully")
        return redirect('team_list')

    return render(request, 'team_confirm_delete.html', {'team': team})



@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    participations = (
        Participation.objects
        .filter(team=team)
        .select_related('event')
        .order_by('event__name')
    )

    results = {
        r.event_id: r
        for r in Result.objects.filter(team=team)
    }

    # Group participants by event
    event_data = {}
    for p in participations:
        event = p.event
        if event.id not in event_data:
            event_data[event.id] = {
                'event': event,
                'participants': [],
                'result': results.get(event.id)
            }
        event_data[event.id]['participants'].append(p.participant_name)

    return render(request, 'team_detail.html', {
        'team': team,
        'event_data': event_data.values()
    })




from collections import defaultdict

@login_required
def participation_list(request):
    participations = Participation.objects.select_related(
        'event', 'team'
    ).order_by('event__name', 'team__team_name')

    grouped = defaultdict(list)

    for p in participations:
        key = (p.event, p.team)
        grouped[key].append(p.participant_name)

    grouped_data = [
        {
            'event': event,
            'team': team,
            'participants': names
        }
        for (event, team), names in grouped.items()
    ]

    return render(
        request,
        'participation_list.html',
        {'grouped_data': grouped_data}
    )



@login_required
def participation_add(request):
    event_id = request.GET.get('event')
    event = get_object_or_404(Event, id=event_id) if event_id else None

    # -------------------------
    # SINGLE EVENT
    # -------------------------
    if event and event.event_type == 'SINGLE':
        if request.method == 'POST':
            form = ParticipationForm(request.POST, event=event)
            if form.is_valid():
                participation = form.save(commit=False)
                participation.event = event  # force event
                participation.save()
                messages.success(request, "Participant added successfully")
                return redirect('participation_list')
        else:
            form = ParticipationForm(event=event)

        return render(
            request,
            'participation_single_form.html',
            {
                'form': form,
                'event': event
            }
        )

    # -------------------------
    # GROUP EVENT
    # -------------------------
    if event and event.event_type == 'GROUP':
        teams = Team.objects.all()

        ParticipationFormSet = modelformset_factory(
            Participation,
            form=ParticipationForm,
            extra=event.max_team_size,
            can_delete=False
        )

        if request.method == 'POST':
            team_id = request.POST.get('team')
            team = get_object_or_404(Team, id=team_id)

            formset = ParticipationFormSet(
                request.POST,
                queryset=Participation.objects.none(),
                form_kwargs={
                    'event': event,
                    'team': team
                }
            )

            if formset.is_valid():
                participations = formset.save(commit=False)

                # remove empty name rows
                participations = [
                    p for p in participations if p.participant_name
                ]

                # ❌ below minimum
                if len(participations) < event.min_team_size:
                    messages.error(
                        request,
                        f"Minimum {event.min_team_size} participants required."
                    )
                    return render(
                        request,
                        'participation_group_form.html',
                        {
                            'formset': formset,
                            'event': event,
                            'teams': teams
                        }
                    )

                # ✅ save valid participants
                for p in participations:
                    p.event = event
                    p.team = team
                    p.save()

                messages.success(
                    request,
                    "Group participants added successfully"
                )
                return redirect('participation_list')

        else:
            formset = ParticipationFormSet(
                queryset=Participation.objects.none(),
                form_kwargs={
                    'event': event,
                    'team': None
                }
            )

        return render(
            request,
            'participation_group_form.html',
            {
                'formset': formset,
                'event': event,
                'teams': teams
            }
        )

    # -------------------------
    # FALLBACK
    # -------------------------
    messages.error(request, "Please select a valid event")
    return redirect('participation_list')






@login_required
def participation_edit(request, event_id, team_id):
    event = get_object_or_404(Event, id=event_id)
    team = get_object_or_404(Team, id=team_id)

    queryset = Participation.objects.filter(event=event, team=team)

    # -------------------------
    # SINGLE EVENT
    # -------------------------
    if event.event_type == 'SINGLE':
        participation = queryset.first()

        if request.method == 'POST':
            form = ParticipationForm(
                request.POST,
                instance=participation,
                event=event,
                team=team
            )
            if form.is_valid():
                participation = form.save(commit=False)
                participation.event = event
                participation.team = team
                participation.save()

                messages.success(request, "Participation updated successfully")
                return redirect('participation_list')
        else:
            form = ParticipationForm(
                instance=participation,
                event=event,
                team=team
            )

        return render(
            request,
            'participation_edit.html',
            {
                'form': form,
                'event': event,
                'team': team
            }
        )

    # -------------------------
    # GROUP EVENT
    # -------------------------
    ParticipationFormSet = modelformset_factory(
        Participation,
        form=ParticipationForm,
        extra=0,
        can_delete=True
    )

    if request.method == 'POST':
        formset = ParticipationFormSet(
            request.POST,
            queryset=queryset,
            form_kwargs={
                'event': event,
                'team': team
            }
        )

        if formset.is_valid():
            participations = formset.save(commit=False)

            for obj in formset.deleted_objects:
                obj.delete()

            for p in participations:
                p.event = event
                p.team = team
                p.save()

            messages.success(
                request,
                "Group participation updated successfully"
            )
            return redirect('participation_list')

    else:
        formset = ParticipationFormSet(
            queryset=queryset,
            form_kwargs={
                'event': event,
                'team': team
            }
        )

    return render(
        request,
        'participation_edit.html',
        {
            'formset': formset,
            'event': event,
            'team': team
        }
    )



@login_required
def participation_delete(request, participation_id):
    participation = get_object_or_404(Participation, id=participation_id)

    if request.method == 'POST':
        participation.delete()
        messages.success(request, "Participation deleted successfully")
        return redirect('participation_list')

    return render(
        request,
        'participation_confirm_delete.html',
        {'participation': participation}
    )





@login_required
def result_list(request):
    results = Result.objects.select_related(
        'event', 'team'
    ).order_by('event__name', 'position')

    return render(request, 'result_list.html', {'results': results})


@login_required
def result_add(request):
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Result added successfully")
            return redirect('result_list')
    else:
        form = ResultForm()

    return render(request, 'result_form.html', {'form': form})


@login_required
def result_edit(request, result_id):
    result = get_object_or_404(Result, id=result_id)

    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, "Result updated successfully")
            return redirect('result_list')
    else:
        form = ResultForm(instance=result)

    return render(request, 'result_form.html', {'form': form})


@login_required
def result_delete(request, result_id):
    result = get_object_or_404(Result, id=result_id)

    if request.method == 'POST':
        result.delete()
        messages.success(request, "Result deleted successfully")
        return redirect('result_list')

    return render(
        request,
        'result_confirm_delete.html',
        {'result': result}
    )



def public_index(request):
    points = (
        Team.objects
        .annotate(
            total_points=Coalesce(
                Sum('results__points'),
                0
            )
        )
        .values(
            'id',
            'team_name',
            'department',
            'total_points'
        )
        .order_by('-total_points', 'team_name')
    )

    return render(request, 'index.html', {
        'points': points
    })



def public_event_list(request):
    events = Event.objects.all().order_by('stage_type', 'name')
    return render(request, 'pevent_list.html', {'events': events})


def public_event_result(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    results = Result.objects.filter(
        event=event
    ).select_related('team').order_by('position')

    participants = Participation.objects.filter(
        event=event
    ).select_related('team')

    return render(
        request,
        'pevent_result.html',
        {
            'event': event,
            'results': results,
            'participants': participants,
        }
    )



from django.shortcuts import get_object_or_404

def public_team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    participations = (
        Participation.objects
        .filter(team=team)
        .select_related('event')
        .order_by('event__name')
    )

    results = {
        r.event_id: r
        for r in Result.objects.filter(team=team)
    }

    event_data = {}
    for p in participations:
        event = p.event
        if event.id not in event_data:
            event_data[event.id] = {
                'event': event,
                'participants': [],
                'result': results.get(event.id)
            }
        event_data[event.id]['participants'].append(p.participant_name)

    return render(request, 'public_team_detail.html', {
        'team': team,
        'event_data': event_data.values()
    })




def points_table(request):
    points = (
        Result.objects
        .values('team__team_name', 'team__department')
        .annotate(total_points=Sum('points'))
        .order_by('-total_points')
    )

    return render(request, 'points_table.html', {
        'points': points
    })


from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from .models import Event, Result, Participation


@login_required
def event_result_pdf(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    results = (
        Result.objects
        .filter(event=event)
        .select_related('team')
        .order_by('position')
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{event.name}_Results.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    LEFT = 60
    TOP = height - 80
    LINE = 16
    y = TOP

    # ================= HEADER =================
    p.setFont("Times-Bold", 20)
    p.setFillColor(colors.black)
    p.drawCentredString(width / 2, y, f"{event.name} – Result Sheet")
    y -= 24

    p.setFont("Times-Italic", 11)
    p.setFillColor(colors.grey)
    p.drawCentredString(
        width / 2,
        y,
        f"{event.stage_type} | {event.event_type}"
    )
    y -= 20

    p.setStrokeColor(colors.lightgrey)
    p.line(LEFT, y, width - LEFT, y)
    y -= 30

    # ================= RESULTS =================
    for r in results:

        if y < 120:
            # Footer before page break
            p.setFont("Times-Italic", 9)
            p.setFillColor(colors.grey)
            p.drawCentredString(
                width / 2, 40,
                f"Generated on {now().strftime('%d %B %Y')} | Campus Fest"
            )

            p.showPage()
            y = TOP

            # Repeat header on new page
            p.setFont("Times-Bold", 18)
            p.setFillColor(colors.black)
            p.drawCentredString(width / 2, y, f"{event.name} – Result Sheet")
            y -= 30

        # Position + Team
        p.setFont("Times-Bold", 13)
        p.setFillColor(colors.black)
        p.drawString(
            LEFT,
            y,
            f"{r.position}. {r.team.team_name}"
        )
        y -= LINE

        # Participants
        members = Participation.objects.filter(
            event=event,
            team=r.team
        )

        p.setFont("Times-Roman", 11)
        for m in members:
            p.drawString(
                LEFT + 20,
                y,
                f"• {m.participant_name}"
            )
            y -= LINE - 2

        y -= 10  # spacing between teams

    # ================= FOOTER =================
    p.setFont("Times-Italic", 9)
    p.setFillColor(colors.grey)
    p.drawCentredString(
        width / 2, 40,
        f"Generated on {now().strftime('%d %B %Y')} | Campus Fest Management System"
    )

    p.showPage()
    p.save()
    return response



from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required

from .models import Team, Participation, Result


@login_required
def team_participation_pdf(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    participations = (
        Participation.objects
        .filter(team=team)
        .select_related('event')
        .order_by('event__name')
    )

    results = {
        r.event_id: r
        for r in Result.objects.filter(team=team)
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{team.team_name}_Participation_Report.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    LEFT = 60
    TOP = height - 80
    LINE = 16
    y = TOP

    # ================= HEADER =================
    p.setFont("Times-Bold", 20)
    p.setFillColor(colors.black)
    p.drawCentredString(width / 2, y, "Team Participation Report")
    y -= 24

    p.setFont("Times-Italic", 11)
    p.setFillColor(colors.grey)
    p.drawCentredString(
        width / 2,
        y,
        f"{team.team_name} | {team.department}"
    )
    y -= 20

    p.setStrokeColor(colors.lightgrey)
    p.line(LEFT, y, width - LEFT, y)
    y -= 30

    # ================= CONTENT =================
    current_event = None

    if not participations.exists():
        p.setFont("Times-Roman", 12)
        p.drawString(LEFT, y, "No participation records found for this team.")
        y -= LINE

    for part in participations:

        # New event block
        if current_event != part.event:
            current_event = part.event

            if y < 140:
                # Footer before page break
                p.setFont("Times-Italic", 9)
                p.setFillColor(colors.grey)
                p.drawCentredString(
                    width / 2, 40,
                    f"Generated on {now().strftime('%d %B %Y')} | Campus Fest Management System"
                )

                p.showPage()
                y = TOP

                # Repeat header
                p.setFont("Times-Bold", 18)
                p.setFillColor(colors.black)
                p.drawCentredString(width / 2, y, "Team Participation Report")
                y -= 30

            # Event title
            p.setFont("Times-Bold", 14)
            p.setFillColor(colors.black)
            p.drawString(LEFT, y, current_event.name)
            y -= LINE

            # Event meta
            p.setFont("Times-Italic", 11)
            p.setFillColor(colors.grey)
            p.drawString(
                LEFT + 10,
                y,
                f"{current_event.stage_type} | {current_event.event_type}"
            )
            y -= LINE

            # Result info
            result = results.get(current_event.id)
            p.setFont("Times-Roman", 11)
            p.setFillColor(colors.black)
            p.drawString(
                LEFT + 10,
                y,
                f"Result: {f'Position {result.position}, {result.points} points' if result else 'Not Published'}"
            )
            y -= LINE

            p.drawString(LEFT + 10, y, "Participants:")
            y -= LINE

        # Participant name
        p.setFont("Times-Roman", 11)
        p.drawString(
            LEFT + 30,
            y,
            f"• {part.participant_name}"
        )
        y -= LINE - 2

    # ================= FOOTER =================
    p.setFont("Times-Italic", 9)
    p.setFillColor(colors.grey)
    p.drawCentredString(
        width / 2, 40,
        f"Generated on {now().strftime('%d %B %Y')} | Campus Fest Management System"
    )

    p.showPage()
    p.save()
    return response



import io
import zipfile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

from .models import Result, Participation

\
def _draw_certificate(p, width, height, name, team, event, position, points):
    """
    Professional, institutional certificate design
    """

    PRIMARY = HexColor("#1f2937")
    ACCENT = HexColor("#2563eb")
    LIGHT = HexColor("#f8fafc")
    MUTED = HexColor("#6b7280")

    # ================= LIGHT GRADIENT HEADER =================
    for i in range(40):
        shade = 0.96 - (i * 0.003)
        p.setFillColorRGB(shade, shade + 0.01, 1)
        p.rect(0, height - (i * 10), width, 10, fill=1, stroke=0)

    # ================= BORDER =================
    p.setStrokeColor(PRIMARY)
    p.setLineWidth(3)
    p.rect(40, 40, width - 80, height - 80)

    # ================= TITLE =================
    p.setFillColor(PRIMARY)
    p.setFont("Times-Bold", 30)
    p.drawCentredString(width / 2, height - 160, "Certificate of Achievement")

    p.setFont("Times-Italic", 13)
    p.setFillColor(MUTED)
    p.drawCentredString(
        width / 2,
        height - 195,
        "This certificate is proudly presented to"
    )

    # ================= NAME =================
    p.setFont("Times-Bold", 26)
    p.setFillColor(colors.black)
    p.drawCentredString(width / 2, height - 250, name)

    # ================= TEAM INFO =================
    p.setFont("Times-Roman", 14)
    p.setFillColor(colors.black)
    p.drawCentredString(
        width / 2,
        height - 290,
        f"Team {team.team_name} — Department of {team.department}"
    )

    # ================= ACHIEVEMENT =================
    p.setFont("Times-Roman", 15)
    p.drawCentredString(
        width / 2,
        height - 330,
        f"For securing {position} Position"
    )

    p.setFont("Times-Bold", 17)
    p.drawCentredString(
        width / 2,
        height - 360,
        f"in the event “{event.name}”"
    )

    p.setFont("Times-Italic", 13)
    p.setFillColor(MUTED)
    p.drawCentredString(
        width / 2,
        height - 395,
        f"Awarded with {points} points"
    )

    # ================= SIGNATURES =================
    p.setFillColor(colors.black)
    p.setFont("Times-Roman", 12)

    p.drawString(90, 140, "________________________")
    p.drawString(105, 120, "Event Coordinator")

    p.drawString(width - 290, 140, "________________________")
    p.drawString(width - 260, 120, "Principal / Head")

    # ================= FOOTER =================
    p.setFont("Times-Italic", 10)
    p.setFillColor(MUTED)
    p.drawCentredString(
        width / 2,
        90,
        f"Issued on {now().strftime('%d %B %Y')} | Campus Fest"
    )


@login_required
def generate_winner_certificate(request, result_id):
    result = get_object_or_404(Result, id=result_id)

    event = result.event
    team = result.team
    position = result.position
    points = result.points

    participants = Participation.objects.filter(
        event=event,
        team=team
    )

    # =====================================================
    # 🔹 CASE 1: SINGLE EVENT → ONE PDF
    # =====================================================
    if event.event_type == 'SINGLE':
        participant = participants.first()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{participant.participant_name}_{event.name}_Certificate.pdf"'
        )

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        _draw_certificate(
            p, width, height,
            participant.participant_name,
            team, event, position, points
        )

        p.showPage()
        p.save()
        return response

    # =====================================================
    # 🔹 CASE 2: GROUP EVENT → MULTIPLE PDFs (ZIP)
    # =====================================================
    zip_buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED)

    for member in participants:
        pdf_buffer = io.BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4

        _draw_certificate(
            p, width, height,
            member.participant_name,
            team, event, position, points
        )

        p.showPage()
        p.save()
        pdf_buffer.seek(0)

        filename = f"{member.participant_name}_{event.name}_Certificate.pdf"
        zip_file.writestr(filename, pdf_buffer.read())

    zip_file.close()
    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = (
        f'attachment; filename="{team.team_name}_{event.name}_Certificates.zip"'
    )

    return response


from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.utils.timezone import now

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart

from .models import Event, Team, Participation, Result


@login_required
def fest_full_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="CampusFest_Full_Report.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    LEFT = 60
    RIGHT = 60
    TOP = height - 80
    LINE = 18

    # =====================================================
    # COVER PAGE (SOFT GRADIENT)
    # =====================================================
    for i in range(80):
        shade = 0.97 - (i * 0.002)
        p.setFillColorRGB(shade, shade + 0.01, 1)
        p.rect(0, height - (i * 10), width, 10, fill=1, stroke=0)

    p.setFillColor(colors.black)
    p.setFont("Times-Bold", 32)
    p.drawCentredString(width / 2, height / 2 + 60, "CAMPUS FEST")

    p.setFont("Times-Roman", 18)
    p.drawCentredString(width / 2, height / 2 + 25, "Comprehensive Fest Report")

    p.setFont("Times-Italic", 12)
    p.drawCentredString(
        width / 2,
        height / 2 - 10,
        f"Generated on {now().strftime('%d %B %Y')}"
    )

    p.showPage()

    # =====================================================
    # COMMON FOOTER
    # =====================================================
    def footer():
        p.setFont("Times-Italic", 9)
        p.setFillColor(colors.grey)
        p.drawCentredString(
            width / 2, 40,
            "Campus Fest Management System"
        )

    # =====================================================
    # SECTION TITLE
    # =====================================================
    def section(title, y):
        p.setFont("Times-Bold", 22)
        p.setFillColor(colors.black)
        p.drawString(LEFT, y, title)
        y -= 10
        p.setStrokeColor(colors.lightgrey)
        p.line(LEFT, y, width - RIGHT, y)
        return y - 25

    # =====================================================
    # FEST OVERVIEW
    # =====================================================
    y = TOP
    y = section("Fest Overview", y)

    total_events = Event.objects.count()
    total_teams = Team.objects.count()
    total_participants = Participation.objects.count()

    p.setFont("Times-Roman", 13)
    p.drawString(LEFT + 20, y, f"• Total Events        : {total_events}")
    y -= LINE
    p.drawString(LEFT + 20, y, f"• Total Teams         : {total_teams}")
    y -= LINE
    p.drawString(LEFT + 20, y, f"• Total Participants  : {total_participants}")

    footer()
    p.showPage()

    # =====================================================
    # EVENT SECTIONS
    # =====================================================
    def event_section(title, stage):
        y = TOP
        y = section(title, y)

        events = (
            Event.objects
            .filter(stage_type=stage)
            .annotate(team_count=Count('participations__team', distinct=True))
            .order_by('name')
        )

        for e in events:
            if y < 120:
                footer()
                p.showPage()
                y = TOP
                y = section(title, y)

            p.setFont("Times-Bold", 14)
            p.drawString(LEFT + 10, y, e.name)
            y -= LINE - 2

            p.setFont("Times-Roman", 12)
            p.drawString(
                LEFT + 30, y,
                f"{e.event_type} | Teams Participated: {e.team_count}"
            )
            y -= LINE

        footer()
        p.showPage()

    event_section("On-Stage Events Summary", "ON_STAGE")
    event_section("Off-Stage Events Summary", "OFF_STAGE")

    # =====================================================
    # TEAM PERFORMANCE
    # =====================================================
    y = TOP
    y = section("Team Performance Summary", y)

    teams = (
        Team.objects
        .annotate(total_points=Coalesce(Sum('results__points'), 0))
        .order_by('-total_points')
    )

    rank = 1
    for t in teams:
        if y < 100:
            footer()
            p.showPage()
            y = TOP
            y = section("Team Performance Summary", y)

        p.setFont("Times-Roman", 12)
        p.drawString(
            LEFT + 20, y,
            f"{rank}. {t.team_name} ({t.department}) — {t.total_points} points"
        )
        y -= LINE
        rank += 1

    footer()
    p.showPage()

    # =====================================================
    # GRAPH PAGE (CLEAN CARD STYLE)
    # =====================================================
    p.setFont("Times-Bold", 22)
    p.drawString(LEFT, TOP, "Top Teams – Points Distribution")

    # Card background
    p.setFillColor(colors.whitesmoke)
    p.rect(LEFT - 10, TOP - 320, width - 2 * LEFT + 20, 260, fill=1, stroke=0)

    top = teams[:6]
    data = [[t.total_points for t in top]]
    labels = [t.team_name[:10] for t in top]

    drawing = Drawing(420, 240)
    chart = VerticalBarChart()
    chart.x = 60
    chart.y = 40
    chart.height = 180
    chart.width = 320
    chart.data = data
    chart.categoryAxis.categoryNames = labels
    chart.valueAxis.valueMin = 0
    chart.bars[0].fillColor = colors.Color(0.2, 0.4, 0.7)

    drawing.add(chart)
    drawing.drawOn(p, LEFT, TOP - 300)

    footer()
    p.showPage()

    # =====================================================
    # EVENT WINNERS
    # =====================================================
    y = TOP
    y = section("Event Winners", y)

    results = Result.objects.order_by('event__name', 'position')
    current_event = None

    for r in results:
        if current_event != r.event:
            current_event = r.event

            if y < 120:
                footer()
                p.showPage()
                y = TOP
                y = section("Event Winners", y)

            p.setFont("Times-Bold", 14)
            p.drawString(LEFT + 10, y, current_event.name)
            y -= LINE - 2

        p.setFont("Times-Roman", 12)
        p.drawString(
            LEFT + 30, y,
            f"Position {r.position}: {r.team.team_name} ({r.points} points)"
        )
        y -= LINE

    footer()
    p.showPage()
    p.save()
    return response
