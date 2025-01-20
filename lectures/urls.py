from django.urls import path, include
from .views import LectureUploadInitializeView, LectureUploadChunkView, LectureUploadCompleteView, LectureView


urlpatterns = [
    path('', LectureUploadInitializeView.as_view(), name="lecture_create"),
    path('chunk/', LectureUploadChunkView.as_view(), name="lecture_chunk"),
    path('complete/', LectureUploadCompleteView.as_view(), name="lecture_complete"),
    path('<str:c_uid>', LectureView.as_view(), name="lecture_view")
]
