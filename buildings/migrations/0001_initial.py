# Generated by Django 4.1.1 on 2022-10-01 09:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Buildings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('location', models.IntegerField()),
            ],
            options={
                'db_table': 'buildings',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('nric', models.TextField(unique=True)),
                ('name', models.TextField()),
                ('dob', models.DateField()),
                ('email', models.TextField(blank=True, null=True)),
                ('phone', models.IntegerField()),
                ('gender', models.TextField()),
                ('address', models.TextField()),
                ('postal_code', models.TextField()),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Buildingaccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_timestamp', models.DateTimeField()),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='buildings.buildings')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='buildings.users')),
            ],
            options={
                'db_table': 'buildingaccess',
                'unique_together': {('user', 'building', 'access_timestamp')},
            },
        ),
    ]
