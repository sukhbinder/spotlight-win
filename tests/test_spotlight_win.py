from spotlight_win import cli
from spotlight_win.spotlight import safe_eval
import pytest
from unittest.mock import patch
from spotlight_win.spotlight import ShutdownPlugin, LLMPlugin


def test_safe_eval():
    assert safe_eval("1+1") == 2
    assert safe_eval("2*3") == 6
    assert safe_eval("10/2") == 5.0
    assert safe_eval("5-3") == 2
    assert safe_eval("(1+2)*3") == 9
    assert safe_eval("-5") == -5
    assert safe_eval("2**3") == 8
    assert safe_eval("10%3") == 1

    # Test unsupported operations
    with pytest.raises(ValueError):
        safe_eval("1 and 2")
    with pytest.raises(ValueError):
        safe_eval("1+a")
    with pytest.raises(SyntaxError):
        safe_eval("import os")


def test_shutdown_plugin_match():
    plugin = ShutdownPlugin()
    assert plugin.match("shutdown") == (100, "Shutdown computer")
    assert plugin.match("Shutdown") == (100, "Shutdown computer")
    assert plugin.match("shut down") is None
    assert plugin.match("something else") is None

@patch("os.system")
def test_shutdown_plugin_activate(mock_os_system):
    plugin = ShutdownPlugin()
    plugin.activate("shutdown")
    mock_os_system.assert_called_once_with("shutdown /s /t 1")


from spotlight_win.spotlight import RestartPlugin

def test_restart_plugin_match():
    plugin = RestartPlugin()
    assert plugin.match("restart") == (100, "Restart computer")
    assert plugin.match("Restart") == (100, "Restart computer")
    assert plugin.match("re start") is None
    assert plugin.match("something else") is None

@patch("os.system")
def test_restart_plugin_activate(mock_os_system):
    plugin = RestartPlugin()
    plugin.activate("restart")
    mock_os_system.assert_called_once_with("shutdown /r /t 1")


from spotlight_win.spotlight import OpenSettingsPlugin

def test_open_settings_plugin_match():
    plugin = OpenSettingsPlugin()
    assert plugin.match("settings") == (100, "Open Settings")
    assert plugin.match("Settings") == (100, "Open Settings")
    assert plugin.match("setings") is None
    assert plugin.match("something else") is None

@patch("os.system")
def test_open_settings_plugin_activate(mock_os_system):
    plugin = OpenSettingsPlugin()
    plugin.activate("settings")
    mock_os_system.assert_called_once_with("start ms-settings:")


from spotlight_win.spotlight import LLMPlugin

def test_llm_plugin_match():
    plugin = LLMPlugin()
    assert plugin.match("llm what is the capital of france") == (100, "Ask LLM: what is the capital of france")
    assert plugin.match("LLM tell me a joke") == (100, "Ask LLM: tell me a joke")
    assert plugin.match("something else") is None
    assert plugin.match("llm") is None

@patch("subprocess.run")
def test_llm_plugin_activate(mock_subprocess_run):
    plugin = LLMPlugin()
    mock_result = mock_subprocess_run.return_value
    mock_result.stdout = "Paris"
    mock_result.stderr = ""
    mock_result.strip.return_value = "Paris" # Mock the strip method as well

    result = plugin.activate("llm what is the capital of france")
    
    # Check if subprocess.run was called with the correct arguments
    mock_subprocess_run.assert_called_once()
    args, kwargs = mock_subprocess_run.call_args
    assert args[0][0].endswith("q.bat") # Check if q.bat is in the command
    assert args[0][1] == "what is the capital of france"
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["shell"] is True
    
    assert result == "Paris"

@patch("subprocess.run")
def test_llm_plugin_activate_error(mock_subprocess_run):
    plugin = LLMPlugin()
    mock_subprocess_run.side_effect = Exception("Test error")

    result = plugin.activate("llm something bad happened")
    assert result == "Error: Test error"

@patch("subprocess.run")
def test_llm_plugin_activate_no_response(mock_subprocess_run):
    plugin = LLMPlugin()
    mock_result = mock_subprocess_run.return_value
    mock_result.stdout = ""
    mock_result.stderr = ""
    mock_result.strip.return_value = "" # Mock the strip method as well

    result = plugin.activate("llm no response expected")
    assert result == "No response."
