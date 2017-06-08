# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-07 18:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('boomerrang_app', '0002_auto_20170512_2330'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', phonenumber_field.modelfields.PhoneNumberField(max_length=128)),
                ('validated', models.NullBooleanField()),
                ('blacklisted', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='callrequest',
            name='source_num',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_number', to='boomerrang_app.PhoneNumber'),
        ),
    ]