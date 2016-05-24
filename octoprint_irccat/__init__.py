# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.events

class IrccatPlugin(octoprint.plugin.SettingsPlugin,
                   octoprint.plugin.TemplatePlugin):

	def get_settings_defaults(self):
		return dict(
			host="127.0.0.1",
                        port=12345,
                        events=["PrintDone"]
		)

        def get_template_vars(self):
                return dict(
                        host=self._settings.get(["host"]),
                        port=self._settings.get(["port"]),
                        selectedEvents=self._settings.get(["events"]),
                        possibleEvents=octoprint.events.all_events()
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

__plugin_name__ = "Irccat Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = IrccatPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

