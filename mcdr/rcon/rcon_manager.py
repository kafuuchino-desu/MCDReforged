"""
A more flexible interface for rcon support
"""
from mcdr.rcon.rcon_connection import RconConnection


# pack everything up and make sure no exception can escape
class RconManager:
	def __init__(self, mcdr_server):
		self.mcdr_server = mcdr_server
		self.logger = mcdr_server.logger
		self.rcon = None

	def is_running(self):
		return self.rcon is not None and self.rcon.socket is not None

	def connect(self, address, port, password):
		if self.is_running():
			self.disconnect()
		self.rcon = RconConnection(address, port, str(password), self.logger)
		try:
			success = self.rcon.connect()
		except Exception as e:
			self.logger.info(self.mcdr_server.tr('rcon_manager.connect.connection_fail', e))
			self.rcon = None
		else:
			if success:
				self.logger.info(self.mcdr_server.tr('rcon_manager.connect.connected'))
			else:
				self.logger.info(self.mcdr_server.tr('rcon_manager.connect.wrong_password'))

	def disconnect(self):
		if self.is_running():
			try:
				self.rcon.disconnect()
				self.logger.info(self.mcdr_server.tr('rcon_manager.disconnect.disconnected'))
			except:
				self.mcdr_server.logger.error(self.mcdr_server.tr('rcon_manager.disconnect.disconnect_fail'))
		self.rcon = None

	def send_command(self, command):
		if self.is_running():
			return self.rcon.send_command(command)
		else:
			return None