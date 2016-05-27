# coding=utf-8
import sys
import os
sys.path.append(os.path.abspath('.'))

import pytest
import pytest_mock

import socket
import octoprint.events
import octoprint.settings
import octoprint_irccat

# Hack needed to instantiate Settings on a Mac
octoprint.settings._default_basedir = lambda _ : '/tmp'

@pytest.fixture
def subject():
    instance = octoprint_irccat.IrccatPlugin()
    instance._settings = octoprint.settings.Settings()
    instance.initialize()
    return instance

def test_default_settings():
    expected_settings = dict(
        host="127.0.0.1",
        port=12345,
        cost_per_hour=1.50,
        cost_per_meter=0.2,
        currency='£'
    )
    assert expected_settings == subject().get_settings_defaults()

def test_on_event(mocker):
    plugin = subject()
    mocker.patch.object(plugin, 'handle_print_started')
    plugin.on_event(octoprint.events.Events.PRINT_STARTED, {})
    plugin.handle_print_started.assert_called_with({})

    mocker.patch.object(plugin, 'handle_print_done')
    plugin.on_event(octoprint.events.Events.PRINT_DONE, {})
    plugin.handle_print_done.assert_called_with({})

def test_hostname():
    assert socket.gethostname() == subject().hostname()
    
def test_print_cost(mocker):
    plugin = subject()
    mocker.patch.object(plugin, '_cost_per_hour', new_callable=lambda : lambda : 1.50)
    assert plugin.print_cost(3600) == 1.50
    assert plugin.print_cost(7200) == 3.00

def test_filament_cost(mocker):
    plugin = subject()
    mocker.patch.object(plugin, '_cost_per_meter', new_callable=lambda : lambda : 0.2)
    assert plugin.filament_cost(1000) == 0.2
    assert plugin.filament_cost(2000) == 0.4

def test_format_time():
    plugin = subject()
    assert plugin.format_time(0) == '0s'
    assert plugin.format_time(59) == '59s'
    assert plugin.format_time(60) == '1m'
    assert plugin.format_time(61) == '1m1s'
    assert plugin.format_time(3599) == '59m59s'
    assert plugin.format_time(3600) == '1h'
    assert plugin.format_time(3601) == '1h1s'
    assert plugin.format_time(24 * 3600 - 1) == '23h59m59s'
    assert plugin.format_time(24 * 3600) == '1d'
    assert plugin.format_time(24 * 3600 + 1) == '1d1s'

def test_sending_fails(mocker):
    plugin = subject()
    mocker.patch.object(plugin._logger, 'error')

    for exc in [socket.error, socket.herror, socket.gaierror, socket.timeout]:
        e = exc(1, "something bad happened")
        def raiser(_, __):
            raise e
        mocker.patch('socket.socket', new_callable=lambda : raiser)
        plugin.send_to_irccat('irrelevant')
        plugin._logger.error.assert_called_with(repr(e))
