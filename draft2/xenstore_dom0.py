from pyxs import Client
# from pyxs import Router
# from pyxs.connection import XenBusConnection



domu_ids = []
keys = ["heart_rate","tager_rate"]
base_path = '/local/domain'
with Client(xen_bus_path="/dev/xen/xenbus") as c:
	for x in c.list(base_path.encode()):
		domu_ids.append(x.decode())
	domu_ids.pop(0)
	for domuid in domu_ids:
		permissions = []
		permissions.append(('b'+'0').encode())
		permissions.append(('b'+domuid).encode())
		for key in keys:
			tmp_key_path = (base_path+'/'+domuid+'/'+key).encode()
			tmp_val = ('init').encode()
			c.write(tmp_key_path,tmp_val)
			c.set_perms(tmp_key_path,permissions)
			print('created',key,'for dom',domuid)
with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
	m = c.monitor()
	for domuid in domu_ids:
		for key in keys:
			tmp_key_path = (base_path+'/'+domuid+'/'+key).encode()
			token = (key+' '+domuid).encode()
			m.watch(tmp_key_path,token)
			print('watching',key,'for dom',domuid)
	num_done = 0
	while num_done < len(domu_ids):
		path,token=next(m.wait())
		msg=c.read(path).decode()
		print( token.decode(),':',msg)
		if msg=='q':
			num_done+=1

# with Client(xen_bus_path="/dev/xen/xenbus") as c:
# 	c.write(b'/local/domain/5/vic',b'init_key_vic')
# 	c.set_perms(b"/local/domain/5/vic",[b'b5',b'b0'])
# 	c.write(b'/local/domain/4/vic',b'init_key_vic')
# 	c.set_perms(b"/local/domain/4/vic",[b'b4',b'b0'])
# with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
# 	m = c.monitor()
# 	m.watch(b"/local/domain/4/vic", b"dom4")
# 	m.watch(b"/local/domain/5/vic", b"dom5")
# 	msg = ""
# 	while msg!='q':
# 		print("from",(next(m.wait()))[0])
# 		msg = c.read(b'/local/domain/4/vic').decode()
# 		print(msg)



