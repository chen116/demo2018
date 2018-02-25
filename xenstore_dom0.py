from pyxs import Client
with Client(xen_bus_path="/dev/xen/xenbus") as c:
	# c.write(b'/local/domain/4/vic2',b'hey')
	c.set_perms(b"/local/domain/4/vic2",[b'b4',b'b0'])

