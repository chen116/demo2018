from pyxs import Client
with Client(xen_bus_path="/dev/xen/xenbus") as c:
	print(c.read(b"/local/domain/4/name"))

