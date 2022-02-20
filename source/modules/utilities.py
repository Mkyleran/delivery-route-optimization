from modules import credentials

import pandas as pd
import geopandas as gpd
import polyline

import plotly.express as px
import plotly.graph_objects as go

import googlemaps
# Open Calgary API
from sodapy import Socrata

from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import AgglomerativeClustering
from sklearn.pipeline import Pipeline


YYC_STREET_TYPEs = {
    # https://www.calgary.ca/pda/pd/addressing.html#Addressing
    'AL': 'Alley',
    'AV': 'Avenue',
    'BA': 'Bay',
    'BV': 'Boulevard',
    'CA': 'Cape',
    'CE': 'Centre',
    'CI': 'Circle',
    'CL': 'Close',
    'CM': 'Common',
    'CO': 'Court',
    'CV': 'Cove',
    'CR': 'Crescent',
    'DR': 'Drive',
    'GD': 'Gardens',
    'GA': 'Gate',
    'GR': 'Green',
    'GV': 'Grove',
    'HE': 'Heath',
    'HT': 'Heights',
    'HI': 'Highway',
    'HL': 'Hill',
    'IS': 'Island',
    'LN': 'Lane',
    'LI': 'Link',
    'MR': 'Manor',
    'ME': 'Mews',
    'MT': 'Mount',
    'PR': 'Parade',
    'PA': 'Park',
    'PY': 'Parkway',
    'PS': 'Passage',
    'PH': 'Path',
    'PL': 'Place',
    'PZ': 'Plaza',
    'PT': 'Point',
    'RI': 'Rise',
    'RD': 'Road',
    'RO': 'Row',
    'SQ': 'Square',
    'ST': 'Street',
    'TC': 'Terrace',
    'TR': 'Trail',
    'VW': 'View',
    'VI': 'Villas',
    'WK': 'Walk',
    'WY': 'Way'
}


def load_data():
    """
    Load Open Calgary address data set
    """
    # Load saved sample file
    add = pd.read_csv(
        '../data/openYYCtestdata.csv',
        usecols=['address', 'longitude', 'latitude']
    )

    return df_to_geodf(add)


def polyline_to_geodf(geometry: 'str'):
    """
    Convert a polyline string to a GeoDataframe
    
    Parameters
    ----------
    geometry: polyline string
    
    Returns
    -------
    a: GeoDataframe
    """
    pl = polyline.decode(expression=geometry)
    a = pd.DataFrame(pl, columns=['latitude', 'longitude'])
    a = df_to_geodf(a)
    return a


def googlemaps_geocode(address: 'str'):
    """
    Geocode an address via Google Maps geocode API
    
    Parameters
    ----------
    address: string
        
    Returns
    -------
    loc: Dataframe
    
    TODO
    ----
    - check how 'short_name' impacts street_number for appartment units
    """
    gmaps = googlemaps.Client(key=credentials.GOOGLE_API_KEY)
    geocode_result = gmaps.geocode(
        address=address,
        components={
            'administrative_area_level_1': 'Alberta',
            'country': 'Canada'
        },
        language='English'
    )
    address = pd.json_normalize(geocode_result[0], record_path=['address_components'])
    address = ' '.join(address.loc[0:1, 'short_name']).upper()
    
    loc = pd.json_normalize(geocode_result[0]['geometry']['location'])
    loc.rename(columns={'lat': 'latitude',
                        'lng': 'longitude'}, inplace=True)
    
    loc['address'] = address
    
    loc = df_to_geodf(loc)
    
    return loc


def open_calgary_geocode(address: 'str'):
    """
    Look up address by exact match in Open Calgary Parcel Address database.
    
    Format: #UNIT house_number STREET NAME STREET_TYPE STREET_QUAD
    Example: #7V 20 COUNTRY HILLS VW NW
    
    Parameters
    ----------
    address: string
        
    Returns
    -------
    results_df: Dataframe
    
    TODO
    ----
    Test this function
    """
    
    client = Socrata(
        domain="data.calgary.ca",
        app_token=credentials.OPEN_YYC_APP_TOKEN
    )

    address = address.upper()

    results = client.get(
        dataset_identifier="9zvu-p8uz",
        where=f'ADDRESS = "{address}"',
    )
    
    if len(results) == 0:
        print('No address found.')
        return
    
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    
    return results_df


def df_to_geodf(df):
    """
    Convert Dataframe to GeoDataframe
    
    Parameters
    ----------
    df: Dataframe
        df contains columns 'latitude' and 'longitude'.
        
    Returns
    -------
    gdf: GeoDataframe
        gdf has added column 'geometry' of POINT geometries.
    """
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['longitude'], df['latitude'])
    )
    
    return gdf


def label_routes(
    n_routes: 'int',
    matrix: 'str'='../data/duration_matrix_20220216-222102.csv'
):
    """

    Parameters
    ----------
    n_routes: integer
        The number of routes to generate equal to the number of drivers
        available
    matrix: string
        Filename of distance matrix to use

    Returns
    -------
    List of route numbers, where the index corresponds to the address
    """

    # Load distance matrix
    df = pd.read_csv(matrix, header=None)

    # Build pipeline
    estimators = [
        ('scaler', MinMaxScaler()),
        ('clustering', AgglomerativeClustering(
            n_clusters=n_routes, 
            affinity='precomputed', 
            linkage='complete'
        ))
    ]

    pipe = Pipeline(estimators)

    pipe.fit(df)

    return pipe['clustering'].labels_


def plot_routes(route_table, addresses, warehouse):
    """
    Plot routes with paths.
    
    Parameters
    ----------
    route_table: Dataframe
        The output of OSRM.tsp_polylines()
    
    Returns
    -------
    None
    
    TODO
    ----
    - See if folium does a better job with plotting
    - Route based colour schemes
    """
    
    fig = go.Figure()
    traces = []
    
    for i, route in route_table.iterrows():
        # Plot route
        t = polyline_to_geodf(route['geometry'])

        fig.add_scattermapbox(
            mode="lines",
            lat=t.geometry.y,
            lon=t.geometry.x,
            name=f'Route {i + 1}', 
            # fill='toself'
        )

        # Plot stops
        waypoints = pd.json_normalize(route['waypoints'])
        waypoints.drop(columns=['location', 'hint'], inplace=True)

        c = addresses[['address', 'longitude', 'latitude']][addresses['route'] == i]
        # Add warehouse as source
        c = pd.concat([warehouse, c], axis=0)
        c.reset_index(drop=True, inplace=True)

        stops = pd.concat(
            [
                c,
                waypoints[['waypoint_index', 'distance']]
            ],
            axis=1
        )

        stops = utilities.df_to_geodf(stops)
    
        fig2 = px.scatter_mapbox(
            stops,
            lat=stops.geometry.y,
            lon=stops.geometry.x,
            color='waypoint_index',
            hover_name='waypoint_index',
            hover_data=['address']
        )
        fig.add_trace(fig2.data[0])

    fig.update_layout(
        margin ={'l':0,'t':0,'b':0,'r':0},
        mapbox = {
            'style': "open-street-map",
            'center': {'lon': -114.03, 'lat': 51.04},
            'zoom': 8
        },
        coloraxis={'colorscale': 'rainbow'}
    )

    fig.show()
    return


if __name__ == '__main__':
    pass