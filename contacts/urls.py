from django.urls import path

from .views import (
    GenerateTemporaryIdsView
)

app_name = 'contacts'

urlpatterns = [
    path('temp_id', GenerateTemporaryIdsView.as_view()),
]