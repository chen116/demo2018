from pyxs import Client
with Client(xen_bus_path="/dev/xen/xenbus") as c:
	print(c.get_perms(b"/local/domain/4"))
	print(c.list(b"/local/domain/4"))
	# c.write(b'/local/domain/4/vic',b'heyy')
	# print(c.read(b'/local/domain/'))



