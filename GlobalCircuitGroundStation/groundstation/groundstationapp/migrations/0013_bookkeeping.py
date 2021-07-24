# Generated by Django 2.2.2 on 2021-06-08 21:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groundstationapp', '0012_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookKeeping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_id', models.IntegerField()),
                ('GPSSats', models.IntegerField()),
                ('RBSig', models.IntegerField()),
                ('Commands', models.IntegerField()),
                ('AltTemp', models.IntegerField()),
                ('AltPress', models.IntegerField()),
                ('VbatP', models.IntegerField()),
                ('VbatM', models.IntegerField()),
                ('ThreeVSix', models.IntegerField()),
                ('SevenV_I', models.IntegerField()),
                ('ThreeThreeV_I', models.IntegerField()),
                ('Tbat', models.IntegerField()),
                ('Tcomp', models.IntegerField()),
                ('Tmag', models.IntegerField()),
                ('Tadc1', models.IntegerField()),
                ('Tadc2', models.IntegerField()),
                ('Trock', models.IntegerField()),
                ('Text', models.TextField()),
                ('RBIMEI', models.IntegerField()),
                ('global_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groundstationapp.Packet')),
            ],
        ),
    ]