
from django.urls import path
from . import views
urlpatterns = [
    path('get/predict/<int:year>/<int:month>/<int:day>',views.predict_view, name='predict' ),
    path('get/<str:vegetable_name>/overview', views.vegetable_summary_view, name='vegetable_summary'),
    path('get/<str:vegetable_name>/all', views.vegetable_monthly_summary_view, name='vegetable_monthly_summary_view'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('calendar/<str:username>', views.calendar_list_view),
    path('calendar/<str:username>/planted_date/harvested_date/expense/earn/profit', views.calendar_list_view),
    path('create-calendar/', views.create_calendar, name='create-calendar'),
    path('calendar/<str:username>/<int:pk>/delete/', views.delete_calendar, name='calendar-delete'),
    path('calendar/update/<str:username>/<int:pk>/', views.update_crop_calendar, name='update_crop_calendar'),
]
