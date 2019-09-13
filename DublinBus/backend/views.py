"""
Create views here
Don't need to worry about rendering
Mostly just create the logic for the machine learning
"""

from django.shortcuts import HttpResponse
from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
import json
import requests
import os
from rest_framework import generics
from datetime import datetime, timedelta, date
from ast import literal_eval
import pickle
from sklearn.linear_model import LinearRegression
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import redis
from itertools import permutations
from .queries import *
from django.db.models import Q, F
from sklearn.preprocessing import MinMaxScaler
import polyline as pl
load_dotenv(find_dotenv(), override=True)


dirname = os.path.dirname(__file__)

from .serializers import *
from .models import *
#from .permissions import ApiPermissions

class SearchByStop(views.APIView):
    """
    Search by stop feature
    """

    def get(self, request):
        """
        Input: HTTP request
        Output: Machine learning output as json
        Note: Main logic implemented here using the methods below
        """

        stop_number = self.request.GET.get("stopnumber")
        time = self.get_time()
        day_info = self.get_day_and_date()
        routes = self.get_routes(str(stop_number))
        services=get_services(day_info['day_long'], day_info['date'])
        trips=get_relevant_stop_times_per_routes_and_stops(stop_number, routes, services, time, day_info['prediction_digit'])
        stop_coords = self.get_stop_coords(stop_number)
        results = self.format_results(trips, stop_coords, day_info['prediction_digit'])
        return Response(results)

    def get_stop_coords(self, stop_number):
        """
        Input: stop number as string
        Output: stop coordinates as dictionary
        """
        query_result = Stops.objects.filter(stopid_short=stop_number)[0]
        coords = {
            "lat": query_result.stop_lat,
            "lng": query_result.stop_lon
        }
        return coords

    def format_results(self, results, stop_coords, prediction_digit):
        """
        Input: results as json
        Output: formatted results as json
        """
        #results+={'stop': machine_learning_inputs['stop_number'], 'route': route, 'arrival_time': arrival_time.strftime("%H:%M"), 'stop':machine_learning_inputs['trips'][route][num].stop, 'trip_id':machine_learning_inputs['trips'][route][num].trip_id},
        formatted_results = [{"directions": [], "map": {"markers": [], "polyline": []}}]
        for i in range(0, len(results)):
            formatted_results[0]["directions"] += [
                {
                    "instruction": results[i].route_short_name,
                    "time": getattr(results[i], "predicted_arrival_times_"+str(prediction_digit))
                }
            ]
        formatted_results[0]["map"]["markers"] += [stop_coords]
        return formatted_results

    def get_time(self):
        """
        input: None
        output: either time specified in url or time now as string
        """
        now = datetime.now().strftime("%H:%M")
        if self.request.GET.get("time", now) == "null":
            return now
        return self.request.GET.get("time", now)

    def get_day_and_date(self):
        """
        input: None
        output: return day and date in dict in different formats.
        'date' returns date in format d-m-Y. 'month' returns month as a value(1-12)
        'day_long' returns day as a word in lowercase. 'day' is a number between (0-6)
        with 0 being Monday
        """
        date = datetime.today().strftime('%d-%m-%Y')
        if self.request.GET.get("date") == "null" or self.request.GET.get("date") is None:
            prediction_digit=0
            day = datetime.strptime(date, '%d-%m-%Y').weekday()
            month=int(datetime.strptime(date, '%d-%m-%Y').strftime('%m'))
            day_long=datetime.strptime(date, '%d-%m-%Y').strftime('%A').lower()
            return {"date": date, "day": day, 'month': month, 'day_long':day_long, 'prediction_digit':prediction_digit}

        date = self.request.GET.get("date", None)
        roundedA = datetime.strptime(date, '%d-%m-%Y').replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        roundedB = datetime.today().replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        prediction_digit = (roundedA - roundedB).days
        day = datetime.strptime(date, '%d-%m-%Y').weekday()
        day_long=datetime.strptime(date, '%d-%m-%Y').strftime('%A').lower()
        month=int(datetime.strptime(date, '%d-%m-%Y').strftime('%m'))
        return {"date": date, "day": day, 'month': month, 'day_long':day_long, 'prediction_digit':prediction_digit}

    def get_routes(self, stop_number):
        """
        Input: Http request, bus_stop_info
        Ouput: route(s) as list
        """
        if self.request.GET.get("route") != "null" and self.request.GET.get("route") is not None:
            routes = [self.request.GET.get("route")]
        else:
            filename = os.path.join(dirname, "stop_with_routes.json")
            with open(filename) as json_file:
                busStopInfo = json.load(json_file)
                routes = busStopInfo[stop_number]
        return routes

    def format_trips_into_dict_with_routes_as_key(self, trips):
        """
        Input: Trips Objects in a queryset
        Use to seperate trips into routes to create dataframes for our ML
        Output: Dictionary with route as key and trip objects as a list.
        """
        info={}
        for trip in trips:
            route_short=trip.route_short_name
            if route_short not in info:
                info[route_short]=[trip]
            else:
                info[route_short]+=trip,
        return info

    def sort_results(self, results):
        """
        Input: Machine learning results as json
        Output: Machine learning results sorted by departure time as json
        """
        results_sorted = sorted(results, key=lambda k: k["arrival_time"])
        return results_sorted


