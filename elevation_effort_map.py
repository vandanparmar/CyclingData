from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import gpxpy
import numpy as np
import json
import power_curve_gen
import ride_effort_plot
from itertools import repeat
from tqdm import tqdm
mass = 78
bike_mass = 10.0
t_m = mass + bike_mass
g = 9.81
area = 0.4
earth_r = 6371000
C_d = 1.0
rho = 1.225

time = 60

filename = 'data/20180404-1-Ride.gpx'

power_curve  = np.array(json.load(open('power_curve_vp.json','r'))['power_curve'][::-1])

gpx_data = gpxpy.parse(open(filename,'r'))
json_data = power_curve_gen.make_json_data(gpx_data)
json_data = power_curve_gen.add_power_to_json(json_data)
json_data = ride_effort_plot.add_powers(json_data, [time],power_curve)

colour_data = np.array(json_data['prop_powers']).T[:,0]

elev = np.cumsum(json_data['d_elev'])[:-1]
elev = elev-np.min(elev)+10
# elev = list(np.array(list(zip(repeat(0),elev))).flatten())
elev=list(elev)

polys = []

for track in gpx_data.tracks:
	for segment in track.segments:
		for i in tqdm(range(0,len(elev))):
			if (i==0):
				x = [segment.points[0].latitude]*2+[segment.points[-1].latitude]*2
				y = [segment.points[0].longitude]*2+[segment.points[-1].longitude]*2
				z = [0]+[elev[0]]+[elev[-1]]+[0]
			else:
				x = [segment.points[i].latitude]*2+[segment.points[i-1].latitude]*2
				y = [segment.points[i].longitude]*2+[segment.points[i-1].longitude]*2
				z = [0]+[elev[i]]+[elev[i-1]]+[0]
			polys.append(list(zip(x,y,z)))

lat = list(map(lambda x: x.latitude, gpx_data.tracks[0].segments[0].points))
lon = list(map(lambda x: x.longitude, gpx_data.tracks[0].segments[0].points))


# points = list(np.array(points)[:-2])
# print(points)
norm = plt.Normalize(0,0.9)
poly = Poly3DCollection(polys,closed=True,cmap='magma',norm=norm)
poly.set_array(np.power(colour_data,0.8))

fig = plt.figure()
ax = fig.gca(projection='3d',facecolor ='black')
ax.w_xaxis.set_pane_color((0.0,0.0,0.0, 1.0))
ax.w_yaxis.set_pane_color((0.0,0.0,0.0, 1.0))
ax.w_zaxis.set_pane_color((0.0,0.0,0.0, 1.0))
ax.set_xlim(np.min(lat),np.max(lat))
ax.set_xticks([])
ax.set_yticks([])
ax.set_ylim(np.min(lon), np.max(lon))
ax.set_zlim(0, np.max(elev))

ax.add_collection3d(poly)
plt.show()