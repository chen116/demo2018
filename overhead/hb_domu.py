


# thruput

import heartbeat
window_size_hr=5
hb = heartbeat.Heartbeat(1024,window_size_hr,10000,"vic.log",10,100)
#             shm_key, win_size,buf_depth,log_file,min_target,max_target):
# monitoring_items = ["heart_rate","app_mode","frame_size","timeslice"]
# comm = heartbeat.DomU(monitoring_items)
print("start")
for i in range(10000):
# hb stuff
	hb.heartbeat_beat()
	# window_hr = hb.get_window_heartrate()
# #print("hb: before get_instant_heartrate()")
print(hb.get_instant_heartrate())
# #print("hb: after hb stuff")
# if global_cnt>window_size_hr:
# 	comm.write("heart_rate",window_hr)
# # #print('------------------window_hr:',window_hr)
# # #print('instant_hr:',instant_hr)
# current_checked = checked.get()
# if previous_checked!=current_checked:
# 	comm.write("app_mode",current_checked)
# 	previous_checked=current_checked
# if previous_f_size!=current_f_size:
# 	comm.write("frame_size",current_f_size)
# 	previous_f_size=current_f_size
# current_ts=ts1.get()
# if previous_ts!=current_ts:
# 	comm.write("timeslice",current_ts)
# 	previous_ts=current_ts