class SearchByDestination(SearchByStop):
    """
    Search by destination feature
    Inherits from search by stop
    First tries to find a direct route between the beginning and end stations
    If no direct journeys ar available, it looks for a direct crossover.
    Finally calls API for multi-leg journeys
    """

    def get(self, request):

        time = self.get_time()
        day_info = self.get_day_and_date()
        start_coords = {"lat": float(self.get_coords("startLat")),
                        "lon": float(self.get_coords("startLon"))}
        end_coords = {"lat": float(self.get_coords("destinationLat")),
                        "lon": float(self.get_coords("destinationLon"))}
        start_stations=get_stations_nearby(start_coords["lat"],
                                                start_coords["lon"])
        end_stations=get_stations_nearby(end_coords["lat"],
                                              end_coords["lon"])

        services=get_services(day_info['day_long'], day_info['date'])
        start_routes=self.get_routes_for_list_of_stops(start_stations['list_stop_short'])
        end_routes=self.get_routes_for_list_of_stops(end_stations['list_stop_short'])

        dir_route = self.find_direct_routes(start_stations,end_stations,
                                            start_routes, end_routes,
                                           services,
                                           time, day_info['prediction_digit'])
        if len(dir_route)!=0:
            dir_route=self.format_direct_route(dir_route, start_coords, end_coords, start_stations, end_stations, time)
            results=self.sort_routes(dir_route)
            results=self.get_polyline_coords(results)
            results = self.format_response(results)
            return Response(results)

        crossovers=self.bus_crossover(start_stations, start_routes, end_stations, end_routes, services, time, day_info['prediction_digit'])
        if len(crossovers)!=0:
            crossovers=self.format_bus_crossover(crossovers, start_coords, end_coords, start_stations, end_stations, time)
            results=self.sort_routes(crossovers)
            results=self.get_polyline_coords(results)
            results = self.format_response(results)
            return Response(results)
        routes = self.get_route(time, day_info['date'], start_coords, end_coords)
        full_journeys = self.get_full_journeys(routes, time, services, day_info['prediction_digit'], day_info['date'])
        results=self.sort_routes(full_journeys)
        results = self.format_response(results)
        return Response(results)

    def get_coords(self, point):
        """
        Input: http request
        Output: coords as dict
        """
        coords = self.request.GET.get(point)
        return coords

    def get_route(self, time, date, start_coords, end_coords, mode='transit'):

        """
        Input: origin coords as string, destination coords as string
        Output: route as json
        """
        date=datetime.strptime(date,'%d-%m-%Y')
        time=datetime.strptime(time, '%H:%M').time()
        time=int(datetime.combine(date, time).timestamp())
        key = os.getenv("GOOGLE")
        call = "https://maps.googleapis.com/maps/api/directions/json?origin="\
        +str(start_coords['lat'])+','+str(start_coords['lon'])+"&destination="+str(end_coords['lat'])+','+str(end_coords['lon'])+"&key="\
        + key + "&mode=transit&transit_mode=bus&alternatives=true&region=ie&departure_time="+str(time)

        response = requests.get(call)
        if response.status_code == 200:
            route = json.loads(response.text)
            if route['status']=='ZERO_RESULTS':
                route=[]
        elif response.status_code == 400:
            route = "not found"
        return route

    def get_full_journeys(self, route, time, services, prediction_day, date):
        """
        Input: route as json
        Ouput: route segments as json
        """

        all_routes=[]
        for r in range(0, len(route["routes"])):
            valid_flag=True
            steps = route["routes"][r]["legs"][0]["steps"]
            segments = {'duration':None, 'journey':[]}
            start_time=time
            for i in range(0, len(steps)):
                if valid_flag==False:
                    break
                step=steps[i]
                if step["travel_mode"] == "WALKING":
                    step['arrival_time']=(datetime.strptime(start_time,"%H:%M")+timedelta(seconds=int(step["duration"]["value"]))).strftime('%H:%M')
                    segments['journey']+={
                    "duration_sec": step["duration"]["value"],
                    "instruction": step["html_instructions"],
                    "start_lat": step["start_location"]["lat"],
                    "start_lon": step["start_location"]["lng"],
                    "end_lat": step["end_location"]["lat"],
                    "end_lon": step["end_location"]["lng"],
                    "distance": step['distance']['value'],
                    "travel_mode": "WALKING",
                    "start_time": start_time,
                    "end_time": step['arrival_time'],
                    "markers" : [step["start_location"]["lat"], step["start_location"]["lng"], step["end_location"]["lat"], step["end_location"]["lng"]],
                                    },
                    if i !=len(steps)-1:
                        start_time=step['arrival_time']

                elif step["travel_mode"] == "TRANSIT" and (step["transit_details"]["line"]['agencies'][0]['name']=='Dublin Bus' or step["transit_details"]["line"]['agencies'][0]['name']=='Go-Ahead'):
                    step_route=step["transit_details"]["line"]["short_name"].lower()
                    dep_stop=get_station_number(step["transit_details"]["departure_stop"]["name"], step["start_location"]["lat"], step["start_location"]["lng"], step_route)
                    arrival_stop=get_station_number(step["transit_details"]["arrival_stop"]["name"], step["end_location"]["lat"], step["end_location"]["lng"], step_route)
                    if step['transit_details']['line']['agencies'][0]['name']=='Dublin Bus':
                        variable_column = 'predicted_arrival_times_'+str(prediction_day)
                        filter_gt = variable_column + '__' + 'gte'
                        stop_times=StopTimes.objects.filter(service_id__in=services, stop__stopid_short=dep_stop, route_short_name=step_route)
                        stop_times1=StopTimes.objects.filter(service_id__in=services, stop__stopid_short=arrival_stop, route_short_name=step_route)
                        stop_times=stop_times.filter(trip_id__in=stop_times1).values('trip_id')

                        trip=StopTimes.objects.filter(trip_id__in=stop_times, **{ filter_gt: start_time }, stop__stopid_short=dep_stop).order_by(variable_column)
                        if trip.count()==0:
                            valid_flag=False
                            break
                        for i in range(0, len(trip)):
                            step["departure_time"]=getattr(trip[i], "predicted_arrival_times_"+str(prediction_day)).strftime('%H:%M')
                            arrival_stop_time=StopTimes.objects.get(trip_id=trip[i].trip_id, stop__stopid_short=arrival_stop)
                            step['arrival_time']=getattr(arrival_stop_time, "predicted_arrival_times_"+str(prediction_day)).strftime('%H:%M')
                            step['duration']['value']=duration=round((datetime.strptime(step['arrival_time'],"%H:%M")-datetime.strptime(step['departure_time'],"%H:%M")).total_seconds())
                            if step['duration']['value']>0:
                                break
                        if step['duration']['value']<0:
                            valid_flag=False
                            break
                        segments['journey']+={
                        "instruction": step["html_instructions"],
                        "start_lat": step["start_location"]["lat"],
                        "start_lon": step["start_location"]["lng"],
                        "end_lat": step["end_location"]["lat"],
                        "end_lon": step["end_location"]["lng"],
                        "travel_mode": "TRANSIT",
                        "route": step["transit_details"]["line"]["short_name"],
                        "arrival_stop": arrival_stop,
                        "departure_stop": dep_stop,
                        "markers" :[step["start_location"]["lat"], step["start_location"]["lng"], step["end_location"]["lat"], step["end_location"]["lng"]],
                        "duration_sec": step['duration']['value'],
                        "polyline":self.decode_polyline(step["polyline"]["points"]),
                        "end_time": step['arrival_time'],
                        "start_time": step["departure_time"]
                                },
                        if i !=len(steps)-1:
                            start_time=step['arrival_time']
                    elif step['transit_details']['line']['agencies'][0]['name']=='Go-Ahead':
                        GA_route=self.get_route(start_time, date, {"lat": step["start_location"]["lat"],
                        "lon": step["start_location"]["lng"],}, {"lat": step["end_location"]["lat"],
                        "lon": step["end_location"]["lng"]}, mode='transit')
                        GA_route=GA_route["routes"][0]["legs"][0]["steps"]
                        for GA in GA_route:
                            if GA['travel_mode']=='TRANSIT':
                                step=GA
                        step["departure_time"]=datetime.strptime(step['transit_details']["departure_time"]['text'],'%I:%M%p').strftime('%H:%M')
                        step['arrival_time']=datetime.strptime(step['transit_details']["arrival_time"]['text'],'%I:%M%p').strftime('%H:%M')
                        step["html_instructions"]="Go-Ahead Route: " +step["html_instructions"]+" (Arrival time estimate from Google)"

                        segments['journey']+={
                        "instruction": step["html_instructions"],
                        "start_lat": step["start_location"]["lat"],
                        "start_lon": step["start_location"]["lng"],
                        "end_lat": step["end_location"]["lat"],
                        "end_lon": step["end_location"]["lng"],
                        "travel_mode": "TRANSIT",
                        "route": step["transit_details"]["line"]["short_name"],
                        "arrival_stop": arrival_stop,
                        "departure_stop": dep_stop,
                        "markers" :[step["start_location"]["lat"], step["start_location"]["lng"], step["end_location"]["lat"], step["end_location"]["lng"]],
                        "duration_sec": step['duration']['value'],
                        "polyline":self.decode_polyline(step["polyline"]["points"]),
                        "end_time": step['arrival_time'],
                        "start_time": step["departure_time"]
                                },
                        if i !=len(steps)-1:
                            start_time=step['arrival_time']
                else:
                    valid_flag=False
                    break
            if valid_flag:
                segments['duration']=str((datetime.strptime(step['arrival_time'],"%H:%M")-datetime.strptime(time,"%H:%M")).total_seconds())
                all_routes+=segments,

        return all_routes

    def sort_routes(self, results):
        """
        Input: Routes results as json
        Output: Routes results sorted into a dictionary where route is key, then stops and times as values
        """
        for journey in range(0, len(results)):
            results[journey]['duration']=float(results[journey]['duration'])
        return sorted(results, key=lambda k: k["duration"])


    def make_walking_segment(self, start_lat, start_lon, end_lat, end_lon, end_name, walking_time, walking_distance, start_time=None):
        """
        input: Strings(starting coordinates, end coordinates, walking_time of segment, starting time of segments)
        output: walking segment as json
        """
        return {
            "duration_sec": walking_time,
            "instruction": "Walk to "+end_name,
            "start_lat": start_lat,
            "start_lon": start_lon,
            "end_lat": end_lat,
            "end_lon": end_lon,
            "distance": walking_distance,
            "travel_mode": "WALKING",
            "start_time": start_time,
            "end_time": (datetime.strptime(start_time,"%H:%M")+timedelta(seconds=walking_time)).strftime('%H:%M'),
            "markers" : [start_lat, start_lon, end_lat, end_lon]

        }

    def make_transit_segment(self, start_time, end_time, start_lat, start_lon, end_lat, end_lon, end_name, route, start_stop, end_stop, trip_headsign, start_seq, end_seq, trip_id):
        """
        input: Strings(starting coordinates, end coordinates, destination name, route number, starting stop, end stop, trip_headsign)
        output: transit segment as json
        """
        return {
                "instruction": "Bus towards "+end_name,
                "trip_headsign": trip_headsign,
                "start_time": start_time.strftime('%H:%M'),
                "end_time":end_time.strftime('%H:%M'),
                "start_lat": start_lat,
                "start_lon": start_lon,
                "end_lat": end_lat,
                "end_lon": end_lon ,
                "travel_mode": "TRANSIT",
                "route": route ,
                "arrival_stop": end_stop,
                "departure_stop": start_stop,
                "markers" : [start_lat, start_lon, end_lat, end_lon],
                "start_seq":start_seq,
                "end_seq":end_seq,
                "trip_id": trip_id,
                "duration_sec": (datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)).total_seconds()

        }

    def format_direct_route(self, trips, start_coord, end_coord, start_stations, end_stations, time):
        """
        input: trips is a querset holding stoptime objects. Start and end coordinates. Start and end stations. The time as a string.
        output: results in a list
        """
        results=[]
        for trip in trips:
            route=[]
            end_name='destination'
            route+=self.make_walking_segment(start_coord['lat'], start_coord['lon'], trip.start_lat, trip.start_lon, trip.start_stop_name, start_stations[trip.start_stop_id_long]['walking_time'], start_stations[trip.start_stop_id_long]['distance'], time),
            route+=self.make_transit_segment(trip.departure_time, trip.arrival_time, trip.start_lat, trip.start_lon, trip.end_lat, trip.end_lon, trip.end_stop_name, trip.route_short_name, trip.start_stop_id, trip.end_stop_id, trip.trip_headsign, trip.start_num, trip.end_num, trip.trip_id),
            route+=self.make_walking_segment(trip.end_lat, trip.end_lon, end_coord["lat"], end_coord['lon'], end_name, end_stations[trip.end_stop_id_long]['walking_time'], end_stations[trip.end_stop_id_long]['distance'], trip.arrival_time.strftime('%H:%M')),
            duration=str((datetime.strptime(route[2]['end_time'],"%H:%M")-datetime.strptime(route[0]['start_time'],"%H:%M")).total_seconds())
            if float(duration)<0:
                duration=float(duration)+86400
                duration=str(round(duration))
            results+={'duration':duration, 'journey':route},
        return results

    def format_bus_crossover(self, trips, start_coord, end_coord, start_stations, end_stations, time):
        """
        input: trips is a querset holding stoptime objects. Start and end coordinates. Start and end stations. The time as a string.
        output: results in a list
        """
        results=[]
        for trip in trips:
            route=[]
            leg1=trip[0]
            leg2=trip[1]
            end_name='destination'
            route+=self.make_walking_segment(start_coord['lat'], start_coord['lon'], leg1.start_lat, leg1.start_lon, leg1.start_stop_name, start_stations[leg1.start_stop_id_long]['walking_time'], start_stations[leg1.start_stop_id_long]['distance'], time),
            route+=self.make_transit_segment(leg1.departure_time, leg1.arrival_time, leg1.start_lat, leg1.start_lon, leg1.end_lat, leg1.end_lon, leg1.end_stop_name, leg1.route_short_name, leg1.start_stop_id, leg1.end_stop_id, leg1.trip_headsign, leg1.start_num, leg1.end_num, leg1.trip_id),
            route+=self.make_transit_segment(leg2.departure_time, leg2.arrival_time, leg2.start_lat, leg2.start_lon, leg2.end_lat, leg2.end_lon, leg2.end_stop_name, leg2.route_short_name, leg2.start_stop_id, leg2.end_stop_id, leg2.trip_headsign, leg2.start_num, leg2.end_num, leg2.trip_id),
            route+=self.make_walking_segment(leg2.end_lat, leg2.end_lon, end_coord["lat"], end_coord['lon'], end_name, end_stations[leg2.end_stop_id_long]['walking_time'], end_stations[leg2.end_stop_id_long]['distance'], (datetime.combine(date.today(), leg2.arrival_time)).strftime('%H:%S')),
            duration=str((datetime.strptime(route[3]['end_time'],"%H:%M")-datetime.strptime(route[0]['start_time'],"%H:%M")).total_seconds())
            if float(duration)<0:
                duration=float(duration)+86400
                duration=str(round(duration))
            results+={'duration':duration, 'journey':route},
        return results

    def decode_polyline(self, encoded):
        decoded=pl.decode(encoded)
        polyline=[]
        for tup in decoded:
            polyline+={'lat':tup[0], 'lng':tup[1]},
        return polyline


    def get_polyline_coords(self, results):
        for full_journey in results:
            for leg in full_journey['journey']:
                if leg['travel_mode']=='TRANSIT':
                    leg['polyline']=[]
                    #try with  markers
                    for stop in StopTimes.objects.filter(trip_id=leg['trip_id'], stop_sequence__gte=leg['start_seq'], stop_sequence__lte=leg['end_seq']).select_related('stop'):
                        leg['polyline']+={'lat':stop.stop.stop_lat, 'lng':stop.stop.stop_lon},
        return results

    def get_routes_for_list_of_stops(self, list_stop_short):
        """
        input: a list of short stop_ids
        output: results as a dictionary with all stop_ids as keys with routes
        as values, and all as key and all routes as values
        """
        results={'all':[]}
        for stop in list_stop_short:
            #get all routes that serve a stop
            if stop!=None:
                results['all']+= self.get_routes(str(stop))
                results[stop]=self.get_routes(str(stop))
        results['all'] = sorted(list(dict.fromkeys(results['all'])))
        return results

    def find_direct_routes(self, start_stations, end_stations, start_routes, end_routes, services, time, prediction_digit):
        """
        Input: start poition as dictionary with lat long as keys, end position as dictionary with lat long
               as keys.
        Our own routing which finds a direct route from one station to another.
        Output: All valid trips for each route in the nearest start station to the user with valid trips.
        """
        #holds information 'start_stations', 'end_stations, 'date', 'start_time', 'end_time' for query
        inputs={}
        inputs['prediction_time']=prediction_digit
        inputs['start_time']=datetime.strptime(time,"%H:%M").strftime('%H:%M')

        common_routes=[]
        index=0
        for start_route in start_routes['all']:
            for end_route_index in range(index, len(end_routes['all'])):
                if start_route==end_routes['all'][end_route_index]:
                    common_routes+=start_route,
                    index=end_route_index
                    break
                if start_route<end_routes['all'][end_route_index]:
                    index=end_route_index
                    break
        if len(common_routes)==0:
            return[]
        inputs['start_stations']=tuple(start_stations['list_stop_long'])
        inputs['end_stations']=tuple(end_stations['list_stop_long'])

        inputs['services']=[]
        for service in services:
            inputs['services']+=service.service_id,
        #Finds all trip info for direct routes from one of the given start stations and stop stations
        #within a given time on a specific day.
        results=[]
        for start_station in start_stations['list_stop_long']:

            walking_time=int(start_stations[start_station]['walking_time'])
            inputs['start_time']=(datetime.strptime(inputs['start_time'],"%H:%M")+timedelta(seconds=walking_time)).strftime('%H:%M')
            inputs['end_time']=(datetime.strptime(inputs['start_time'],"%H:%M")+timedelta(minutes=30)).strftime('%H:%M')
            inputs['common_routes']=[]
            inputs['start_stations']=start_station
            for route in start_routes[start_stations[start_station]['short']]:
                if route in common_routes:
                    inputs['common_routes']=route,

                    trips=StopTimes.objects.raw("SELECT distinct t.trip_headsign, r.route_short_name, st1.trip_id,"\
                    +" st1.predicted_arrival_times_%(prediction_time)s as departure_time, s1.stop_id as start_stop_id_long, s1.stopID_short as start_stop_id, s1.stop_name as start_stop_name,"\
                    +"s1.stop_lat as start_lat, s1.stop_lon as start_lon, st1.stop_sequence as start_num, "\
                    +"st2.predicted_arrival_times_%(prediction_time)s as arrival_time, s2.stopID_short as end_stop_id, s2.stop_id as end_stop_id_long, "\
                    +"s2.stop_name as end_stop_name, s2.stop_lat as end_lat, s2.stop_lon as end_lon, "\
                    +"st2.stop_sequence as end_num FROM website.stop_times as st1, website.stop_times as st2,"\
                    +" website.trips as t, website.routes as r, website.stops as s1, "\
                    + "website.stops as s2  where st1.route_short_name in %(common_routes)s and st2.route_short_name in %(common_routes)s and st1.stop_id =  %(start_stations)s"\
                    +" and st2.stop_id in  %(end_stations)s and st1.stop_sequence<st2.stop_sequence and st1.predicted_arrival_times_%(prediction_time)s>=%(start_time)s and "\
                    +"st1.predicted_arrival_times_%(prediction_time)s<=%(end_time)s and st2.predicted_arrival_times_%(prediction_time)s>%(start_time)s"\
                    +" and st1.trip_id=t.trip_id and t.service_id in %(services)s and st1.trip_id=st2.trip_id"\
                    +"  and r.route_id=t.route_id and s1.stop_id=st1.stop_id "\
                    +" and s2.stop_id=st2.stop_id order by st1.predicted_arrival_times_%(prediction_time)s limit 1;",inputs)
                    if len(trips)>0:
                        results+=trips
            if len(results)!=0:
                return results
        return results

    def bus_crossover(self, start_stations, start_routes, end_stations, end_routes, services, time, prediction_day):
        """
        Input: start poition as dictionary with lat long as keys, end position as dictionary with lat long
               as keys.
        When no direct route is possible, our app looks for a route with a stop_id as a direct crossover
        Output: All valid trips for each route with each leg in a list in the nearest start station to the user with valid trips.
        """
        stoptimes_all_start_stops=get_relevant_stop_times_per_routes_and_stops(start_stations['list_stop_short'], start_routes['all'], services, time, prediction_day)
        possible_crossovers_stops_leg1=StopTimes.objects.filter(trip_id__in=stoptimes_all_start_stops).values('stop__stopid_short')
        stoptimes_all_end_stops=get_relevant_stop_times_per_routes_and_stops(end_stations['list_stop_short'], end_routes['all'], services, time, prediction_day)
        possible_crossovers_stops_leg2=StopTimes.objects.filter(trip_id__in=stoptimes_all_end_stops).values('stop__stopid_short')
        crossovers=Stops.objects.filter(Q(stopid_short__in=possible_crossovers_stops_leg1)&Q(stopid_short__in=possible_crossovers_stops_leg2)).values('stop_id', 'stopid_short')
        if not crossovers.exists():
            return []
        results=[]
        crossover_stations={'list_stop_long':[], 'list_stop_short':[]}
        for crossover in crossovers:
            crossover_stations['list_stop_long']+=crossover['stop_id'],
            crossover_stations['list_stop_short']+=crossover['stopid_short'],
            crossover_stations[crossover['stop_id']]={'short': crossover['stopid_short']}
        crossover_routes=self.get_routes_for_list_of_stops(crossover_stations['list_stop_short'])
        all_leg1s=self.find_direct_routes(start_stations, crossover_stations, start_routes, crossover_routes, services, time, prediction_day)
        for leg1 in all_leg1s:
            leg2=self.find_direct_routes({'list_stop_long':[leg1.end_stop_id_long], 'list_stop_short':[leg1.end_stop_id], leg1.end_stop_id_long:{'short':leg1.end_stop_id, 'walking_time':0}}, end_stations, {'all':sorted(list(dict.fromkeys(crossover_routes[leg1.end_stop_id]))), leg1.end_stop_id:crossover_routes[leg1.end_stop_id]}, end_routes, services, leg1.arrival_time.strftime("%H:%M"), prediction_day)
            if len(leg2)!=0:
                results+=[leg1, leg2[0]],
        return results


    def format_response(self, results):
        """
        """
        response = []
        count = 0
        #results = results[:3]
        for result in results:
            result_flag=True
            route_breakdown = {}
            route_breakdown["directions"] = []
            route_breakdown["map"] = {"markers": [], "polyline": []}

            for i in range(0, len(result['journey'])):
                leg=result["journey"][i]
                if int(leg["duration_sec"]) == 0:
                    time = 0
                elif int(leg["duration_sec"]) < 60:
                    time = 1
                else:
                    time = leg["duration_sec"] // 60

                route_dict = {
                    "instruction": leg["instruction"],
                    "time": time,
                    "start_time": leg["start_time"],
                    "end_time": leg["end_time"],
                    "travel_mode": "",
                    }

                marker = {
                    "lat": leg["markers"][0],
                    "lng": leg["markers"][1],
                    "route": "",
                    "stop": ""
                }

                if i == 0:
                    route_breakdown["map"]["polyline"] += [{
                        "lat": marker["lat"],
                        "lng": marker["lng"]
                    }]

                if leg["travel_mode"] == "TRANSIT":
                    route_dict["travel_mode"] = leg["route"]
                    marker["route"] = leg["route"]
                    marker["stop"] = leg["arrival_stop"]
                    route_breakdown["map"]["polyline"] += leg['polyline']
                    route_dict["instruction"] = route_dict["instruction"].replace("Bus", route_dict["travel_mode"])
                else:
                    route_dict["travel_mode"] = "WALKING"


                route_breakdown["directions"] += [route_dict]
                route_breakdown["map"]["markers"] += [marker]

                if route_dict["travel_mode"] == "WALKING" and i != len(result["journey"])-1:
                    arrive_time = datetime.strptime(leg["end_time"], "%H:%M")
                    depart_time = datetime.strptime(result["journey"][i+1]["start_time"], "%H:%M")
                    wait_time = depart_time - arrive_time
                    wait_time = wait_time.total_seconds() // 60
                    if wait_time<0:
                        result_flag=False
                    waiting = {
                        "instruction": "Wait for bus",
                        "time": wait_time,
                        "travel_mode": "WALKING"
                    }
                    if wait_time>0:
                        route_breakdown["directions"] += [waiting]
                elif i != len(result["journey"])-1 and result["journey"][i+1]["travel_mode"] == "TRANSIT":
                    arrive_time = datetime.strptime(leg["end_time"], "%H:%M")
                    depart_time = datetime.strptime(result["journey"][i+1]["start_time"], "%H:%M")
                    wait_time = depart_time - arrive_time
                    wait_time = wait_time.total_seconds() // 60
                    if wait_time<0:
                        result_flag=False
                    waiting = {
                        "instruction": "Wait for bus",
                        "time": wait_time,
                        "travel_mode": "WALKING"
                    }
                    if wait_time>0:
                        route_breakdown["directions"] += [waiting]


                if i == len(result):
                    route_breakdown["map"]["markers"] += [{
                        "lat": leg["markers"][2],
                        "lng": leg["markers"][3],
                    }]
                    route_breakdown["map"]["polyline"] += [{
                        "lat": leg["markers"][2],
                        "lng": leg["markers"][3],
                    }]

            route_breakdown["duration"] = 0
            for duration in route_breakdown["directions"]:
                route_breakdown["duration"] += duration["time"]
            if result_flag:
                response += [route_breakdown]

        return response


