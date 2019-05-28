import requests
import pickle
import sys
from datetime import datetime, timedelta
from io import StringIO
import numpy as np

# set the base URL for the requests to ping
baseurl = "https://tidesandcurrents.noaa.gov/api/datagetter"

# set the payload for the request
payload = {
    'station': 8454000,             # Providence, RI
    'units': 'metric',
    'time_zone': 'gmt',
    'application': 'ports_screen',
    'format': 'csv',
    'datum': 'MSL',                 # reference point for water level is MSL (mean sea level)

    # will be assigned dynamically
    'begin_date': None,
    'end_date': None,
    'product': None,
}

products = ['air_temperature', 'water_temperature', 'air_pressure', 'water_level']

directions = {
    'N': 0, 'NNE': 1, 'NE': 2, 'ENE': 3, 'E': 4, 'ESE': 5, 'SE': 6, 'SSE': 7,
    'S': 8, 'SSW': 9, 'SW': 10, 'WSW': 11, 'W': 12, 'WNW': 13, 'NW': 14, 'NNW': 15, '': -1
}

date_format = '%Y%m%d'

def fetch(payload, converters=None):
    r = requests.get(baseurl, params=payload)
    csv = StringIO(r.content.decode('utf-8'))

    # If the station does not have data, skip this fetch
    if "Error: No data was found" in csv.read():
        return None

    # convert all datetimes to epoch time
    conv = lambda x: int(datetime.strptime(x.decode('utf-8'), '%Y-%m-%d %H:%M').timestamp())
    csv.seek(0)
    data = np.genfromtxt(csv, delimiter=',', skip_header=1, dtype=int, converters={0: conv})[:,0]
    logical = data % 360 == 0   # only select dates every six minutes to clean data

    # reset the IO stream and use the logical array to filter the data to only be every six minutes
    csv.seek(0)
    data = np.genfromtxt(csv, delimiter=',', skip_header=1, converters=converters)
    data = data[logical,:]
    return data


def get_data(begin_date, end_date):
    '''
    Collects data on the products in the products array for a range of dates

    :param begin_date: the start date of the entries
    :type begin_date: datetime.datetime
    :param end_date: the end date of the entries
    :type begin_date: datetime.datetime
    :return: a numpy array of the product data for the given date range
    '''
    # set the payload to have the requested begin and end date range, and product
    payload['begin_date'] = begin_date.strftime(date_format)
    payload['end_date'] = end_date.strftime(date_format)

    # deal with wind first since it has a different format
    payload['product'] = 'wind'

    # lambda function to convert wind direction to numerical value
    def cb(x):
        try:
            return float(directions[x.decode('utf-8')])
        except KeyError:
            return -1.0
    callback = lambda x: cb(x)

    arr = fetch(payload, converters={3: callback})
    if arr is None:
        return None
    arr = arr[:,1:5]    # cols 1-4 are wind speed, direction, cardinal direction, and gust

    for p in products:
        payload['product'] = p

        new_cols = fetch(payload)
        if new_cols is None:
            return None

        # reshape the data so that it is a 2d column vector
        new_cols = np.reshape(new_cols[:,1], (new_cols.shape[0], 1))

        # append the data to the arr variable
        try:
            arr = np.append(arr, new_cols, axis=1)
        # N.B. sometimes the data gets corrupted somehow. If that happens, skip this 31-day window and continue
        except ValueError:
            return None

    return arr

def collect_recent_data(start_date):
    '''
    Collects data from start date to the present

    :param start_date: the time to start collecting data
    :return: a large numpy array of all the data since the start date
    '''
    now = datetime.now()
    start = datetime.strptime(start_date, date_format)
    delta = timedelta(30)
    end = now if start + delta > now else start + delta
    print("Now gathering data from {} to {}...".format(start.strftime('%m/%d/%Y'), end.strftime('%m/%d/%Y')))
    arr = get_data(start, end)

    while end != now:
        start = end + timedelta(1)
        end = now if start + delta > now else start + delta
        print("Now gathering data from {} to {}...".format(start.strftime('%m/%d/%Y'), end.strftime('%m/%d/%Y')))
        data = get_data(start, end)

        # only append if the data was not corrupted somehow
        if data is not None:
            arr = np.append(arr, data, axis=0)
        print('Done, {} total data rows'.format(arr.shape[0]))

    return arr[~np.isnan(arr).any(axis=1)]


if __name__ == "__main__":
    start_date = sys.argv[1]
    data = collect_recent_data(start_date)
    print("All done! Pickling data...")
    with open('{}.pkl'.format(start_date), 'wb') as pkl_file:
        pickle.dump(data, pkl_file, protocol=pickle.HIGHEST_PROTOCOL)
    print("Done. Data saved in {}.pkl".format(start_date))

