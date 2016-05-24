# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.events
import socket

class IrccatPlugin(octoprint.plugin.SettingsPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.EventHandlerPlugin):

	def get_settings_defaults(self):
		return dict(
			host="127.0.0.1",
                        port=12345,
		)

        def get_template_vars(self):
                return dict(
                        host=self._settings.get(["host"]),
                        port=self._settings.get(["port"]),
                )
                
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
                filamentLength = metadata["analysis"]["tool0"]["length"]

                printCost = 1.50 * printTime / 60
                filamentCost = filamentLength * 0.20

                self.send_to_irccat(hostname() + ' started printing, estimated print time: ' + format_time(printTime) + ', estimated cost: ' + str(printCost + filamentCost)
                
        def handle_print_done(self, payload):
                metadata = self._file_manager.get_metadata(payload["origin"], payload["file"])
                print metadata

        def hostname(self):
                if not self._hostname:
                        self._hostname = socket.gethostname()
                return self._hostname

        def send_to_irccat(self, message):
                print message
                return
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self._settings.get(["host"]), self._settings.get(["port"])))
                s.send("#london-hack-space-dev ", message)
                s.close()

__plugin_name__ = "Irccat Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = IrccatPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