class TouristPlanner(SearchByStop):
    """
    Returns best route through series of tourist destinations
    """

    def get(self, request):
        """
        Input: user http request
        Output: array of lowest cost route
        """
        attractions = self.get_attractions()
        home = self.get_home()
        home_coords = self.get_home_coords()
        time = self.get_time()
        day_info = self.get_day_and_date()
        attractions = self.remove_home_from_attractions(attractions, home)
        attractions = list(permutations(attractions))
        attractions = self.convert_tuples_to_list(attractions)
        attractions = self.add_home(attractions, home)
        best_route = self.get_best_route(attractions)
        best_route_formatted = self.format_route(best_route, home, home_coords, time, day_info["date"])
        best_route_formatted = self.remove_null(best_route_formatted, home)
        return Response(best_route_formatted)

    def format_route(self, best_route, home, home_coords, time, date):
        """
        Input: best route as an array
        Output:best route formatted as json
        """
        results = []
        for i in range(len(best_route[0])-1):
            if best_route[0][i] != home and best_route[0][i+1] != home:
                start_lat = Touristattractions.objects.filter(name=best_route[0][i])[0].lat
                start_lon = Touristattractions.objects.filter(name=best_route[0][i])[0].lon
                end_lat = Touristattractions.objects.filter(name=best_route[0][i+1])[0].lat
                end_lon = Touristattractions.objects.filter(name=best_route[0][i+1])[0].lon
                time = time
            elif best_route[0][i] == home:
                start_lat = home_coords["lat"]
                start_lon = home_coords["lon"]
                end_lat = Touristattractions.objects.filter(name=best_route[0][i+1])[0].lat
                end_lon = Touristattractions.objects.filter(name=best_route[0][i+1])[0].lon
                time = time
            else:
                start_lat = Touristattractions.objects.filter(name=best_route[0][i])[0].lat
                start_lon = Touristattractions.objects.filter(name=best_route[0][i])[0].lon
                end_lat = home_coords["lat"]
                end_lon = home_coords["lon"]
                time = time

            results += [{
                "number": i+1,
                "attraction": best_route[0][i] + " to " + best_route[0][i+1],
                "start_lat": start_lat,
                "start_lon": start_lon,
                "end_lat": str(end_lat),
                "end_lon": str(end_lon),
                "time": str(time),
                "date": str(date)
            }]
        return results

    def get_attractions(self):
        """
        Input: request from user
        Output: attractions as array
        """
        attractions = literal_eval(self.request.GET.get("attractions", ["this", "didn't", "work"]))
        results = []
        for attraction in attractions:
            if attraction != "":
                results += [attraction]
        return results

    def get_home(self):
        """
        Input: request from user
        Output: home as string
        """
        return self.request.GET.get("home")

    def remove_home_from_attractions(self, attractions, home):
        """
        Input: attractions as array, home as string
        Output: home removed from attractions
        """
        while home in attractions:
            attractions.remove(home)
        return attractions

    def convert_tuples_to_list(self, attractions):
        """
        Input: List of tuples
        Output: List of lists
        """
        for i in range(len(attractions)):
            attractions[i] = list(attractions[i])
        return attractions

    def add_home(self, permutations, home):
        """
        Input: permutations as array of arrays, home as string
        Output: home added to start and end of each permutation
        """
        if permutations[0][0] != home:
            for i in range(len(permutations)):
                permutations[i] = [home] + permutations[i] + [home]
        return permutations

    def remove_null(self, results, home):
        if home == "null":
            results[0]["attraction"] = results[0]["attraction"].replace("null", "Your starting point")
            results[len(results)-1]["attraction"] = results[len(results)-1]["attraction"].replace("null", "your starting point")
        return results

    def get_best_route(self, attractions):
        """
        Input: permutations as array of arrays
        Output: lowest cost permutation as array, cost of permutation
        """
        minimum = float("inf")
        lowest_cost_permutation = []
        r = redis.Redis(host="localhost", port=6379, db=0)

        for permutation in attractions:
            total_cost = 0
            i = 0
            while total_cost < minimum and i < len(permutation)-1:
                if r.exists(str(permutation[i]) + " " + str(permutation[i+1])):
                    cost = r.get(str(permutation[i]) + " " + str(permutation[i+1]))
                    total_cost += int(cost.decode())
                elif i == 0:
                    cost = self.get_cost_from_api(permutation[i], permutation[i+1])
                    r.set(str(permutation[i]) + " " + str(permutation[i+1]), cost, ex=3600)
                    total_cost += cost
                elif i == len(permutation)-2:
                    cost = self.get_cost_from_api(permutation[i], permutation[i+1])
                    r.set(str(permutation[i]) + " " + str(permutation[i+1]), cost, ex=3600)
                    total_cost += cost
                else:
                    cost = self.get_cost_from_database(permutation[i], permutation[i+1])
                    r.set(str(permutation[i]) + " " + str(permutation[i+1]), cost, ex=3600)
                    total_cost += cost
                i += 1
            if total_cost < minimum:
                lowest_cost_permutation = permutation
                minimum = total_cost

            return lowest_cost_permutation, minimum

    def get_home_coords(self):
        """
        Input: home as string
        Output: home coordinates as dicitonary
        """

        lat = self.request.GET.get("startLat")
        lon = self.request.GET.get("startLon")
        return {"lat": lat, "lon": lon}



    def get_cost_from_api(self, origin, destination):
        """
        Input: origin, destination as string
        Output: cost as int
        """
        call = "https://maps.googleapis.com/maps/api/directions/json?origin=" + origin + "&destination=" + destination + "&key=" + os.getenv("GOOGLE") + "&mode=transit&transit_mode=bus&region=IE"
        response = requests.get(call)
        response_json = json.loads(response.text)
        result = response_json["routes"][0]["legs"][0]["distance"]["value"]
        return result

    def get_cost_from_database(self, origin, destination):
        """
        Input: origin, destination as string
        Output: cost as int
        """
        return Costs.objects.filter(origin=origin, destination=destination)[0].cost

class GetTouristAttractions(generics.ListCreateAPIView):
    """
    Handles returning results from database for journey planner attraction info
    """
    queryset = Touristattractions.objects.all()
    serializer_class = TouristSerializer

"""
class RouteView(generics.ListCreateAPIView):
    #Shows routes table
    queryset = Routes.objects.all()
    serializer_class = RouteSerializer
"""
class directions(views.APIView):

    def get(self, request):
        stop_number = self.get_params("stopnumber")
        route_number = self.get_params("route")
        date = datetime.today().strftime("%d-%m-%Y")
        day = datetime.today().weekday()
        day_long = datetime.strptime(date, '%d-%m-%Y').strftime('%A').lower()
        directions = get_direction(day_long, date, route_number, stop_number)
        return Response(directions)

    def get_params(self, param):
        """
        Input: None
        Output: Route, direction, day as dict
        """
        result = self.request.GET.get(param, None)
        return result
