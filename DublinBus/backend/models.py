# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models



class Touristattractions(models.Model):
    name = models.CharField(primary_key=True, max_length=75)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    raters = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    visiting_time = models.IntegerField(blank=True, null=True)
    image = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'TouristAttractions'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Calendar(models.Model):
    service_id = models.CharField(primary_key=True, max_length=45)
    start_date = models.TextField(blank=True, null=True)
    end_date = models.TextField(blank=True, null=True)
    monday = models.TextField(blank=True, null=True)
    tuesday = models.TextField(blank=True, null=True)
    wednesday = models.TextField(blank=True, null=True)
    thursday = models.TextField(blank=True, null=True)
    friday = models.TextField(blank=True, null=True)
    saturday = models.TextField(blank=True, null=True)
    sunday = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'calendar'


class CalendarDates(models.Model):
    service = models.ForeignKey(Calendar, models.DO_NOTHING, primary_key=True)
    date = models.CharField(max_length=45)
    exception_type = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'calendar_dates'
        unique_together = (('service', 'date'),)


class Costs(models.Model):
    origin = models.ForeignKey(Touristattractions, models.DO_NOTHING, db_column='origin', primary_key=True, related_name="cost")
    destination = models.ForeignKey(Touristattractions, models.DO_NOTHING, db_column='destination', null=True)
    cost = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'costs'
        unique_together = (('origin', 'destination'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Forecast(models.Model):
    date = models.TextField(blank=True, null=True)
    start_time = models.TextField(blank=True, null=True)
    end_time = models.TextField(blank=True, null=True)
    temperature = models.TextField(blank=True, null=True)
    cloud_percent = models.TextField(blank=True, null=True)
    rain = models.TextField(blank=True, null=True)
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'forecast'


class Routes(models.Model):
    route_id = models.CharField(primary_key=True, max_length=45)
    route_short_name = models.CharField(max_length=45, blank=True, null=True)
    route_long_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'routes'


class StopTimes(models.Model):
    trip_id = models.CharField(primary_key=True, max_length=45)
    arrival_time = models.TimeField(blank=True, null=True)
    departure_time = models.TimeField(blank=True, null=True)
    stop = models.ForeignKey('Stops', models.DO_NOTHING, blank=True, null=True)
    stop_sequence = models.IntegerField()
    stop_headsign = models.CharField(max_length=45, blank=True, null=True)
    shape_dist_traveled = models.CharField(max_length=45, blank=True, null=True)
    service_id = models.CharField(max_length=45, blank=True, null=True)
    route_short_name = models.CharField(max_length=45, blank=True, null=True)
    predicted_arrival_times_0 = models.TimeField(blank=True, null=True)
    predicted_arrival_times_1 = models.TimeField(blank=True, null=True)
    predicted_arrival_times_2 = models.TimeField(blank=True, null=True)
    predicted_arrival_times_3 = models.TimeField(blank=True, null=True)
    predicted_arrival_times_4 = models.TimeField(blank=True, null=True)
    predicted_arrival_times_5 = models.TimeField(blank=True, null=True)
    predicted_arrival_times_6 = models.TimeField(blank=True, null=True)
    predicted_arrival_times_7 = models.TimeField(blank=True, null=True)
    predicted_arrival_times_8 = models.TimeField(blank=True, null=True)
    predicted_arrival_times_9 = models.TimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'stop_times'
        unique_together = (('trip_id', 'stop_sequence'),)


class Stops(models.Model):
    stop_lat = models.FloatField(blank=True, null=True)
    stop_lon = models.FloatField(blank=True, null=True)
    stop_id = models.CharField(primary_key=True, max_length=60)
    stop_name = models.TextField(blank=True, null=True)
    stopid_short = models.IntegerField(db_column='stopID_short', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'stops'


class Trips(models.Model):
    route = models.ForeignKey(Routes, models.DO_NOTHING, primary_key=True)
    direction_id = models.IntegerField()
    trip_headsign = models.CharField(max_length=100, blank=True, null=True)
    shape_id = models.CharField(max_length=45, blank=True, null=True)
    service = models.ForeignKey(Calendar, models.DO_NOTHING, blank=True, null=True)
    trip = models.ForeignKey(StopTimes, models.DO_NOTHING, null=True)

    class Meta:
        managed = True
        db_table = 'trips'
        unique_together = (('route', 'direction_id', 'trip'),)
