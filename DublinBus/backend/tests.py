"""
Tests for django backend
"""

from django.test import RequestFactory, TestCase

from .views import *
from datetime import datetime, timedelta, date
import polyline as pl
import redis

# Create your tests here.


class SearchByStopTest(TestCase):
    """
    UnitTests for SearchByStops Feature
    """

    def setUp(self):
        """
        Setup fake models for testing
        """

        Trips.objects.create(
            route = Routes.objects.create(
                route_id='7b long',
                route_short_name='7d',
            ),
            direction_id = 1,
            trip_headsign = 'towards town',
            shape_id = 'ascd',
            service = Calendar.objects.create(
                service_id = "12345",
                start_date = "20190303",
                end_date = "20190615",
                monday = "1",
                tuesday = "0",
                wednesday = "0",
                thursday = "0",
                friday = "0",
                saturday = "0",
                sunday = "0"
            ),
            trip = StopTimes.objects.create(
                    trip_id = "1.1.60-79-b12-1.346.I",
                    arrival_time = "07:30:00 ",
                    departure_time = "07:30:00",
                    stop = Stops.objects.create(
                        stop_lat = 123,
                        stop_lon = 123,
                        stop_id = 'big7556',
                        stop_name = 'testname',
                        stopid_short ='2007',
                    ),
                    stop_sequence = "1",
                    stop_headsign = "Aston Quay",
                    shape_dist_traveled = None,
                    service_id="12345",
                    route_short_name='7d',
                    predicted_arrival_times_0="07:30:00 ",
                    predicted_arrival_times_1="07:30:00 ",
                    predicted_arrival_times_2="07:30:00 ",
                    predicted_arrival_times_3="07:30:00 ",
                    predicted_arrival_times_4="07:30:00 ",
                    predicted_arrival_times_5="07:30:00 ",
                    predicted_arrival_times_6="07:30:00 ",
                    predicted_arrival_times_7="07:30:00 ",
                    predicted_arrival_times_8="07:30:00 ",
                    predicted_arrival_times_9="07:30:00 ",
            ),
        )

        self.factory = RequestFactory()
        self.request_specific = self.factory.get("/api/stop/?stopnumber=2007&route=7D&time=14:00&date=02-07-2019")
        self.request_not_specific = self.factory.get("/api/stop/?stopnumber=2007&time=null&route=null")
        self.test_view_specific = self.setup_view(SearchByStop(),
                                                  self.request_specific)
        self.test_view_not_specific = self.setup_view(SearchByStop(),
                                                  self.request_not_specific)

        def tearDown(self):
            del self.test_view

    def setup_view(self, view, request, *args, **kwargs):
        """
        Sets up view so its methods can be called and tested
        """
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

    def test_get(self):
        """
        Test response code of get function
        """
        request = self.factory.get("/api/stop/?stopnumber=2007&route=7D")
        self.assertEquals((self.test_view_not_specific.get(request).status_code), 200)


    def test_get_time_now(self):
        """
        Should return time now as a string
        """
        now = datetime.now().strftime("%H:%M")
        self.assertEqual(self.test_view_not_specific.get_time(), now)

    def test_get_time_specified(self):
        """
        Should return time specified in url as a string
        """
        self.assertEqual(self.test_view_specific.get_time(), "14:00")

    def test_get_day_today(self):
        """
        Should return today as a string
        """
        today = datetime.now().weekday()
        self.assertEqual(self.test_view_not_specific.get_day_and_date()["day"],             today)

    def test_get_day_specified(self):
        """
        Should return day specified in url as a string
        """
        self.assertEqual(self.test_view_specific.get_day_and_date()["day"], 1)

    def test_get_date_today(self):
        """
        Should return date now as a string
        """
        today = datetime.now().strftime("%d-%m-%Y")
        self.assertEqual(self.test_view_not_specific.get_day_and_date()["date"], today)

    def test_get_date_specified(self):
        """
        Should return date specified in url as a string
        """
        self.assertEqual(self.test_view_specific.get_day_and_date()["date"], "02-07-2019")

    def test_get_routes_none_specified(self):
        """
        Should return route info
        """
        self.assertEqual(self.test_view_not_specific.get_routes('2007'),
                                                    ['145', '155', '46a', '47', '84x', '116', '7b', '7d'])
    def test_get_routes(self):
        """
        Should return route info
        """
        self.assertEqual(self.test_view_specific.get_routes('2007'),
                                                    ['7D'])


    def test_sort_results(self):
        """
        Should return machine learning results sorted as json
        """
        test_input = [
            {"route": "46a", "arrival_time": 4, "travel_time": None},
            {"route": "39a", "arrival_time": 2, "travel_time": None},
            {"route": "145", "arrival_time": 1, "travel_time": None},
            {"route": "46a", "arrival_time": 8, "travel_time": None},
            {"route": "155", "arrival_time": 6, "travel_time": None}
        ]
        test_output = [
            {"route": "145", "arrival_time": 1, "travel_time": None},
            {"route": "39a", "arrival_time": 2, "travel_time": None},
            {"route": "46a", "arrival_time": 4, "travel_time": None},
            {"route": "155", "arrival_time": 6, "travel_time": None},
            {"route": "46a", "arrival_time": 8, "travel_time": None},
        ]
        self.assertEqual(self.test_view_specific.sort_results(test_input), test_output)

    def test_format_trips_into_dict_with_routes_as_key(self):
        """
        Should return trip as a dict
        """
        trip=[Trips.objects.get(route='7b long')]
        trip[0].route_short_name='7b'
        self.assertEqual(self.test_view_specific.format_trips_into_dict_with_routes_as_key(trip), {'7b': trip})

    def test_format_results(self):
        """
        Should format results to json
        """
        results=StopTimes.objects.filter(stop__stopid_short=2007)
        stop_coords={'lat': 53.3088750410389, 'lng': -6.21611120483354}
        prediction_digit=0
        time=datetime.strptime('07:30', '%H:%M').time()
        output=[    {
        "directions": [
            {
                "instruction": "7d",
                "time": time
            },],
            'map': {'markers': [{'lat': 53.3088750410389, 'lng': -6.21611120483354}],'polyline': []}}]

        self.assertEqual(self.test_view_specific.format_results(results, stop_coords, prediction_digit), output)

