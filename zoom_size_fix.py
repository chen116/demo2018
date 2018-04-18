from foscam_v3 import FoscamCamera
import pprint
import time

mycam1 = FoscamCamera('65.114.169.139',88,'arittenbach','8mmhamcgt16!')
mycam2 = FoscamCamera('65.114.169.151',88,'admin','admin')

pprint.pprint(mycam1.get_video_stream_param()[1])
pprint.pprint(mycam2.get_video_stream_param()[1])

pprint.pprint(mycam1.set_infra_led_config(1))
pprint.pprint(mycam2.set_infra_led_config(1))

pprint.pprint(mycam1.get_infra_led_config(1))
pprint.pprint(mycam2.get_infra_led_config(1))
# mycam2.zoomOut()
# mycam1.zoomOut()
# time.sleep(1)
# mycam2.zoomStop()
# mycam1.zoomStop()





# Original output:
# Send Foscam command: http://65.114.169.139:88/cgi-bin/CGIProxy.fcgi?usr=arittenbach&pwd=8mmhamcgt16!&cmd=getVideoStreamParam
# Received Foscam response: 0, {'isVBR3': '1', 'isVBR1': '1', 'bitRate1': '2097152', 'bitRate0': '2097152', 'bitRate3': '2097152', 'bitRate2': '1048576', 'GOP2': '60', 'GOP3': '30', 'GOP0': '30', 'GOP1': '60', 'isVBR0': '1', 'frameRate1': '20', 'frameRate0': '30', 'frameRate3': '30', 'frameRate2': '15', 'resolution1': '0', 'resolution0': '6', 'resolution3': '0', 'resolution2': '3', 'isVBR2': '1'}
# {'GOP0': '30',
#  'GOP1': '60',
#  'GOP2': '60',
#  'GOP3': '30',
#  'bitRate0': '2097152',
#  'bitRate1': '2097152',
#  'bitRate2': '1048576',
#  'bitRate3': '2097152',
#  'frameRate0': '30',
#  'frameRate1': '20',
#  'frameRate2': '15',
#  'frameRate3': '30',
#  'isVBR0': '1',
#  'isVBR1': '1',
#  'isVBR2': '1',
#  'isVBR3': '1',
#  'resolution0': '6',
#  'resolution1': '0',
#  'resolution2': '3',
#  'resolution3': '0'}
# Send Foscam command: http://65.114.169.151:88/cgi-bin/CGIProxy.fcgi?usr=admin&pwd=admin&cmd=getVideoStreamParam
# Received Foscam response: 0, {'isVBR3': '1', 'isVBR1': '1', 'bitRate1': '2097152', 'bitRate0': '2097152', 'bitRate3': '2097152', 'bitRate2': '1048576', 'GOP2': '60', 'GOP3': '30', 'GOP0': '30', 'GOP1': '60', 'isVBR0': '1', 'frameRate1': '20', 'frameRate0': '30', 'frameRate3': '30', 'frameRate2': '15', 'resolution1': '0', 'resolution0': '0', 'resolution3': '0', 'resolution2': '3', 'isVBR2': '1'}
# {'GOP0': '30',
#  'GOP1': '60',
#  'GOP2': '60',
#  'GOP3': '30',
#  'bitRate0': '2097152',
#  'bitRate1': '2097152',
#  'bitRate2': '1048576',
#  'bitRate3': '2097152',
#  'frameRate0': '30',
#  'frameRate1': '20',
#  'frameRate2': '15',
#  'frameRate3': '30',
#  'isVBR0': '1',
#  'isVBR1': '1',
#  'isVBR2': '1',
#  'isVBR3': '1',
#  'resolution0': '0',
#  'resolution1': '0',
#  'resolution2': '3',
#  'resolution3': '0'}