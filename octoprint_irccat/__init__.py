# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.events
import socket
import logging

class IrccatPlugin(octoprint.plugin.SettingsPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.EventHandlerPlugin):

        def __init__(self):
                self._logger = logging.getLogger("octoprint.plugins.irccat")
                self._hostname = socket.gethostname()

	def get_settings_defaults(self):
		return dict(
			host="127.0.0.1",
                        port=12345,
                        cost_per_hour=1.50,
                        cost_per_meter=0.2,
                        currency='GBP',
                        channel_or_user='#*'
		)

        def get_template_configs(self):
                return [
                        dict(type="settings", custom_bindings=False)
                ]

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			irccat=dict(
				displayName="Irccat Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="jasiek",
				repo="OctoPrint-Irccat",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/jasiek/OctoPrint-Irccat/archive/{target_version}.zip"
			)
		)

        def on_event(self, event, payload):
                if event == octoprint.events.Events.PRINT_STARTED:
                        self.handle_print_started(payload)
                elif event == octoprint.events.Events.PRINT_DONE:
                        self.handle_print_done(payload)

        def handle_print_started(self, payload):
                metadata = self._file_manager.get_metadata(payload["origin"], payload["file"])
                printTime = metadata["analysis"]["estimatedPrintTime"]
                filamentLength = metadata["analysis"]["filament"]["tool0"]["length"]

                total_cost = self.print_cost(printTime) + self.filament_cost(filamentLength)
                self.send_to_irccat(self._hostname + ' started printing, estimated print time: ' + self.format_time(printTime) + ', estimated cost: ' + self.format_amount(total_cost))
                
        def handle_print_done(self, payload):
                metadata = self._file_manager.get_metadata(payload["origin"], payload["file"])
                printTime = metadata['statistics']['lastPrintTime']['_default']
                filamentLength = metadata["analysis"]["filament"]["tool0"]["length"]

                total_cost = self.print_cost(printTime) + self.filament_cost(filamentLength)
                self.send_to_irccat(self._hostname + ' finished printing, actual print time: ' + self.format_time(printTime) + ', actual cost: ' + self.format_amount(total_cost))

        def send_to_irccat(self, message):
                try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((self._settings.get(["host"]), self._settings.get(["port"])))
                        s.send(' '.join([self._settings.get(["channel_or_user"]), message]))
                        s.close()
                except (socket.error, socket.herror, socket.gaierror, socket.timeout) as e:
                        self._logger.error(repr(e))

        def _cost_per_hour(self):
                return self._settings.get(["cost_per_hour"]) or 0
        
        def print_cost(self, print_time):
                return float(self._cost_per_hour()) / 3600 * print_time

        def _cost_per_meter(self):
                return self._settings.get(["cost_per_meter"]) or 0
        
        def filament_cost(self, filament_length):
                return float(self._cost_per_meter()) / 1000 * filament_length

        def format_time(self, seconds):
                seconds = int(seconds)
                
                days = seconds / 86400
                hours = seconds / 3600 % 24
                minutes = seconds / 60 % 60
                seconds = seconds % 60

                output = []
                if days > 0:
                        output.append(days)
                        output.append('d')
                if hours > 0:
                        output.append(hours)
                        output.append('h')
                if minutes > 0:
                        output.append(minutes)
                        output.append('m')
                if seconds > 0:
                        output.append(seconds)
                        output.append('s')
                if output == [] and seconds == 0:
                        output.append('0s')
                return ''.join([str(x) for x in output])

        def format_amount(self, amount):
                return self._settings.get(["currency"]) + "%.2f" % amount



__plugin_name__ = "Irccat Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = IrccatPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

