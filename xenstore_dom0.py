from pyxs import Client
with Client(xen_bus_path="/dev/xen/xenbus") as c:
	c.write(b'/local/domain/5/vic',b'hey')
	# c.set_perms(b"/local/domain/4/vic",[b'b4',b'b0'])

