"""
The place to reacting information from the server
"""
import queue
import time
from typing import List, TYPE_CHECKING

from mcdreforged import constant
from mcdreforged.info import Info
from mcdreforged.reactor.abstract_reactor import AbstractReactor
from mcdreforged.utils import misc_util, file_util

if TYPE_CHECKING:
	from mcdreforged import MCDReforgedServer


class InfoReactorManager:
	def __init__(self, mcdr_server: 'MCDReforgedServer'):
		self.mcdr_server = mcdr_server
		self.last_queue_full_warn_time = None
		self.reactors = []  # type: List[AbstractReactor]

	def load_reactors(self, folder):
		for file in file_util.list_file_with_suffix(folder, constant.REACTOR_FILE_SUFFIX):
			module = misc_util.load_source(file)
			if callable(getattr(module, 'get_reactor', None)):
				self.reactors.append(module.get_reactor(self.mcdr_server))

	def process_info(self, info: Info):
		for reactor in self.reactors:
			try:
				reactor.react(info)
			except:
				self.mcdr_server.logger.exception(self.mcdr_server.tr('mcdr_server.react.error', type(reactor).__name__))  # TODO: fix translation

	def put_info(self, info):
		try:
			self.mcdr_server.task_executor.add_info_task(lambda: self.process_info(info))
		except queue.Full:
			current_time = time.time()
			logging_method = self.mcdr_server.logger.debug
			if self.last_queue_full_warn_time is None or current_time - self.last_queue_full_warn_time >= constant.REACTOR_QUEUE_FULL_WARN_INTERVAL_SEC:
				logging_method = self.mcdr_server.logger.warning
				self.last_queue_full_warn_time = current_time
			logging_method(self.mcdr_server.tr('mcdr_server.info_queue.full'))