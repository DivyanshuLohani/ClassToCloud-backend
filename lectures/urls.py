from django.urls import path, include
from .views import LectureCreateView, LectureView

urlpatterns = [
    path('', LectureCreateView.as_view(), name="lecture_create"),
    path('<str:c_uid>', LectureView.as_view(), name="lecture_view")
]
