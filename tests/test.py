# coding=utf-8
import sys
import os
sys.path.append(os.path.abspath('.'))

import pytest
import pytest_mock

import socket
import octoprint.events
import octoprint_irccat

@pytest.fixture
def subject():
    return octoprint_irccat.IrccatPlugin()

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
    
def test_print_cost():
    assert subject().print_cost(3600) == 1.50
    assert subject().print_cost(7200) == 3.00

def test_filament_cost():
    assert subject().filament_cost(1000) == 0.2
    assert subject().filament_cost(2000) == 0.4
