from pyxs import Client




keys = ["heart_rate"]
base_path = '/local/domain'
with Client(xen_bus_path="/dev/xen/xenbus") as c:
	domU_id = c.read("domid".encode())
	for key in keys:
		tmp_key_path = (base_path+'/'+domU_id.decode()+'/'+key).encode()
	msg= ""
	while msg!='q':
		msg=input('->')
		for key in keys:
			tmp_key_path = (base_path+'/'+domU_id.decode()+'/'+key).encode()
			c.write(tmp_key_path,msg.encode())
	# print(c.get_perms("/local/domain".encode()))
	# print(c.list(b"/local/domain"))
	# c.write(b'/local/domain/4/vic',b'heyy')
	# print(c.get_perms(b"/local/domain/4/vic"))

	# except:
	# 	print("nope")

	# print(c.read(b'/local/domain/'))


