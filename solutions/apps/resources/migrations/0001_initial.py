# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('pmid', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('date_created', models.DateField(null=True, blank=True)),
                ('date_revised', models.DateField(null=True, blank=True)),
            ],
        ),
    ]
