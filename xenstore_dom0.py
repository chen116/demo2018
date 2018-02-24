from pyxs import Client
with Client(xen_bus_path="/dev/xen/xenbus") as c:
	c.set_perms(b"/local/domain/4/name",[b'n4',b'n0'])

