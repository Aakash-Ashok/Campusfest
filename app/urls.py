from django.urls import path
from . import views

urlpatterns = [

    # --------------------
    # AUTH
    # --------------------
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("create-superuser/", views.create_superuser_once),


    # --------------------
    # ADMIN DASHBOARD
    # --------------------
    path('ad/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # --------------------
    # EVENT MANAGEMENT
    # --------------------
    path('ad/events/', views.event_list, name='event_list'),
    path('ad/events/add/', views.event_create, name='event_create'),
    path('ad/events/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('ad/events/<int:event_id>/delete/', views.event_delete, name='event_delete'),

    # --------------------
    # TEAM MANAGEMENT
    # --------------------
    path('ad/teams/', views.team_list, name='team_list'),
    path('ad/teams/add/', views.team_create, name='team_create'),
    path('ad/teams/<int:team_id>/edit/', views.team_edit, name='team_edit'),
    path('ad/teams/<int:team_id>/delete/', views.team_delete, name='team_delete'),

    # --------------------
    # PARTICIPATION
    # --------------------
    path('ad/participations/', views.participation_list, name='participation_list'),
    path('ad/participations/add/', views.participation_add, name='participation_add'),
    path(
    'ad/participations/<int:event_id>/<int:team_id>/edit/',
    views.participation_edit,
    name='participation_edit'
    ),

    path(
    'ad/participations/<int:event_id>/<int:team_id>/delete/',
    views.participation_delete,
    name='participation_delete'
    ),

    # --------------------
    # RESULTS
    # --------------------
    path('ad/results/', views.result_list, name='result_list'),
    path('ad/results/add/', views.result_add, name='result_add'),
    path('ad/results/<int:result_id>/edit/', views.result_edit, name='result_edit'),
    path('ad/results/<int:result_id>/delete/', views.result_delete, name='result_delete'),
    path(
    'ad/teams/<int:team_id>/pdf/',
    views.team_participation_pdf,
    name='team_participation_pdf'
    ),
    path(
    'ad/results/<int:result_id>/certificate/',
    views.generate_winner_certificate,
    name='winner_certificate'
    ),
    path(
    'ad/events/<int:event_id>/pdf/',
    views.event_result_pdf,
    name='event_result_pdf'
    ),
    path(
    'ad/teams/<int:team_id>/',
    views.team_detail,
    name='team_detail'
),

path(
    'ad/reports/fest/',
    views.fest_full_report,
    name='fest_full_report'
),





    # --------------------
    # PUBLIC
    # --------------------
    path('', views.public_index, name='public_index'),
    path('pevents/', views.public_event_list, name='public_event_list'),
    path('event/<int:event_id>/', views.public_event_result, name='public_event_result'),
    path('points/', views.points_table, name='points_table'),
    path(
    'team/<int:team_id>/',
    views.public_team_detail,
    name='public_team_detail'
),

    


]
