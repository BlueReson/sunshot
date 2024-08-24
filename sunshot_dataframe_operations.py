import pandas as pd
import datetime as dt
import pytz
from timezonefinder import TimezoneFinder

# Vaste locatie voor alle observaties
lat = 52 + (57 / 60) + (26.9 / 3600)  # Voorbeeld: 52° 57' 26.9" N
lon = 4 + (46 / 60) + (37.5 / 3600)   # Voorbeeld: 4° 46' 37.5" E

# test DataFrame
data = {
    'datetime_UTC': ['31-12-2019 08:41:44', '31-12-2019 08:43:16', '31-12-2019 08:44:12', '31-12-2019 08:44:52'],
    'obs_sun_deg': [343, 344, 344, 344],
    'obs_sun_min': [41, 6, 16, 22],
    'obs_sun_sec': [24, 0, 44, 5],
    'obs_gyro_deg_true': [155.063, 154.985, 155.055, 155.058]
}
df = pd.DataFrame(data)

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
    def convert_to_dms(dd):
        is_positive = dd >= 0
        dd = abs(dd)
        degrees = int(dd)
        minutes = int((dd - degrees) * 60)
        seconds = (dd - degrees - minutes / 60) * 3600
        sign = '' if is_positive else '-'
        dms_string = u'{0}{1}°{2:02}′{3:05.2f}″'.format(sign, degrees, minutes, seconds)
        return dms_string

    if isinstance(decimal_degrees, pd.Series):
        return decimal_degrees.apply(convert_to_dms)
    else:
        return convert_to_dms(decimal_degrees)

df = pd.DataFrame(data)


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
    utc_dt = row['datetime_UTC']
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

# ---------------------------------------------------------------------------------------------------------------------- DATAFRAME MODIFIERS --------------------------------

# Omzetten van de datetime_UTC kolom naar datetime objecten
df['datetime_UTC'] = pd.to_datetime(df['datetime_UTC'])

# Localtime (CET of CEST) berekenen voor elke rij in de DataFrame en toevoegen aan de juiste kolom
df = df.apply(add_localtime_column, axis=1)

# Converteer graden, minuten, seconden naar decimale graden
df['obs_sun_decimal'] = dms_to_decimal(df['obs_sun_deg'], df['obs_sun_min'], df['obs_sun_sec'])

# voeg locale tijd toe

# Converteer decimale graden naar DMS-notatie en sla het op in een nieuwe kolom
df['obs_sun_dms'] = decimal_to_dms(df['obs_sun_decimal'])
df['obs_gyro_dms'] = decimal_to_dms(df['obs_gyro_deg_true'])


# Verwijder de oorspronkelijke DMS-kolommen
df.drop(['obs_sun_deg', 'obs_sun_min', 'obs_sun_sec'], axis=1, inplace=True)


print(df)

