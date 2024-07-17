from django.urls import path
from .views import (
    GetBatches,
    GetSubjects,
    GetChapters,

    CreateBatch,
    CreateSubject,
    CreateChapter,

    ListChapterNotes,
    ListChapterDPPs,
    ListChapterLectures
)

urlpatterns = [
    path("", GetBatches.as_view(), name="get_batches"),
    path("<str:batch_id>/", GetSubjects.as_view(), name="batch_view"),
    path("subjects/<str:subject_id>/",
         GetChapters.as_view(), name="chapters_view"),

    path("create/", CreateBatch.as_view(), name="create_batch"),
    path("subjects/", CreateSubject.as_view(), name="create_subject"),
    path("chapters/", CreateChapter.as_view(), name="create_chapter"),

    path("chapters/<str:uid>/notes/",
         ListChapterNotes.as_view(), name="notes_list_view"),
    path("chapters/<str:uid>/dpps/",
         ListChapterDPPs.as_view(), name="dpps_list_view"),
    path("chapters/<str:uid>/lectures/",
         ListChapterLectures.as_view(), name="lectures_list_view"),
]
