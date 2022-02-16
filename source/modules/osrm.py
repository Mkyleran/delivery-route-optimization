import pandas as pd
import requests
import time

# Open Source Routing Machine (OSRM) API
# Documentation: http://project-osrm.org/docs/v5.24.0/api/?language=Python

class OSRM():
    """
    Python wrapper for the OSRM API v5.24.0
    
    Parameters
    ----------
    version:
        Version of the protocol implemented by the service. v1 for all OSRM 5.x
        installations
    profile:
        Mode of transportation, is determined statically by the Lua profile 
        that is used to prepare the data using osrm-extract. Typically car, 
        bike or foot if using one of the supplied profiles.
    format_:
        json or flatbuffers. This parameter is optional and defaults to json.
    
    General Request Options
    bearings: {bearing};{bearing}[;{bearing} ...]
        Limits the search to segments with given bearing in degrees towards 
        true north in clockwise direction.
    radiuses: {radius};{radius}[;{radius} ...]
        Limits the search to given radius in meters.
    generate_hints: true (default), false
        Adds a Hint to the response which can be used in subsequent requests, 
        see hints parameter.
    hints: {hint};{hint}[;{hint} ...]
        Hint from previous request to derive position in street network.
    approaches: {approach};{approach}[;{approach} ...]
        Keep waypoints on curb side.
    exclude: {class}[,{class}]
        Additive list of classes to avoid, order does not matter.
    snapping: default (default), any
        Default snapping avoids is_startpoint (see profile) edges, any will 
        snap to any edge in the graph
    skip_waypoints: true, false (default)
        Removes waypoints from the response. Waypoints are still calculated, 
        but not serialized. Could be useful in case you are interested in some
        other part of response and do not want to transfer waste data.
    """
    
    def __init__(
        self,
        base_url: 'str'='http://127.0.0.1:8080',
        version='v1',
        profile: 'str'='car',
        # default options
        # format_: 'str'='json',
        # bearings=None,
        # radiuses=None,
        # generate_hints: 'bool'=True,
        # hints=None,
        # approaches: 'str | list(str)'='unrestricted',
        # exclude=None,
        # snapping: 'str'='default',
        # skip_waypoints: 'bool'=False,
    ):
        self.base_url = base_url
        self.version = version
        self.profile = profile
        # self.format = format_
        # self.bearings = bearings
        # self.radiuses = radiuses
        # self.generate_hints = generate_hints
        # self.hints = hints
        # self.approaches = approaches
        # self.exclude = exclude
        # self.snapping = snapping
        # self.skip_waypoints = skip_waypoints
        
    
    def parse_parameters(
        self,
        params
    ):
        """
        params: locals()
            Dictionary of function parameters 
        """
        
        # Remove forbidden keys
        params = {k: v for k, v in params.items() 
                  if k not in ['self', 'coordinates', 'url'] 
                  if v is not None}
        
        for k, v in params.items():
            if isinstance(v, bool):
                params[k] = str(v).lower()
            elif isinstance(v, str):
                params[k] = v.lower()
            elif isinstance(v, int):
                params[k] = str(v)
            elif isinstance(v, list):
                if isinstance(v[0], int):
                    params[k] = ';'.join([str(_) for _ in v])
                elif isinstance(v[0], str):
                    params[k] = ','.join([str(_) for _ in v])

        return params
    
    
    def route(
        self,
        coordinates,
        alternatives: 'bool | int'=False,
        steps: 'bool'=False,
        annotations: 'bool | str'=False,
        geometries: 'str'='polyline',
        overview: 'str'='simplified',
        continue_straight: 'str | bool'='default',
        waypoints: 'list(int) | None'=None
    ):
        """
        Finds the fastest route between coordinates in the supplied order.

        Parameters
        ----------
        coordinates
            DF, GDF
            Must contain features ['longitude', 'latitude']
        alternatives: true, false (default), or Number
            Search for alternative routes. Passing a number alternatives=n
            searches for up to n alternative routes. Please note that even if
            alternative routes are requested, a result cannot be guaranteed.
        step: true, false (default)
            Returned route steps for each route leg
        annotations: true, false (default), nodes, distance, duration, 
            datasources, weight, speed
            Returns additional metadata for each coordinate along the route
            geometry.
            # TODO: annotations can be a list(str)
        geometries: polyline (default), polyline6, geojson
            Returned route geometry format (influences overview and per step)
        overview: simplified (default), full, false
            Add overview geometry either full, simplified according to highest
            zoom level it could be display on, or not at all.
        continue_straight: default (default), true, false
            Forces the route to keep going straight at waypoints constraining
            uturns there even if it would be faster. Default value depends on 
            the profile.
        waypoints: {index};{index};{index}...
            Treats input coordinates indicated by given indices as waypoints in 
            returned Match object. Default is to treat all input coordinates as
            waypoints.

        Returns
        -------
        response: Requests response object
        """
        
        parameters = self.parse_parameters(params=locals())
        
        # Parse coordinates
        coordinates = (
            coordinates[['longitude', 'latitude']]
            .agg(','.join, axis=1)
            .str.cat(sep=';')
        )

        url = (f'{self.base_url}/route/{self.version}/{self.profile}/'
               + coordinates)

        tick = time.time()
        response = requests.get(url=url, params=parameters)
        print(time.time() - tick)
        return response


    def table(
        self,
        coordinates,
        sources: "list | 'all'"='all',
        destinations: "list | 'all'"='all',
        annotations: 'str | list(str)'='duration',
        fallback_speed: 'float'=None,
        fallback_coordinate: 'str'='input',
        scale_factor: 'float'=None
    ):
        """
        Computes the duration of the fastest route between all pairs of
        supplied coordinates. Returns the durations or distances or both
        between the coordinate pairs. Note that the distances are not the
        shortest distance between two coordinates, but rather the distances of
        the fastest routes. Duration is in seconds and distances is in meters.

        Parameters
        ----------
        coordinates
            DF, GDF
            Must contain features ['longitude', 'latitude']
        sources: {index};{index}[;{index} ...] or all (default)
            Use location with given index as source.
        destinations: {index};{index}[;{index} ...] or all (default)
            Use location with given index as destination.
        annotations: duration (default) or distance
            Return the requested table or tables in response.
        fallback_speed: double > 0
            If no route found between a source/destination pair, calculate the
            as-the-crow-flies distance, then use this speed to estimate
            duration.
        fallback_coordinate: input (default), or snapped
            When using a fallback_speed, use the user-supplied coordinate
            (input), or the snapped location (snapped) for calculating
            distances.
        scale_factor: double > 0
            Use in conjunction with annotations=durations. Scales the table 
            duration values by this number.

        Returns
        -------
        response: Requests response object
        """

        parameters = self.parse_parameters(params=locals())
        
        coordinates = (
            coordinates[['longitude', 'latitude']]
            .agg(','.join, axis=1)
            .str.cat(sep=';')
        )

        url = (f'{self.base_url}/table/{self.version}/{self.profile}/'
               + coordinates)

        tick = time.time()
        response = requests.get(url=url, params=parameters)
        print(time.time() - tick)
        return response
    
    def match(
        self,
        coordinates,
        steps: 'bool'=False,
        geometries: 'str'='polyline',
        annotations: 'bool | str'=False,
        overview: 'str'='simplified',
        timestamps: 'list(int)'=None,
        radiuses: 'list(float)'=None,
        gaps: 'str'='split',
        tidy: 'bool'=False,
        waypoints: 'list(int)'=None
    ):
        """
        Map matching matches/snaps given GPS points to the road network in the
        most plausible way. Please note the request might result multiple 
        sub-traces. Large jumps in the timestamps (> 60s) or improbable 
        transitions lead to trace splits if a complete matching could not be 
        found. The algorithm might not be able to match all points. Outliers 
        are removed if they can not be matched successfully.

        Parameters
        ----------
        coordinates
            DF, GDF
            Must contain features ['longitude', 'latitude']
        steps: true, false (default)
            Returned route steps for each route
        geometries: polyline (default), polyline6, geojson
            Returned route geometry format (influences overview and per step)
        annotations: true, false (default), nodes, distance, duration,
            datasources, weight, speed
            Returns additional metadata for each coordinate along the route 
            geometry.
        overview: simplified (default), full, false
            Add overview geometry either full, simplified according to highest
            zoom level it could be display on, or not at all.
        timestamps: {timestamp};{timestamp}[;{timestamp} ...]
            integer seconds since UNIX epoch
            Timestamps for the input locations in seconds since UNIX epoch. 
            Timestamps need to be monotonically increasing.
        radiuses: {radius};{radius}[;{radius} ...]
            double >= 0 (default 5m)
            Standard deviation of GPS precision used for map matching. If 
            applicable use GPS accuracy.
        gaps: split (default), ignore
            Allows the input track splitting based on huge timestamp gaps 
            between points.
        tidy: true, false (default)
            Allows the input track modification to obtain better matching 
            quality for noisy tracks.
        waypoints: {index};{index};{index}...
            Treats input coordinates indicated by given indices as waypoints in
            returned Match object. Default is to treat all input coordinates as
            waypoints.

        Returns
        -------
        response: Requests response object
        """

        parameters = self.parse_parameters(params=locals())
        
        coordinates = (
            coordinates[['longitude', 'latitude']]
            .agg(','.join, axis=1)
            .str.cat(sep=';')
        )

        url = (f'{self.base_url}/match/{self.version}/{self.profile}/'
               + coordinates)

        tick = time.time()
        response = requests.get(url=url, params=parameters)
        print(time.time() - tick)
        return response

    
    def trip(
        self,
        coordinates,
        roundtrip: 'bool'=True,
        source: 'str'='any',
        destination: 'str'='any',
        steps: 'bool'=False,
        annotations: 'bool | str'=False,
        geometries: 'str'='polyline',
        overview: 'str'='simplified'
    ):
        """
        The trip plugin solves the Traveling Salesman Problem using a greedy 
        heuristic (farthest-insertion algorithm) for 10 or more waypoints and
        uses brute force for less than 10 waypoints. The returned path does not
        have to be the fastest path. As TSP is NP-hard it only returns an 
        approximation. Note that all input coordinates have to be connected for
        the trip service to work.

        Parameters
        ----------
        coordinates: String of format 
        {longitude},{latitude};{longitude},{latitude}
            [;{longitude},{latitude} ...] 
        or polyline({polyline})
        or polyline6({polyline6}).
            DF, GDF
            Must contain features ['longitude', 'latitude']
        roundtrip: true (default), false
            Returned route is a roundtrip (route returns to first location)
        source: any (default), first
            Returned route starts at any or first coordinate
        destination: any (default), last
            Returned route ends at any or last coordinate
        steps: true, false (default)
            Returned route instructions for each trip
        annotations: true, false (default), nodes, distance, duration, 
            datasources,weight, speed
            Returns additional metadata for each coordinate along the route 
            geometry.
        geometries: polyline (default), polyline6, geojson
            Returned route geometry format (influences overview and per step)
        overview: simplified (default), full, false
            Add overview geometry either full, simplified according to highest
            zoom level it could be display on, or not at all.

        Returns
        -------
        response: Requests response object
        """

        parameters = self.parse_parameters(params=locals())
        
        coordinates = (
            coordinates[['longitude', 'latitude']]
            .agg(','.join, axis=1)
            .str.cat(sep=';')
        )

        url = (f'{self.base_url}/trip/{self.version}/{self.profile}/'
               + coordinates)

        tick = time.time()
        response = requests.get(url=url, params=parameters)
        print(time.time() - tick)
        return response

    
def osrm_call(service: 'int', coordinates):
    # Example /{service}/{version}/{profile}/{coordinates}[.{format}]?option=value&option=value
    api_url = 'http://127.0.0.1:8080/'
    services = ['route', 'nearest', 'table', 'match', 'trip', 'tile']

    coordinates = (
        coordinates[['longitude', 'latitude']]
        .agg(','.join, axis=1)
        .str.cat(sep=';')
    )
    # options
    approaches = ['curb', 'unrestricted']

    url = api_url + services[service] + '/v1/driving/' + coordinates

    parameters = {
        'steps': 'true',  # for route, trip service
        'annotations': 'true'
        # 'annotations': 'duration,distance',  # for table service
        # 'geometries': 'geojson'
    }

    tick = time.time()
    r = requests.get(url=url, params=parameters)
    print(time.time() - tick)
    return r

if __name__ == '__main__':
    pass