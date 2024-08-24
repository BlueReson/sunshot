import pandas as pd
import datetime as dt
from skyfield.api import N,S,E,W, wgs84, load
import pytz
from timezonefinder import TimezoneFinder

# location Port of Den Helder, Nieuwe diep:
lat = 52 + (57 / 60) + (26.9 / 3600)
lon = 4 + (46 / 60) + (37.5 / 3600)
height_m = 6

# Skyfield setup
ts = load.timescale()
planets = load('de421.bsp') # plantary ephemeris dictionary
earth, sun = planets['earth'], planets['sun']
locale = earth + wgs84.latlon(lat * N, lon * E, elevation_m=height_m)

# input data
df = pd.read_csv('data/raw-gyro.csv')
#print(df.head())


# functions ----------------------------------------------------------------------
def dms_to_decimal(degrees, minutes, seconds):
    """
    Convert degrees, minutes, seconds to decimal degrees.
    
    Args:
        degrees (pd.Series or int or float): Degrees part of DMS.
        minutes (pd.Series or int or float): Minutes part of DMS.
        seconds (pd.Series or int or float): Seconds part of DMS.
        
    Returns:
        pd.Series or float: Decimal degrees.
    """
    decimal_degrees = degrees + minutes / 60 + seconds / 3600
    return decimal_degrees

def decimal_to_dms(decimal_degrees):
    """
    Convert decimal degrees to DMS format.
    
    Args:
        decimal_degrees (float or pd.Series): Decimal degrees to convert.
        
    Returns:
        str or pd.Series: DMS formatted string.
    """
    def convert_to_dms_string(dd):
        is_positive = dd >= 0
        dd = abs(dd)
        degrees = int(dd)
        minutes = int((dd - degrees) * 60)
        seconds = (dd - degrees - minutes / 60) * 3600
        sign = '' if is_positive else '-'
        dms_string = u'{0}{1}°{2:02}′{3:05.1f}″'.format(sign, degrees, minutes, seconds)
        return dms_string

    if isinstance(decimal_degrees, pd.Series):
        return decimal_degrees.apply(convert_to_dms)
    else:
        return convert_to_dms_string(decimal_degrees)

# Functie om UTC naar lokale tijd te converteren op basis van lat/lon en datum
def utc_to_localtime(utc_dt, lat=lat, lon=lon):
    # Definieer de tijdzone op basis van lat/lon
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    local_zone = pytz.timezone(timezone_str)
    
    # Zet de datetime naar een aware datetime in UTC
    utc_zone = pytz.utc
    utc_dt = utc_zone.localize(utc_dt)
    
    # Converteer naar lokale tijd
    local_dt = utc_dt.astimezone(local_zone)
    
    return local_dt

# Functie om de juiste kolomnaam te bepalen en de waarde toe te voegen
def add_localtime_column(row):
    utc_dt = row['UTC']
    local_dt = utc_to_localtime(utc_dt)
    
    if local_dt.tzname() == 'CEST':
        row['localtime_CEST'] = local_dt
    else:
        row['localtime_CET'] = local_dt
    
    return row

# Functie om de azimut te berekenen
def calculate_azimuth(utc_time):
    t = ts.utc(utc_time.year, utc_time.month, utc_time.day, utc_time.hour, utc_time.minute, utc_time.second)
    astro = locale.at(t).observe(sun)
    app = astro.apparent()
    _, az, _ = app.altaz()
    return az.degrees

def convert_dms_to_decimal(row, deg_col, min_col, sec_col):
    degrees = row[deg_col]
    minutes = row[min_col]
    seconds = row[sec_col]
    decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
    return round(decimal_degrees, 3)  # Afgerond op drie decimalen



# ---------------------------------------------------------------- 
# Convert the UTC column to datetime objects with UTC timezone
df['UTC'] = pd.to_datetime(df['UTC'], format='%d-%m-%Y %H:%M:%S') # [0]

print(df.head)

df['obs_sun_dec'] = df.apply(lambda row: convert_dms_to_decimal(row, 'obs_sun_deg', 'obs_sun_min', 'obs_sun_sec'), axis=1)
#df['obs_sun_decimal'] = dms_to_decimal(df['obs_sun_deg'], df['obs_sun_min'], df['obs_sun_sec']) #[1]
#df = df.drop(df.columns[[1, 2, 3]], axis=1)  # (remove raw D M S columns) df.columns is zero-based pd.Index 




# Calculate azimuth for each row in the DataFrame and round to three decimal places
df['azimuth(Zn)'] = df['UTC'].apply(calculate_azimuth).round(3) 

df['Zn_dms'] = df['azimuth(Zn)'].apply(decimal_to_dms)
#df['gyro_obs_dms'] = df['obs_gyro_deg_true'].apply(decimal_to_dms)

# Convert UTC datetime objects to string with Zulu time format
df['UTC'] = df['UTC'].dt.strftime('%d-%m-%Y %H:%M:%S%z')
print(df)
print(f"column names: {df.columns.values.tolist()}")

df_reorder =df['fix_nr','datetime_UTC','localtime_CET','obs_sun_decimal','']

