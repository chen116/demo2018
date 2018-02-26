from pyxs import Client

with Client(xen_bus_path="/dev/xen/xenbus") as c:
	c.write(b'/local/domain/5/vic2',b'hey')
	c.set_perms(b"/local/domain/5/vic2",[b'b5',b'b0'])
with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
	m = c.monitor()
	m.watch(b"/local/domain/4/vic2", b"a unique token")
	msg = ""
	while msg!='q':
		print((next(m.wait()))[0])
		msg = c.read(b'/local/domain/4/vic2').decode()
		print(msg)

	# c.set_perms(b"/local/domain/4/vic2",[b'b4',b'b0'])

