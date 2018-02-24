from pyxs import Client
with Client(xen_bus_path="/dev/xen/xenbus") as c:
	try:
		print(c.get_perms("/local/domain".encode()))
		print(c.list(b"/local/domain").decode())
		c.write(b'/local/domain/4/vic',b'heyy')
		print(c.get_perms(b"/local/domain/4/vic"))
	except:
		print("nope")

	# print(c.read(b'/local/domain/'))



