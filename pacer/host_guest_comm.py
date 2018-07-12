from pyxs import Client

class Dom0:
	def __init__(self,keys=['heart_rate'],domu_ids=[],base_path='/local/domain'):
		self.domu_ids = domu_ids
		self.keys=keys
		self.base_path=base_path
		with Client(xen_bus_path="/dev/xen/xenbus") as c:
			if domu_ids==[]:
				for x in c.list(base_path.encode()):
					self.domu_ids.append(x.decode())
				self.domu_ids.pop(0)
			for domuid in self.domu_ids:
				permissions = []
				permissions.append(('b'+'0').encode())
				permissions.append(('b'+domuid).encode())
				for key in keys:
					tmp_key_path = (base_path+'/'+domuid+'/'+key).encode()
					tmp_val = ('xenstore entry init').encode()
					c.write(tmp_key_path,tmp_val)
					c.set_perms(tmp_key_path,permissions)
					print('created',key,'for dom',domuid)
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
			# c.write(self.key_path_hash[key],msg)
			success = False
			while not success:
				c.transaction()
				c.write(self.key_path_hash[key],msg)
				success = c.commit()
