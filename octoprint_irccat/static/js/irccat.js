/*
 * View model for OctoPrint-Irccat
 *
 * Author: Jan Szumiec
 * License: MIT
 */
$(function() {
    function IrccatViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        IrccatViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        [ /* "loginStateViewModel", "settingsViewModel" */ ],

        // e.g. #settings_plugin_irccat, #tab_plugin_irccat, ...
        [ /* ... */ ]
    ]);
});
