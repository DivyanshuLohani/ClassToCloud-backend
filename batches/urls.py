from django.urls import path
from .views import GetBatches, GetSubjects, GetChapters, CreateBatch, CreateSubject, CreateChapter

urlpatterns = [
    path("", GetBatches.as_view(), name="get_batches"),
    path("<str:batch_id>/", GetSubjects.as_view(), name="batch_view"),
    path("subjects/str:subject_id/", GetChapters.as_view(), name="chapters_view"),

    path("create/", CreateBatch.as_view(), "create_batch"),
    path("subjects/", CreateSubject.as_view(), "create_subject"),
    path("chapters/", CreateChapter.as_view(), "create_chapter"),
]
