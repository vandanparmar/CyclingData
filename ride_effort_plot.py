from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import gpxpy
import numpy as np
import json
import power_curve_gen

mass = 78
bike_mass = 10.0
t_m = mass + bike_mass
g = 9.81
area = 0.4
earth_r = 6371000
C_d = 1.0
rho = 1.225


plt.rcParams['figure.facecolor'] = 'black'
plt.rcParams['axes.facecolor'] = 'black'
plt.rcParams['axes3d.grid'] = False
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['axes.edgecolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'




def add_powers(data,box_pts_list,power_curve):
	power = np.clip(data['power'],0.0,np.inf)/t_m
	ts = data['ts']
	all_prop_powers = []
	for box_pts in box_pts_list:
		smoothed = power_curve_gen.smooth(power,box_pts)
		box_pts_left = int(np.ceil(box_pts/2))
		box_pts_right = int(np.floor(box_pts/2))
		pad_left = np.array([ts[0]]*box_pts_left + list(ts[:-box_pts_left]))
		pad_right = np.array(list(ts[box_pts_right:]) + [ts[-1]]*box_pts_right)
		times = pad_right-pad_left
		times = list(map(lambda x : x.total_seconds(),times))[:-2]
		print(np.mean(times),np.max(times))
		max_powers = max_power(np.array(times),power_curve)
		prop_powers = smoothed/max_powers
		all_prop_powers.append(prop_powers)
	data['prop_powers'] = all_prop_powers
	return data

def max_power(time,power_curve):
	return np.interp(x=time, xp=power_curve[:,0], fp=power_curve[:,1])

if __name__=='__main__':

	filename = 'data/20180404-1-Ride.gpx'

	power_curve  = np.array(json.load(open('power_curve_vp.json','r'))['power_curve'][::-1])

	box_pts_list = [5,60,300,1200]

	time_names = ['5s','1min','5min','20min']

	gpx_data = gpxpy.parse(open(filename,'r'))
	json_data = power_curve_gen.make_json_data(gpx_data)
	json_data = power_curve_gen.add_power_to_json(json_data)
	box_pts_list = [i for i in box_pts_list if i<len(json_data['ts'])-2]
	time_names = time_names[:len(box_pts_list)]
	json_data = add_powers(json_data,box_pts_list,power_curve)

	plot_type = 'time'

	if plot_type=='time':
		x_axis = list(map(lambda x: x.total_seconds()/60,json_data['ts'][:-2]-json_data['ts'][0]))
		x_label = 'Time / minutes'
	elif plot_type=='distance':
		x_axis = np.cumsum(json_data['ds'])[:-1]/1609
		x_label = 'Distance / miles'
	elev = np.cumsum(json_data['d_elev'])[:-1]
	elev = elev-np.min(elev)
	vs = json_data['vs'][:-1]


	fig,axes = plt.subplots(nrows = 2+len(box_pts_list),sharex=True)

	for i,ax in enumerate(axes):
		if i==0:
			ax.plot(x_axis,vs*2.237,color='deepskyblue')
			ax.set_ylabel('Speed / $mph	$')
		elif i==1:
			ax.plot(x_axis,elev,color='limegreen')
			ax.set_ylabel('Elevation / $m$')
		else:
			y_data = np.array(json_data['prop_powers']).T[:,i-2]
			points = np.array([x_axis, y_data]).T.reshape(-1, 1, 2)
			segments = np.concatenate([points[:-1], points[1:]], axis=1)
			norm = plt.Normalize(0,0.9)
			lc = LineCollection(segments,norm=norm,cmap = 'magma')
			lc.set_array(np.power(y_data,0.8))
			ax.add_collection(lc)
			ax.set_ylabel(time_names[i-2]+' effort')
			ax1 = ax.twinx()
			ax1.set_yticks([]) 
			ax1.plot(x_axis,elev,color='limegreen',alpha=0.3)
			ax2 = ax.twinx()
			ax2.set_yticks([])
			ax2.plot(x_axis,vs*2.237,color='deepskyblue',alpha=0.3)
			if i==len(axes)-1:
				ax.set_xlabel(x_label)

	plt.show()
