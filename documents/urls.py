from django.urls import path
from .views import CreateNotesView, NotesView, CreateDPPView, DPPView

urlpatterns = [
    path('notes/', CreateNotesView.as_view(), name="notes_create"),
    path('notes/<str:uid>/', NotesView.as_view(), name="notes_view"),
    path('dpps/', CreateDPPView.as_view(), name="dpp_create"),
    path('dpps/<str:uid>/', DPPView.as_view(), name="dpp_view"),
]
