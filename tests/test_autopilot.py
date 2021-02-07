from src.player import Player, AutopilotStatus
from src.bitmap_capture import ImageCapture


def get_autopilot_status(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_autopilot_status()


def test_autopilot_disabled():
    status = get_autopilot_status('tests/images/test_autopilot_disabled.png')
    assert status == AutopilotStatus.DISABLED

def test_autopilot_disabled_2():
    status = get_autopilot_status('tests/images/test_autopilot_disabled_2.png')
    assert status == AutopilotStatus.DISABLED

def test_autopilot_unknown():
    status = get_autopilot_status('tests/images/blank.png')
    assert status == AutopilotStatus.UNKNOWN


def test_autopilot_enabled():
    status = get_autopilot_status('tests/images/test_autopilot_enabled.png')
    assert status == AutopilotStatus.ENABLED

def test_autopilot_enabled_2():
    status = get_autopilot_status('tests/images/test_autopilot_enabled_2.png')
    assert status == AutopilotStatus.ENABLED

def test_autopilot_stopped():
    status = get_autopilot_status('tests/images/test_autopilot_stopped.png')
    assert status == AutopilotStatus.STOPPED

def test_autopilot_stopped_2():
    status = get_autopilot_status('tests/images/test_autopilot_stopped_2.png')
    assert status == AutopilotStatus.STOPPED
