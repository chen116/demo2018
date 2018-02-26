from pyxs import Client
# from pyxs import Router
# from pyxs.connection import XenBusConnection

domU_ids = []
with Client(xen_bus_path="/dev/xen/xenbus") as c:
	domU_ids = c.list(b'/local/domain')
	for x in domU_ids:
		x = x.decode()
	print(domU_ids)
	c.write(b'/local/domain/5/vic',b'init_key_vic')
	c.set_perms(b"/local/domain/5/vic",[b'b5',b'b0'])
	c.write(b'/local/domain/4/vic',b'init_key_vic')
	c.set_perms(b"/local/domain/4/vic",[b'b4',b'b0'])


with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
	m = c.monitor()
	m.watch(b"/local/domain/4/vic", b"dom4")
	m.watch(b"/local/domain/5/vic", b"dom5")
	msg = ""
	while msg!='q':
		print("from",(next(m.wait()))[0])
		msg = c.read(b'/local/domain/4/vic').decode()
		print(msg)



