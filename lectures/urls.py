from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LectureViewSet

router = DefaultRouter()
router.register(r'', LectureViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('upload/', VideoChunkedUploadView.as_view(), name='chunked_upload'),
    # path('upload/complete/', VideoChunkedUploadCompleteView.as_view(),
    #  name='chunked_upload_complete'),
]
