import tqdm
import gpxpy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from xml.dom import minidom

file = 'Lunch_Run.gpx'
gpx_file = open(file,'r')
data = gpxpy.parse(gpx_file)

mass = 78
bike_mass = 4.6
t_m = mass + bike_mass
g = 9.81
area = 0.4
earth_r = 6371000
C_d = 1.0
rho = 1.225

xmldoc = minidom.parse(file)
hrs = xmldoc.getElementsByTagName('gpxtpx:hr')
hrs = list(map(lambda x : int(x.firstChild.nodeValue),hrs))

gpx_file
points = data.tracks[0].segments[0].points
points = list(map(lambda x: [x.latitude,x.longitude,x.elevation,x.time],points))
cols = ['lat','long','elev','time']
points = pd.DataFrame(points,columns=cols)
points['hr'] = hrs
points

points['d_lat'] = np.zeros(len(points))
points['d_lat'][1:] = np.deg2rad(np.diff(points['lat']))
points['d_long'] = np.zeros(len(points))
points['d_long'][1:] = np.deg2rad(np.diff(points['long']))
points['d_elev'] = np.zeros(len(points))
points['d_elev'][1:] = np.diff(points['elev'])
points['d_time'] = np.zeros(len(points))
points['d_time'][1:] = np.diff(points['time'])/(10**9)

h_d_lat_2 = np.power(np.sin(points['d_lat'][1:]/2),2)
cos_cos = np.multiply(np.cos(np.deg2rad(points['lat'][1:])),np.cos(np.deg2rad(points['lat'][:-1])))
h_d_lon_2 = np.power(np.sin(points['d_long'][1:]/2),2)
cc_h_d_lon_2 = np.multiply(cos_cos, h_d_lon_2)

ds = 2*earth_r*np.arcsin(np.sqrt(cc_h_d_lon_2+h_d_lat_2))
points['ds'] = np.zeros(len(points))
points['ds'][1:] = ds

points['vs'] = np.divide(points['ds'],points['d_time'],out=np.zeros_like(points['d_time']), where=points['d_time']!=0)

points

plt.scatter(points['vs'],points['hr'].rolling(10).mean())
