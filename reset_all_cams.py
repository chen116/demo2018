from foscam_v2 import FoscamCamera

mycam1 = FoscamCamera('65.114.169.154',88,'arittenbach','8mmhamcgt16!')
mycam2 = FoscamCamera('65.114.169.108',88,'admin','admin')
mycam1.ptz_reset()
mycam2.ptz_reset()
mycam1.set_ptz_speed(4)
mycam2.set_ptz_speed(4)