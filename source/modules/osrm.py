import pandas as pd
import numpy as np
import math
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
        Parameters
        ----------
        params: locals()
            Dictionary of function parameters
        
        Returns
        -------
        params: dictionary
            Parsed parameters
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
    
    
    def parse_coordinates(
        self,
        coordinates
    ):
        """
        Parse coordinate columns from dataframe into OSRM coordinate string
        format.
        Example: longitude,latitude;longitude,latitude ...
        
        Parameters
        ----------
        coordinates: Dataframe
            Contains columns ['latitude', 'longitude']
        
        Returns
        -------
        coordinates: string
        """
        # Parse coordinates
        coordinates = (
            coordinates[['longitude', 'latitude']].astype(str)
            .agg(','.join, axis=1)
            .str.cat(sep=';')
        )
        
        return coordinates
    
    
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
        
        # Parse parameters
        parameters = self.parse_parameters(params=locals())
        
        # Parse coordinates
        coordinates = self.parse_coordinates(coordinates)

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

        # Parse parameters
        parameters = self.parse_parameters(params=locals())
        
        # Parse coordinates
        coordinates = self.parse_coordinates(coordinates)
        
        url = (f'{self.base_url}/table/{self.version}/{self.profile}/'
               + coordinates)

        tick = time.time()
        response = requests.get(url=url, params=parameters)
        print(time.time() - tick)
        
        return response
    
    
    def large_table(
        self, 
        locations,
        # file_name: 'str | None'=None
    ):
        """
        Calculate the distance and duration matrix using the OSRM table API
        for more than 100 locations and save each to its own csv
        
        Parameters
        ----------
        locations: Dataframe
        
        Returns
        -------
        None
        """
        
        num_locations = locations.shape[0]
        
        duration_matrix = np.empty((0, num_locations))
        distance_matrix = np.empty((0, num_locations))
        # duration_matrix = pd.DataFrame()
        
        ceiling = math.ceil(num_locations / 100)

        tick = time.time()

        for i in range(ceiling):
            start_i = i * 100
            end_i = start_i + 100

            duration_row = np.empty((100, 0))
            distance_row = np.empty((100, 0))
            # row = pd.DataFrame()

            if end_i > num_locations:
                end_i = num_locations
                duration_row = np.empty((num_locations - start_i, 0))
                distance_row = np.empty((num_locations - start_i, 0))

            for j in range(ceiling):
                start_j = j * 100
                end_j = start_j + 100

                if end_j > num_locations:
                    end_j = num_locations

                osrm_response = self.table(
                    coordinates=locations,
                    sources=list(range(start_i, end_i)),
                    destinations=list(range(start_j, end_j)),
                    annotations=['duration', 'distance']
                )

                duration_row = np.c_[
                    duration_row, 
                    np.array(osrm_response.json()['durations'])
                ]
                distance_row = np.c_[
                    distance_row,
                    np.array(osrm_response.json()['distances'])
                ]
                # row = pd.concat(
                #    objs=[row, 
                #          pd.DataFrame(osrm_response.json()['durations'])],
                #     axis=1,
                #     ignore_index=True
                # )
            duration_matrix = np.r_[duration_matrix, duration_row]
            distance_matrix = np.r_[distance_matrix, distance_row]
            # duration_matrix = pd.concat(
            #     objs=[duration_matrix, row],
            #     axis=0,
            #     ignore_index=True
            # )
        print('time', time.time() - tick)
        
        np.savetxt(
            fname=f'duration_matrix_{time.strftime("%Y%m%d-%H%M%S")}.csv',
            X=duration_matrix,
            fmt='%10.1f',
            delimiter=','
        )
        np.savetxt(
            fname=f'distance_matrix_{time.strftime("%Y%m%d-%H%M%S")}.csv',
            X=distance_matrix,
            fmt='%10.1f',
            delimiter=','
        )
        # duration_matrix.to_csv('duration_matrix.csv', index=False)
        
        return

    
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

       # Parse parameters
        parameters = self.parse_parameters(params=locals())
        
        # Parse coordinates
        coordinates = self.parse_coordinates(coordinates)

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
            datasources, weight, speed
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

        # Parse parameters
        parameters = self.parse_parameters(params=locals())
        
        # Parse coordinates
        coordinates = self.parse_coordinates(coordinates)

        url = (f'{self.base_url}/trip/{self.version}/{self.profile}/'
               + coordinates)

        tick = time.time()
        response = requests.get(url=url, params=parameters)
        print(time.time() - tick)
        
        return response
        
        
    def tsp(
        self,
        routes,
        source=None
    ):
        """
        For a list of coordinates with route labels, solve the travelling salesman
        problem for each route.

        Parameters
        ----------
        routes: Dataframe
            Dataframe containing coordinates and route labels
        start: Dataframe
            Warehouse

        Returns
        -------
        route_table: Dataframe
            A dataframe of routes with the features:
            geometry: polyline string
            distance: meters float
            duration: seconds float
            waypoints: json object with feature 'waypoint_index' representing
                the route sequence
            stops: number of stops
            weight: float
                "how long this segment takes to traverse, in units (may differ
                from duration when artificial biasing is applied in the Lua 
                profiles). ACTUAL ROUTING USES THIS VALUE."
        """
        
        route_table = pd.DataFrame()

        for route in range(routes['route'].nunique()):
            route_df = routes[routes['route'] == route]
            # Stop count
            stops = route_df.shape[0]

            # Add warehouse as source
            route_df = pd.concat([source, route_df], axis=0)

            # Solve TSP
            path = self.trip(
                coordinates=route_df[:100],  # TSP solvable for maximum 100 stops
                roundtrip=True,
                source='first',
                destination='any',
                overview='full'
            )

            # Extract trip attributes and waypoints
            try:
                # Geometry, distance, duration
                attributes = pd.json_normalize(path.json(), record_path=['trips'])
            except KeyError:
                continue

            # Waypoints
            waypoints = pd.json_normalize(path.json())['waypoints']

            path = pd.concat(
                [attributes, waypoints],
                axis=1
            )

            # Number of stops
            path[['route', 'stops']] = [route, stops]

            # Append route to table of routes
            route_table = pd.concat(
                [route_table, path],
                axis=0,
                ignore_index=True
            )

        # Drop uneccessary columns
        route_table.drop(['legs', 'weight_name'], axis=1, inplace=True)

        return route_table


if __name__ == '__main__':
    pass