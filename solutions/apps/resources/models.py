from django.db import models


class Resource(models.Model):

    pmid = models.PositiveIntegerField(
        primary_key=True,
    )

    date_created = models.DateField(
        blank=True,
        null=True,
    )

    date_revised = models.DateField(
        blank=True,
        null=True,
    )
