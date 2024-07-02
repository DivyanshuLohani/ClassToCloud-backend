from django.urls import path
from .views import GetBatches, GetSubjects, GetChapters

urlpatterns = [
    path("batches/", GetBatches.as_view(), name="get_batches"),
    path("batches/<str:batch_id>", GetSubjects.as_view(), name="batchView"),
]
