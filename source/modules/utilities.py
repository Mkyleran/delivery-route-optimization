import pandas as pd
import geopandas as gpd
import polyline

import googlemaps


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


def geocode(address: 'str'):
    """
    Geocode an address via Google Maps geocode API
    
    Parameters
    ----------
    address: string
        
    Returns
    -------
    loc: Dataframe
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


if __name__ == '__main__':
    pass