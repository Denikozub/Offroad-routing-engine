import pandas as pd


def parse_gpx(filename):
    track = open(filename).read()
    point_count = track.count('<trkpt')
    point = 0
    lat = []
    lon = []
    for i in range(point_count):
        point = track.find('<trkpt', point + 1)
        coords = track[point:track.find('\n', point)].split('"')
        lat.append(float(coords[1]))
        lon.append(float(coords[3]))
    return pd.DataFrame({'lat': lat, 'lon': lon})


def shift_forw(lst):
    new_lst = lst.copy()
    new_lst.insert(0, new_lst.pop())
    return new_lst


def shift_back(lst):
    new_lst = lst.copy()
    new_lst.append(new_lst.pop(0))
    return new_lst


def shift_df(df_coords):
    df_shifted = pd.DataFrame({'prev_lat': (shift_forw(list(df_coords.lat))-df_coords.lat),
                               'prev_lon': (shift_forw(list(df_coords.lon))-df_coords.lon)})
    wpt = [56.30682, 38.29001]
    df_shifted['wpt_lat'] = df_coords.lat - wpt[0]
    df_shifted['wpt_lon'] = df_coords.lon - wpt[1]
    return df_shifted
