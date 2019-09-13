from django.db.models import Q
from .serializers import *
from .models import *
from datetime import datetime, timedelta, date

def get_services(day, date):
    """
    input: day as a word in lowercase, date as a string d-m-Y
    Used to find which bus services are available on the given date
    output: Quersey holding Calendar objects
    """
    date=(datetime.strptime(date,"%d-%m-%Y")).strftime('%Y%m%d')
    not_running=CalendarDates.objects.filter(date=date, exception_type=2).values('service_id')
    extra=CalendarDates.objects.filter(date=date, exception_type=1).values('service_id')
    services=Calendar.objects.filter((Q(**{day:1}, start_date__lte=date, end_date__gte=date) | Q(service_id__in=extra)) & ~Q(service_id__in=not_running))
    return services

def get_relevant_stop_times_per_routes_and_stops(stop_numbers, route_numbers, services, time, prediction_day):
    """
    Input: list of routes, list of stop numbers
    Filters trips that run for the given day, 30 mins before the time and upto
    one hour after the time given.
    Output: list of trips with srrival time, stop_sequence, short stop id and trip id
    """
    if not isinstance(stop_numbers, list):
        stop_numbers=[stop_numbers]
    if not isinstance(route_numbers, list):
        stop_numbers=[route_numbers]
    #get time 30 minutes before hand to allow for prediction model difference
    start_time=(datetime.strptime(time,"%H:%M")).strftime('%H:%M')
    end_time=(datetime.strptime(time,"%H:%M")+timedelta(minutes=45)).strftime('%H:%M')
    variable_column = 'predicted_arrival_times_'+str(prediction_day)
    filter_gt = variable_column + '__' + 'gte'
    filter_lt = variable_column + '__' + 'lte'
    stop_times=StopTimes.objects.filter(service_id__in=services, **{ filter_gt: start_time }, **{ filter_lt: end_time }, stop__stopid_short__in=stop_numbers, route_short_name__in=route_numbers).order_by(variable_column)
    return stop_times

def get_station_number( name, dest_lat, dest_lon, route):
    """
    Input: Station name and coordinates and a route that serves it.
    Used to match a station name with it's dublinBus stopID
    Output: Short stop id
    """
    num_of_stations_with_name=Stops.objects.filter(stop_name=name).count()
    if num_of_stations_with_name!=1:
        #Finds stations within 500m of the coordinates and returns 1
        for station in Stops.objects.raw('SELECT s.stop_id, s.stopID_short,'\
        +' ( 6371 * acos( cos( radians(%(dest_lat)s) ) * cos( radians( stop_lat ) ) *'\
        + ' cos( radians( stop_lon ) - radians(%(dest_lon)s) ) + sin( radians(%(dest_lat)s) )'\
        +' * sin( radians( stop_lat ) ) ) ) AS distance FROM website.stops as s,'\
        +' website.stop_times as st where st.stop_id=s.stop_id and '\
        +'st.route_short_name=%(route)s HAVING distance < '\
        +'%(default_radius)s ORDER BY distance LIMIT 0 , 1;',{'dest_lat':str(dest_lat), 'dest_lon':str(dest_lon), 'default_radius':str(5), 'route':str(route)}):
            return station.stopid_short
    else:
        return Stops.objects.get(stop_name=name).stopid_short

def walking_time(distance, speed=4):
    """
    Input: distance from stop, speed is by default 4km/hr
    Output: time(in seconds) needed to walk to the bus stops
    """
    return round((float(distance)/float(speed))*3600)

def get_stations_nearby(dest_lat, dest_lon, num_stations=8, radius=5):
    """
    Input: Centre point coordinates. number of stations the user wants to find. Radius is default set to 5km.
    Output: Dictionary with the list of long stop_ids, short stop_ids and dictionaries with long stop id as key
    and short_id, distance in m from centre point, and walking time as values. Results
    are ordered by stations nearest to the start destination.
    """
    default_radius=1 #km
    station_list=[]
    #for results that are not null, the more stations we check the better
    #trade off-response time
    while default_radius<radius and len(station_list)<num_stations:
        station_list=Stops.objects.raw('SELECT distinct(stop_id), stopID_short,'\
        +' ( 6371 * acos( cos( radians(%(dest_lat)s) ) * cos( radians( stop_lat ) ) *'\
        + ' cos( radians( stop_lon ) - radians(%(dest_lon)s) ) + sin( radians(%(dest_lat)s) )'\
        +' * sin( radians( stop_lat ) ) ) ) AS distance FROM website.stops HAVING distance < '\
        +'%(default_radius)s ORDER BY distance limit 30;',{'dest_lat':str(dest_lat), 'dest_lon':str(dest_lon), 'default_radius':str(default_radius)})
        default_radius+=.5
    if (len(list(station_list))==0):
        return None

    station_dict={'list_stop_long':[], 'list_stop_short':[]}
    for station in station_list:
        if station.stopid_short!=None:
            station_dict['list_stop_long']+=station.stop_id,
            station_dict['list_stop_short']+=station.stopid_short,
            station_dict[station.stop_id]={'short': station.stopid_short, 'distance':round(station.distance*1000), 'walking_time':walking_time(station.distance)}
    return station_dict