class SearchByDestinationTest(TestCase):
    def setUp(self):
        """
        Setup fake models for testing
        """
        Trips.objects.create(
            route = Routes.objects.create(
                route_id='7b long',
                route_short_name='7d',
            ),
            direction_id = 1,
            trip_headsign = 'towards town',
            shape_id = 'ascd',
            service = Calendar.objects.create(
                service_id = "12345",
                start_date = "20190303",
                end_date = "20190615",
                monday = "1",
                tuesday = "0",
                wednesday = "0",
                thursday = "0",
                friday = "0",
                saturday = "0",
                sunday = "0"
            ),
            trip = StopTimes.objects.create(
                    trip_id = "id",
                    arrival_time = "07:30:00 ",
                    departure_time = "07:30:00",
                    stop = Stops.objects.create(
                        stop_lat = 123,
                        stop_lon = 123,
                        stop_id = 'big7556',
                        stop_name = 'testname',
                        stopid_short ='7556',
                    ),
                    stop_sequence = "3",
                    stop_headsign = "Aston Quay",
                    shape_dist_traveled = None,
                    service_id="12345",
                    route_short_name='7d',
                    predicted_arrival_times_0="07:30:00 ",
                    predicted_arrival_times_1="07:30:00 ",
                    predicted_arrival_times_2="07:30:00 ",
                    predicted_arrival_times_3="07:30:00 ",
                    predicted_arrival_times_4="07:30:00 ",
                    predicted_arrival_times_5="07:30:00 ",
                    predicted_arrival_times_6="07:30:00 ",
                    predicted_arrival_times_7="07:30:00 ",
                    predicted_arrival_times_8="07:30:00 ",
                    predicted_arrival_times_9="07:30:00 ",
            ),
        )
        Calendar.objects.create(
            service_id = "2#1",
            start_date = "20190303",
            end_date = "20200915",
            monday = "1",
            tuesday = "1",
            wednesday = "1",
            thursday = "1",
            friday = "1",
            saturday = "1",
            sunday = "1"
        )
        StopTimes.objects.create(
                trip_id = "id1",
                arrival_time = "07:30:00 ",
                departure_time = "07:30:00",
                stop = Stops.objects.create(
                    stop_lat = 123,
                    stop_lon = 123,
                    stop_id = 'big75',
                    stop_name = 'testname',
                    stopid_short ='416',
                ),
                stop_sequence = "1",
                stop_headsign = "Aston Quay",
                shape_dist_traveled = None,
                service_id="2#1",
                route_short_name='7a',
                predicted_arrival_times_0="10:55:00 ",
                predicted_arrival_times_1="10:55:00 ",
                predicted_arrival_times_2="07:30:00 ",
                predicted_arrival_times_3="07:30:00 ",
                predicted_arrival_times_4="07:30:00 ",
                predicted_arrival_times_5="07:30:00 ",
                predicted_arrival_times_6="07:30:00 ",
                predicted_arrival_times_7="07:30:00 ",
                predicted_arrival_times_8="07:30:00 ",
                predicted_arrival_times_9="07:30:00 ",
        ),
        StopTimes.objects.create(
                trip_id = "id2",
                arrival_time = "07:30:00 ",
                departure_time = "07:30:00",
                stop = Stops.objects.create(
                    stop_lat = 123,
                    stop_lon = 123,
                    stop_id = 'big755',
                    stop_name = 'testname',
                    stopid_short ='3047',
                ),
                stop_sequence = "4",
                stop_headsign = "Aston Quay",
                shape_dist_traveled = None,
                service_id="2#1",
                route_short_name='7a',
                predicted_arrival_times_0="11:20:00 ",
                predicted_arrival_times_1="11:20:00 ",
                predicted_arrival_times_2="10:05:00 ",
                predicted_arrival_times_3="07:30:00 ",
                predicted_arrival_times_4="07:30:00 ",
                predicted_arrival_times_5="07:30:00 ",
                predicted_arrival_times_6="07:30:00 ",
                predicted_arrival_times_7="07:30:00 ",
                predicted_arrival_times_8="07:30:00 ",
                predicted_arrival_times_9="07:30:00 ",
        ),

        self.factory = RequestFactory()
        self.request_specific = self.factory.get("/api/destination/?startLat=53.3249987&startLon=-6.26499894&destinationLat=53.342608&destinationLon=-6.255987")
        self.request_specific_crossover = self.factory.get("api/destination/?startLat=53.3037056&startLon=-6.2169088&destinationLat=53.3659853&destinationLon=-6.248263199999997&date=15-08-2019&time=10:48")
        self.request_not_specific = self.factory.get("/api/stop/?stop=2007")
        self.test_view_specific = self.setup_view(SearchByDestination(),
                                                  self.request_specific)
        self.test_view_specific_crossover = self.setup_view(SearchByDestination(),
                                                  self.request_specific_crossover)

        self.test_view_not_specific = self.setup_view(SearchByDestination(),
                                                  self.request_not_specific)

        def tearDown(self):
            del self.test_view

    def setup_view(self, view, request, *args, **kwargs):
        """
        Sets up view so its methods can be called and tested
        """
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

    def test_get_coords(self):
        self.assertEqual(self.test_view_specific.get_coords("startLat"), "53.3249987")

    def test_get_direct(self):
        self.assertEqual(self.test_view_specific.get("startLat").status_code, 200)

    def test_Google_API_call(self):
        time = "20:00"
        day_info = datetime.today().strftime('%d-%m-%Y')
        self.assertEqual(self.test_view_specific.get_route(time, day_info, {'lat':53.3249987,'lon': -6.2649989}, {'lat':53.342608, 'lon':-6.255987},'transit')['status'], "OK")

    def test_sort_routes(self):
        """
        Should return machine learning results sorted as json
        """
        test_input = [
            {"duration":90},
            {"duration":92},
            {"duration":95},
            {"duration":93},
            {"duration":91}
        ]
        test_output = [
            {"duration":90},
            {"duration":91},
            {"duration":92},
            {"duration":93},
            {"duration":95}
        ]
        self.assertEqual(self.test_view_specific.sort_routes(test_input), test_output)

    def test_make_walking_segment(self):
        start_lat=123
        start_lon=123
        end_lat=321
        end_lon=321
        end_name='abd'
        walking_time=13
        walking_distance=14
        start_time="12:14"
        result={
            "duration_sec": 13,
            "instruction": "Walk to abd",
            "start_lat": 123,
            "start_lon": 123,
            "end_lat": 321,
            "end_lon": 321,
            "distance": 14,
            "travel_mode": "WALKING",
            "start_time": "12:14",
            "end_time": "12:14",
            "markers" : [123,123,321,321]
        }
        self.assertEqual(self.test_view_specific.make_walking_segment(start_lat, start_lon, end_lat, end_lon, end_name, walking_time, walking_distance, start_time), result)

    def test_make_transit_segment(self):
        start_lat=123
        start_lon=123
        end_lat=321
        end_lon=321
        end_name='end'
        route='7a'
        start_stop=44
        end_stop=78
        trip_headsign='bantry'
        start_seq=35
        end_seq=97
        trip_id='12334'
        start_time=datetime.strptime("12:14", '%H:%M').time()
        end_time=datetime.strptime("13:14", '%H:%M').time()
        result={
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
        self.assertEqual(self.test_view_specific.make_transit_segment(start_time, end_time, start_lat, start_lon, end_lat, end_lon, end_name, route, start_stop, end_stop, trip_headsign, start_seq, end_seq, trip_id), result)

    def test_format_direct(self):
            class trips_edited():
                trip_id= '3977.2.60-83-b12-1.347.I'
                arrival_time= datetime.strptime("20:48", '%H:%M').time()
                departure_time= datetime.strptime("20:36", '%H:%M').time()
                route_short_name= '83'
                trip_headsign= 'Stannaway Court - Charlestown Shopping Centre'
                start_stop_id_long= '8220DB001070'
                start_stop_id= 1070
                start_stop_name= 'Rathmines, Rathmines Town Centre'
                start_lat= 53.3249801839816
                start_lon= -6.26535598291685
                start_num= 20
                end_stop_id= 1359
                end_stop_id_long= '8220DB001359'
                end_stop_name= 'College Green'
                end_lat= 53.3443994063613
                end_lon= -6.26136859043366
                end_num= 28
            a=trips_edited()
            trips=[a]
            result=[{'duration': '1020.0', 'journey': [{'duration_sec': 21, 'instruction': 'Walk to Rathmines, Rathmines Town Centre', 'start_lat': 53.3249987, 'start_lon': -6.26499894, 'end_lat': 53.3249801839816, 'end_lon': -6.26535598291685, 'distance': 24, 'travel_mode': 'WALKING', 'start_time': '20:31', 'end_time': '20:31', 'markers': [53.3249987, -6.26499894, 53.3249801839816, -6.26535598291685]}, {'instruction': 'Bus towards College Green', 'trip_headsign': 'Stannaway Court - Charlestown Shopping Centre', 'start_time': '20:36', 'end_time': '20:48', 'start_lat': 53.3249801839816, 'start_lon': -6.26535598291685, 'end_lat': 53.3443994063613, 'end_lon': -6.26136859043366, 'travel_mode': 'TRANSIT', 'route': '83', 'arrival_stop': 1359, 'departure_stop': 1070, 'markers': [53.3249801839816, -6.26535598291685, 53.3443994063613, -6.26136859043366], 'start_seq': 20, 'end_seq': 28, 'trip_id': '3977.2.60-83-b12-1.347.I', 'duration_sec': 720.0}, {'duration_sec': 21, 'instruction': 'Walk to destination', 'start_lat': 53.3443994063613, 'start_lon': -6.26136859043366, 'end_lat': 53.342608, 'end_lon': -6.255987, 'distance': 24, 'travel_mode': 'WALKING', 'start_time': '20:48', 'end_time': '20:48', 'markers': [53.3443994063613, -6.26136859043366, 53.342608, -6.255987]}]}]
            start_stations={'list_stop_long': ['8220DB001070'], 'list_stop_short':['1070'], '8220DB001070': {'short': 1070, 'distance': 24, 'walking_time': 21}}
            end_stations={'list_stop_long': ['8220DB001359'], 'list_stop_short':['1359'], '8220DB001359': {'short': 1359, 'distance': 24, 'walking_time': 21}}
            self.assertEqual(self.test_view_specific.format_direct_route(trips, {'lat': 53.3249987, 'lon': -6.26499894}, {'lat': 53.342608, 'lon': -6.255987}, start_stations, end_stations, '20:31'), result)

    def test_format_crossover(self):
        class trips_edited():
            trip_id= '3977.2.60-83-b12-1.347.I'
            arrival_time= datetime.strptime("20:48", '%H:%M').time()
            departure_time= datetime.strptime("20:36", '%H:%M').time()
            route_short_name= '83'
            trip_headsign= 'Stannaway Court - Charlestown Shopping Centre'
            start_stop_id_long= '8220DB001070'
            start_stop_id= 1070
            start_stop_name= 'Rathmines, Rathmines Town Centre'
            start_lat= 53.3249801839816
            start_lon= -6.26535598291685
            start_num= 20
            end_stop_id= 1359
            end_stop_id_long= '8220DB001359'
            end_stop_name= 'College Green'
            end_lat= 53.3443994063613
            end_lon= -6.26136859043366
            end_num= 28
        a=trips_edited()
        b=trips_edited()
        b.departure_time=datetime.strptime("20:58", '%H:%M').time()
        b.arrival_time=datetime.strptime("21:58", '%H:%M').time()
        trips=[[a, b]]
        result=[{'duration': '1740.0', 'journey': [{'duration_sec': 21, 'instruction': 'Walk to Rathmines, Rathmines Town Centre', 'start_lat': 53.3249987, 'start_lon': -6.26499894, 'end_lat': 53.3249801839816, 'end_lon': -6.26535598291685, 'distance': 24, 'travel_mode': 'WALKING', 'start_time': '20:31', 'end_time': '20:31', 'markers': [53.3249987, -6.26499894, 53.3249801839816, -6.26535598291685]}, {'instruction': 'Bus towards College Green', 'trip_headsign': 'Stannaway Court - Charlestown Shopping Centre', 'start_time': '20:36', 'end_time': '20:48', 'start_lat': 53.3249801839816, 'start_lon': -6.26535598291685, 'end_lat': 53.3443994063613, 'end_lon': -6.26136859043366, 'travel_mode': 'TRANSIT', 'route': '83', 'arrival_stop': 1359, 'departure_stop': 1070, 'markers': [53.3249801839816, -6.26535598291685, 53.3443994063613, -6.26136859043366], 'start_seq': 20, 'end_seq': 28, 'trip_id': '3977.2.60-83-b12-1.347.I', 'duration_sec': 720.0}, {'instruction': 'Bus towards College Green', 'trip_headsign': 'Stannaway Court - Charlestown Shopping Centre', 'start_time': '20:58', 'end_time': '21:58', 'start_lat': 53.3249801839816, 'start_lon': -6.26535598291685, 'end_lat': 53.3443994063613, 'end_lon': -6.26136859043366, 'travel_mode': 'TRANSIT', 'route': '83', 'arrival_stop': 1359, 'departure_stop': 1070, 'markers': [53.3249801839816, -6.26535598291685, 53.3443994063613, -6.26136859043366], 'start_seq': 20, 'end_seq': 28, 'trip_id': '3977.2.60-83-b12-1.347.I', 'duration_sec': 3600.0}, {'duration_sec': 21, 'instruction': 'Walk to destination', 'start_lat': 53.3443994063613, 'start_lon': -6.26136859043366, 'end_lat': 53.342608, 'end_lon': -6.255987, 'distance': 24, 'travel_mode': 'WALKING', 'start_time': '21:00', 'end_time': '21:00', 'markers': [53.3443994063613, -6.26136859043366, 53.342608, -6.255987]}]}]
        start_stations={'list_stop_long': ['8220DB001070'], 'list_stop_short':['1070'], '8220DB001070': {'short': 1070, 'distance': 24, 'walking_time': 21}}
        end_stations={'list_stop_long': ['8220DB001359'], 'list_stop_short':['1359'], '8220DB001359': {'short': 1359, 'distance': 24, 'walking_time': 21}}
        self.assertEqual(self.test_view_specific.format_bus_crossover(trips, {'lat': 53.3249987, 'lon': -6.26499894}, {'lat': 53.342608, 'lon': -6.255987}, start_stations, end_stations, '20:31'), result)

    def test_decode(self):

        p=pl.encode([(38.5, -120.2), (40.7, -120.9), (43.2, -126.4)], 5)

        test_output = [{'lat':38.5, 'lng':-120.2}, {'lat':40.7, 'lng':-120.9}, {'lat':43.2, 'lng':-126.4}]
        self.assertEqual(self.test_view_specific.decode_polyline(p), test_output)

    def test_get_polyline(self):

        results = [{'journey':[{'travel_mode':'TRANSIT', 'trip_id': 'id', 'start_seq':1, 'end_seq':5}]}]
        test_output = [{'journey': [{'travel_mode': 'TRANSIT', 'trip_id': 'id', 'start_seq': 1, 'end_seq': 5, 'polyline': [{'lat': 123.0, 'lng': 123.0}]}]}]
        self.assertEqual(self.test_view_specific.get_polyline_coords(results), test_output)

    def test_get_route_list(self):

        list_stop_short=[406]
        test_output={'all': ['145','155','25','25a', '25b','25d', '26', '46a',
        '66','66a','66b', '66e', '67','7b','7d'], 406: ['145', '66','26','66b','66a','155','25b','25a','25',
        '67', '46a','66e','25d','7b','7d']}
        self.assertEqual(self.test_view_specific.get_routes_for_list_of_stops(list_stop_short), test_output)

    def test_direct_route(self):
        start_stations={'list_stop_long': ['8220DB001070'], 'list_stop_short':[1070], '8220DB001070': {'short': 1070, 'distance': 24, 'walking_time': 21}}
        end_stations={'list_stop_long': ['8220DB001359'], 'list_stop_short':[1359], '8220DB001359': {'short': 1359, 'distance': 409, 'walking_time': 368}}
        start_routes={'all':['83', '14'], 1070:['83']}
        end_routes={'all':['83', '12'], 1359:['83']}
        services=Calendar.objects.filter(service_id='2#1')
        time='23:11'
        prediction_digit=0
        self.assertEqual(type(self.test_view_specific.find_direct_routes(start_stations, end_stations, start_routes, end_routes, services, time, prediction_digit)), list)

    def test_crossover_route(self):
        start_stations={'list_stop_long': ['8220DB001169'], 'list_stop_short':[1169], '8220DB001169': {'short': 1169, 'distance': 660, 'walking_time': 594}}
        end_stations={'list_stop_long': ['8240DB000562'], 'list_stop_short':[562], '8240DB000562': {'short': 562, 'distance': 395, 'walking_time': 355}}
        start_routes={'all':['15'], 1169:['15']}
        end_routes={'all':['31'], 562:['31']}
        services=Calendar.objects.filter(service_id='2#1')
        time='10:0'
        prediction_day=1
        self.assertEqual(type(self.test_view_specific.bus_crossover(start_stations, start_routes, end_stations, end_routes, services, time, prediction_day)), list)

    def test_format(self):
        result=[{'duration': 14700.0, 'journey': [{'duration_sec': 594, 'instruction': 'Walk to Rathmines, Rathmines Park',
        'start_lat': 53.322943599999995, 'start_lon': -6.2772334, 'end_lat': 53.3200562645616, 'end_lon': -6.26855785990236,
        'distance': 660, 'travel_mode': 'WALKING', 'start_time': '10:0', 'end_time': '10:09',
        'markers': [53.322943599999995, -6.2772334, 53.3200562645616, -6.26855785990236]},

        {'instruction': 'Bus towards Busáras', 'trip_headsign': 'Outside Luas Station - Maryfield Drive', 'start_time': '12:46',
        'end_time': '13:09', 'start_lat': 53.3200562645616, 'start_lon': -6.26855785990236, 'end_lat': 53.3495336866973,
        'end_lon': -6.25228215714751, 'travel_mode': 'TRANSIT', 'route': '14', 'arrival_stop': 496, 'departure_stop': 1169,
        'markers': [53.3200562645616, -6.26855785990236, 53.3495336866973, -6.25228215714751], 'start_seq': 34, 'end_seq': 48,
        'trip_id': '5780.2.60-14-b12-1.129.I', 'duration_sec': 1380.0, 'polyline': [{'lat': 53.3200562645616, 'lng': -6.26855785990236}]},

        {'instruction': 'Bus towards Howth, Bodeen House', 'trip_headsign': 'Talbot Street - Howth Summit', 'start_time': '13:35',
        'end_time': '14:16', 'start_lat': 53.3495336866973, 'start_lon': -6.25228215714751, 'end_lat': 53.3818815925972,
        'end_lon': -6.05915461887034, 'travel_mode': 'TRANSIT', 'route': '31', 'arrival_stop': 562, 'departure_stop': 496,
        'markers': [53.3495336866973, -6.25228215714751, 53.3818815925972, -6.05915461887034], 'start_seq': 3, 'end_seq': 49,
        'trip_id': '449.2.60-31-b12-1.165.O', 'duration_sec': 2460.0, 'polyline': [{'lat': 53.3495336866973, 'lng': -6.25228215714751}]},

        {'duration_sec': 355, 'instruction': 'Walk to destination', 'start_lat': 53.3818815925972, 'start_lon': -6.05915461887034,
        'end_lat': 53.3785693, 'end_lon': -6.0570132000000285, 'distance': 395, 'travel_mode': 'WALKING', 'start_time': '14:00',
        'end_time': '14:05', 'markers': [53.3818815925972, -6.05915461887034, 53.3785693, -6.0570132000000285]}]}]


        output=[{'directions': [{'instruction': 'Walk to Rathmines, Rathmines Park', 'time': 9, 'start_time': '10:0',
        'end_time': '10:09', 'travel_mode': 'WALKING'}, {'instruction': 'Wait for bus', 'time': 157.0, 'travel_mode': 'WALKING'},
        {'instruction': '14 towards 14áras', 'time': 23.0, 'start_time': '12:46', 'end_time': '13:09', 'travel_mode': '14'},
        {'instruction': 'Wait for bus', 'time': 26.0, 'travel_mode': 'WALKING'}, {'instruction': '31 towards Howth, Bodeen House',
        'time': 41.0, 'start_time': '13:35', 'end_time': '14:16', 'travel_mode': '31'}, {'instruction': 'Walk to destination', 'time': 5,
        'start_time': '14:00', 'end_time': '14:05', 'travel_mode': 'WALKING'}], 'map': {'markers': [{'lat': 53.322943599999995, 'lng': -6.2772334,
        'route': '', 'stop': ''}, {'lat': 53.3200562645616, 'lng': -6.26855785990236, 'route': '14', 'stop': 496},
        {'lat': 53.3495336866973, 'lng': -6.25228215714751, 'route': '31', 'stop': 562}, {'lat': 53.3818815925972, 'lng': -6.05915461887034},
        {'lat': 53.3818815925972, 'lng': -6.05915461887034, 'route': '', 'stop': ''}], 'polyline': [{'lat': 53.322943599999995, 'lng': -6.2772334},
        {'lat': 53.3200562645616, 'lng': -6.26855785990236}, {'lat': 53.3495336866973, 'lng': -6.25228215714751}, {'lat': 53.3818815925972,
        'lng': -6.05915461887034}]}, 'duration': 261.0}]
        self.assertEqual(self.test_view_specific.format_response(result), output)

    def test_get_full_journey(self):
        services=Calendar.objects.filter(service_id='2#1')
        time='10:0'
        prediction_day=0
        date='15-08-2019'
        p=pl.encode([(38.5, -120.2), (40.7, -120.9), (43.2, -126.4)], 5)

        route={'routes':[{'legs':[{'steps':[
        {'distance': {'value': 902},
        'duration': {'value': 669},
        'end_location': {'lat': 53.3188054, 'lng': -6.278130399999999},
        'html_instructions': 'Walk to Harolds Cross, Kenilworth Square North',
        'polyline':
        {'points': p},
        'start_location': {'lat': 53.3229403, 'lng': -6.2773135},
        'travel_mode': 'WALKING'},

        {'distance': {'value': 4358},
        'duration': {'value': 1080},
        'end_location': {'lat': 53.3286404, 'lng': -6.2293996},
        'html_instructions': 'Bus towards Crumlin Childrens Hospital - Newgrove Avenue',
        'polyline': {'points': p},
        'start_location': {'lat': 53.3187381, 'lng': -6.2780827},
        'transit_details':
        {'arrival_stop': {
        'location': {'lat': 53.3286404, 'lng': -6.2293996},
        'name': 'Ballsbridge, Merrion Road RDS'},
        'arrival_time': {'value': 1565861880},
        'departure_stop': {
        'location': {'lat': 53.3187381, 'lng': -6.2780827},
        'name': 'Harolds Cross, Kenilworth Square North'},
        'departure_time': {'value': 1565860800},
        'headsign': 'Crumlin Childrens Hospital - Newgrove Avenue',
        'line': {'agencies': [{'name': 'Go-Ahead'}], 'short_name': '18'},
        'num_stops': 16}, 'travel_mode': 'TRANSIT'},

        {'distance': { 'value': 8855},
        'duration': {'value': 1696},
        'end_location': {'lat': 53.29017030000001, 'lng': -6.131013},
        'html_instructions': 'Bus towards Loughlinstown Pk',
        'polyline': {'points':p},
        'start_location': {'lat': 53.3286404, 'lng': -6.2293996},
        'transit_details':
        {'arrival_stop':
        {'location': {'lat': 53.29017030000001, 'lng': -6.131013},
        'name': "George's St Upper"},
        'arrival_time': {'value': 1565864346},
        'departure_stop': {
        'location': {'lat': 53.3286404, 'lng': -6.2293996},
        'name': 'Ballsbridge, Merrion Road RDS'},
        'departure_time': {'value': 1565862650},
        'headsign': 'Loughlinstown Pk',
        'line': {'agencies': [{'name': 'Dublin Bus'}], 'short_name': '7a'},
        'num_stops': 26}, 'travel_mode': 'TRANSIT'}
        ]}]}]}
        #Beacuse we can't create entries using a composit key. This will always return an empty set
        self.assertEquals(self.test_view_specific.get_full_journeys(route, time, services, prediction_day, date), [])


class TouristPlannerTest(TestCase):
    """
    UnitTests for StopsAutoComplete
    """

    def setUp(self):
        """
        Setup fake models for testing
        """
        Touristattractions.objects.create(
            name="C",
            lat=3.3,
            lon=4.4,
            description="this",
            rating=3.3,
            raters=2,
            address="ee"
        )
        Touristattractions.objects.create(
            name='EPIC The Irish Emigration Museum',
            lat=3.3,
            lon=4.4,
            description="this",
            rating=3.3,
            raters=2,
            address="ee"
        )
        Touristattractions.objects.create(
            name="Glasnevin Cemetery Museum",
            lat=3.3,
            lon=4.4,
            description="this",
            rating=3.3,
            raters=2,
            address="ee"
        )
        Touristattractions.objects.create(
            name="Guinness Storehouse",
            lat=3.3,
            lon=4.4,
            description="this",
            rating=3.3,
            raters=2,
            address="ee"
        )
        Costs.objects.create(
            origin=Touristattractions.objects.create(
                name="A",
                lat=3.3,
                lon=4.4,
                description="this",
                rating=3.3,
                raters=2,
                address="ee"
            ),
            destination=Touristattractions.objects.create(
                name="B",
                lat=3.3,
                lon=4.4,
                description="this",
                rating=3.3,
                raters=2,
                address="ee"
            ),
            cost=7
        )

        self.factory = RequestFactory()

        self.request = self.factory.get("""/api/touristplanner/?attractions=["Trinity+College+Dublin","The+Spire","Guinness+Storehouse"]&home=Westin""")
        self.test_view = self.setup_view(TouristPlanner(),
                                                  self.request)

        def tearDown(self):
            del self.test_view


    def setup_view(self, view, request, *args, **kwargs):
        """
        Sets up view so its methods can be called and tested
        """
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

    def test_format_tourist_route(self):
        route1=(['College Green Westmoreland St', 'EPIC The Irish Emigration Museum', 'College Green Westmoreland St'], 2540)
        route2=(['College Green Westmoreland St', 'EPIC The Irish Emigration Museum', 'Glasnevin Cemetery Museum',  'College Green Westmoreland St'], 15585)
        route3=(['College Green Westmoreland St', 'EPIC The Irish Emigration Museum', 'Glasnevin Cemetery Museum', 'Guinness Storehouse', 'College Green Westmoreland St'], 15585)
        home='College Green Westmoreland St'
        home_coords={'lat': '53.3455715', 'lon': '-6.258648999999991'}
        time='12:51'
        date='15-08-2019'
        output1=[
        {'number': 1, 'attraction': 'College Green Westmoreland St to EPIC The Irish Emigration Museum', 'start_lat': '53.3455715', 'start_lon': '-6.258648999999991', 'end_lat': '3.3', 'end_lon': '4.4', 'time': '12:51', 'date': '15-08-2019'},
        {'number': 2, 'attraction': 'EPIC The Irish Emigration Museum to College Green Westmoreland St', 'start_lat': 3.3, 'start_lon': 4.4, 'end_lat': '53.3455715', 'end_lon': '-6.258648999999991', 'time': '12:51', 'date': '15-08-2019'}]
        self.assertEqual(self.test_view.format_route(route1, home, home_coords, time, date), output1)

    def test_get_best_route(self):
        attractions=[['College Green Westmoreland St', 'EPIC The Irish Emigration Museum', 'College Green Westmoreland St']]
        r = redis.Redis()
        r.flushall()
        self.assertEqual(self.test_view.get_best_route(attractions)[0], ['College Green Westmoreland St', 'EPIC The Irish Emigration Museum', 'College Green Westmoreland St'])
        self.assertEqual(self.test_view.get_best_route(attractions)[0], ['College Green Westmoreland St', 'EPIC The Irish Emigration Museum', 'College Green Westmoreland St'])

    def test_get_attractions(self):
        """
        Should return tourist attractions as array
        """
        expected = [
            "Trinity College Dublin",
            "The Spire",
            "Guinness Storehouse",
        ]
        self.assertEqual(self.test_view.get_attractions(), expected)

    def test_get_home(self):
        """
        Should return home as string
        """
        self.assertEqual(self.test_view.get_home(), "Westin")

    def test_remove_home_from_attractions(self):
        """
        Should return attractions without home as array
        """
        test_input = [
            "Trinity College Dublin",
            "The Spire",
            "Guinness Storehouse",
            "Westin"
        ]

        expected = [
            "Trinity College Dublin",
            "The Spire",
            "Guinness Storehouse",
        ]
        self.assertEqual(self.test_view.remove_home_from_attractions(test_input, "Westin"), expected)


    def test_add_home(self):
        """
        Should return permuatations with home added as array of arrays
        """
        test_input = [
            ['A', 'B', 'C'],
            ['B', 'A', 'C'],
            ['C', 'A', 'B'],
            ['A', 'C', 'B'],
            ['B', 'C', 'A'],
            ['C', 'B', 'A'],

        ]
        expected = [
            ['D', 'A', 'B', 'C', 'D'],
            ['D', 'B', 'A', 'C', 'D'],
            ['D', 'C', 'A', 'B', 'D'],
            ['D', 'A', 'C', 'B', 'D'],
            ['D', 'B', 'C', 'A', 'D'],
            ['D', 'C', 'B', 'A', 'D'],

        ]
        self.assertEqual(self.test_view.add_home(test_input, "D"), expected)

    def test_get_cost_from_database(self):
        """
        Should return cost as int
        """
        self.assertEqual(self.test_view.get_cost_from_database("A", "B"), 7)
