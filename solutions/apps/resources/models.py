from django.db import models


class SearchResult(models.Model):

    term = models.CharField(
        max_length=100,
    )

    year = models.PositiveIntegerField()

    num_results = models.IntegerField()
