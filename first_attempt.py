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

def find_optimal(fba_points):
	fba_points.sort(key = lambda x : x[0],reverse = True)
	to_return = []
	current_max = -np.inf
	for point in fba_points:
		if point[1] > current_max:
			current_max = point[1]
			to_return.append(point)
	return to_return

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def make_json_data(gpx_data):
	points = gpx_data.tracks[0].segments[0].points
	lat = np.array(list(map(lambda x : x.latitude,points)))
	lon = np.array(list(map(lambda x : x.longitude,points)))
	elev = np.array(list(map(lambda x : x.elevation,points)))
	ts = np.array(list(map(lambda x : x.time,points)))
	d_lat = np.deg2rad(np.diff(lat))
	d_lon = np.deg2rad(np.diff(lon))
	d_elev = np.diff(elev)
	d_ts = np.array(list(map(lambda x: x.total_seconds(),np.diff(ts))))

	h_d_lat_2 = np.power(np.sin(d_lat/2),2)
	cos_cos = np.multiply(np.cos(np.deg2rad(lat[1:])),np.cos(np.deg2rad(lat[:-1])))
	h_d_lon_2 = np.power(np.sin(d_lon/2),2)
	cc_h_d_lon_2 = np.multiply(cos_cos, h_d_lon_2)

	ds = 2*earth_r*np.arcsin(np.sqrt(cc_h_d_lon_2+h_d_lat_2))
	vs = ds/d_ts
	if (len(vs)<10):
		box_pts = len(vs)-1
	else:
		box_pts = 10
	smooth_vs = smooth(vs, box_pts)
	to_return = {'d_elev':d_elev,'d_ts':d_ts,'ds':ds,'vs':smooth_vs,'rough_vs':vs,'ts':ts}
	return to_return

def add_power_to_json(data):
	d_KE = np.diff(np.power(data['vs'],2))*t_m*0.5
	d_GPE = t_m*g*data['d_elev'][:-1]/data['d_ts'][:-1]
	P_drag = 0.5*C_d*area*rho*np.power(data['vs'][:-1],3)
	P_kin = (d_KE + d_GPE)/data['d_ts'][:-1]
	power = P_drag + P_kin
	data['power'] = power
	return data

def power_curve(data):
	power = np.clip(data['power'],0.0,np.inf)/t_m
	ts = data['ts']
	powers = []
	times = []
	box_pts = 4
	while box_pts<len(power):
		smoothed = smooth(power, box_pts)
		p = np.max(smoothed)
		arg = np.argmax(smoothed)
		if arg-box_pts<0:
			min_arg = 0
		else:
			min_arg = arg-box_pts
		time = (ts[arg]-ts[min_arg]).total_seconds()
		if(time>1500):
			break

		times.append(time)
		powers.append(p)
		box_pts+=int(np.ceil(0.07*box_pts))
	return powers,times
if __name__ == '__main__':
	data = []

	for file in tqdm(sorted(os.listdir(path))):
		gpx_file = open(path+file,'r')
		data.append(make_json_data(gpxpy.parse(gpx_file)))
		data[-1] = add_power_to_json(data[-1])


	# for datum in data:
	# 	power = datum['power']
	# 	mean = np.mean(power)
	# 	print(mean)

	all_powers = []
	all_times = []

	plt.rcParams['figure.facecolor'] = 'black'
	plt.rcParams['axes.facecolor'] = 'black'
	plt.rcParams['text.color'] = 'white'
	plt.rcParams['axes.labelcolor'] = 'white'
	plt.rcParams['axes.edgecolor'] = 'white'
	plt.rcParams['xtick.color'] = 'white'
	plt.rcParams['ytick.color'] = 'white'
	show_recent = True
	for i,datum in enumerate(tqdm(data)):
		powers, times = power_curve(datum)
		all_powers.extend(powers)
		all_times.extend(times)
		if show_recent:
			plt.semilogx(times,powers,color = 'deepskyblue',alpha = 0.1+0.9*1.2**i/1.2**len(data),markersize=3)
		else:
			plt.semilogx(times,powers,color='deepskyblue',markersize=3)
	plt.xlabel('Time')
	plt.ylabel('Power / $W kg^{-1}$')
	plt.xticks([5,10,30,60,120,300,600,1200],['5s','10s','30s','1min','2min','5min','10min','20min'])
	plt.xlim([4.5,1250])
	plt.show()
	points = list(zip(all_times,all_powers))
	points = [x for x in points if x[0]<1300]
	to_save = {'power_curve':find_optimal(points)}	
	print(to_save)
	with open('power_curve_vp.json','w') as outfile:
		json.dump(to_save,outfile)

