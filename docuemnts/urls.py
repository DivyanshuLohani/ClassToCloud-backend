from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LectureViewSet, LectureView

router = DefaultRouter()
router.register(r'', LectureViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<str:c_uid>/', LectureView.as_view(), name="lecture_view")
]
