''' Inspired by http://andykee.com/visualizing-strava-tracks-with-python.html '''

from matplotlib import pyplot as plt
import gpxpy
import os
from tqdm import tqdm
import numpy as np
import json


path = './data/'

mass = 78
bike_mass = 4.6
t_m = mass + bike_mass
g = 9.81
area = 0.4
earth_r = 6371000
C_d = 1.0
rho = 1.225


data = []

for file in tqdm(sorted(os.listdir(path))):
	gpx_file = open(path+file,'r')
	data.append(gpxpy.parse(gpx_file))

all_lat = []
all_lon = []
print(len(data))
for ride in tqdm(data):
	this_lat = []
	this_lon = []
	for track in ride.tracks:
		for segment in track.segments:
			for point in segment.points:
				this_lon.append(point.longitude)
				this_lat.append(point.latitude)
	all_lat.append(this_lat)
	all_lon.append(this_lon)

fig = plt.figure(facecolor = '0.05')
ax = plt.Axes(fig, [0., 0., 1., 1.], )
ax.set_aspect('equal')
ax.set_axis_off()
fig.add_axes(ax)
for lat,lon in zip(all_lat, all_lon):
	plt.plot(lon, lat, color = 'deepskyblue', lw = 0.2, alpha = 0.8)
plt.show()