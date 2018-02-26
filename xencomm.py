from pyxs import Client
# from pyxs import Router
# from pyxs.connection import XenBusConnection

class Dom0:
	def __init__(self,keys=['test'],base_path='/local/domain'):
		self.domu_ids = []
		self.keys=keys
		self.base_path=base_path
		with Client(xen_bus_path="/dev/xen/xenbus") as c:
			for x in c.list(base_path.encode()):
				self.domu_ids.append(x.decode())
			self.domu_ids.pop(0)
			for domuid in self.domu_ids:
				permissions = []
				permissions.append(('b'+'0').encode())
				permissions.append(('b'+domuid).encode())
				for key in keys:
					tmp_key_path = (base_path+'/'+domuid+'/'+key).encode()
					tmp_val = ('init').encode()
					c.write(tmp_key_path,tmp_val)
					c.set_perms(tmp_key_path,permissions)
					print('created',key,'for dom',domuid)
	def monitor(self):
		with Client(unix_socket_path="/var/run/xenstored/socket_ro") as c:
			m = c.monitor()
			for domuid in self.domu_ids:
				for key in self.keys:
					tmp_key_path = (self.base_path+'/'+domuid+'/'+key).encode()
					token = (key+' '+domuid).encode()
					m.watch(tmp_key_path,token)
					print('watching',key,'of dom',domuid)
			num_done = -1
			while 1:#num_done < len(self.domu_ids):
				path,token=next(m.wait())
				msg=c.read(path).decode()
				print( token.decode(),':',msg)
				if msg=='q':
					num_done+=1
class DomU:
	def __init__(self,keys=['test'],base_path='/local/domain'):
		self.domu_id=""
		self.keys=keys
		self.base_path=base_path
		self.key_path_hash = {}
		with Client(xen_bus_path="/dev/xen/xenbus") as c:
			self.domu_id = c.read("domid".encode())
			for key in self.keys:
				self.key_path_hash[key]=(self.base_path+'/'+self.domu_id.decode()+'/'+key).encode()
	def write(self,key='test',val='0'):
		with Client(xen_bus_path="/dev/xen/xenbus") as c:
			msg=str(val).encode()
			c.write(self.key_path_hash[key],msg)


if __name__ == "__main__":
	c = Dom0()
	c.monitor()
