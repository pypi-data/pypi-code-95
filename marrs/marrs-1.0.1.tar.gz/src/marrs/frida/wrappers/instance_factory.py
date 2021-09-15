from .instances import Array, Instance


class InstanceFactory:
	@staticmethod
	def create(agent, instance_data):
		if instance_data.get('is_array'):
			return Array(instance_data, agent)

		return Instance(instance_data, agent)
