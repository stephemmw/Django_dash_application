from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.data_analysis_view, name='data_analysis'),
    path('fetch_column_data/', views.fetch_column_data, name='fetch_column_data'),
    path('load_data_view/', views.load_data_view, name='load_data_view'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]

