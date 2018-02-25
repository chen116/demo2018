from pyxs import Client
with Client(xen_bus_path="/dev/xen/xenbus") as c:
	c.set_perms(b"/local/domain/4/vic2",[b'b4',b'b0'])
with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
	# c.write(b'/local/domain/4/vic2',b'hey')
	m = c.monitor()
	m.watch(b"/local/domain/4/vic2", b"a unique token")
	print(next(m.wait()))
	# print(c.read(b'/local/domain/4/vic2'))
	# c.set_perms(b"/local/domain/4/vic2",[b'b4',b'b0'])

