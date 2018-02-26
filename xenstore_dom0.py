from pyxs import Client
from pyxs import Router
from pyxs.connection import XenBusConnection

import pyxs

with Client(xen_bus_path="/dev/xen/xenbus") as c:
	c.write(b'/local/domain/5/vic',b'init_key_vic')
	c.set_perms(b"/local/domain/5/vic",[b'b5',b'b0'])
	c.write(b'/local/domain/4/vic',b'init_key_vic')
	c.set_perms(b"/local/domain/4/vic",[b'b4',b'b0'])



router = Router(pyxs.connection.UnixSocketConnection())




with Client(router=router) as c:
	m = c.monitor()
	m.watch(b"/local/domain/4/vic", b"a-unique-token")
	print(c.router.is_connected)
	c.router.subscribe(b"a-unique-token",m)
	c.router.start()



# with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
# 	m = c.monitor()
# 	m.watch(b"/local/domain/4/vic", b"a-unique-token")
# 	msg = ""


# 	while msg!='q':
# 		print((next(m.wait()))[0])
# 		msg = c.read(b'/local/domain/4/vic').decode()
# 		print(msg)



