from pyxs import Client



with Client(xen_bus_path="/dev/xen/xenbus") as c:
	domU_id = c.read("domid".encode())
	path = "/local/domain/"+domU_id.decode()+'vic'
	path = path.encode()
	msg= ""
	while msg!='q':
		msg=input('->')
		c.write(path,msg.encode())
		print(msg)
	# print(c.get_perms("/local/domain".encode()))
	# print(c.list(b"/local/domain"))
	# c.write(b'/local/domain/4/vic',b'heyy')
	# print(c.get_perms(b"/local/domain/4/vic"))

	# except:
	# 	print("nope")

	# print(c.read(b'/local/domain/'))



