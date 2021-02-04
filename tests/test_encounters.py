from src.player import Player,MissionStatus
from src.bitmap_capture import ImageCapture
import pytesseract

def is_any_news_in_journal(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.is_any_news_in_journal()

def get_accepted_mission_status(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_accepted_mission_status()

def get_mission_time(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_mission_time()

def get_mission_stage(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_mission_stage()

def test_journal_have_items():
    result = is_any_news_in_journal('tests/images/journal_have_items_test.png')
    assert result == True


def test_journal_dont_have_items():
    result = is_any_news_in_journal('tests/images/journal_dont_have_items_test.png')
    assert result == False

def test_get_accepted_mission_status_normal():
    result = get_accepted_mission_status('tests/images/test_get_accepted_mission_status_normal.png')
    assert result == MissionStatus.NORMAL

def test_get_accepted_mission_status_normal_2():
    result = get_accepted_mission_status('tests/images/test_get_accepted_mission_status_normal_2.png')
    assert result == MissionStatus.NORMAL


def test_get_accepted_mission_status_failed():
    result = get_accepted_mission_status('tests/images/test_get_accepted_mission_status_failed.png')
    assert result == MissionStatus.FAILED

def test_get_accepted_mission_status_unknown():
    result = get_accepted_mission_status('tests/images/test_get_accepted_mission_status_unknown.png')
    assert result == MissionStatus.UNKNOWN

def test_get_mission_time_1():
    result = get_mission_time('tests/images/test_get_mission_time_1.png')
    assert result == '02:48:08'

def test_get_mission_time_2():
    result = get_mission_time('tests/images/test_get_mission_time_2.png')
    assert result == '01:38:25'

def test_get_mission_time_3():
    result = get_mission_time('tests/images/test_get_mission_time_3.png')
    assert result == '01:22:27'

def test_get_mission_time_0():
    result = get_mission_time('tests/images/blank.png')
    assert result == None

def test_get_mission_stage_0():
    result = get_mission_stage('tests/images/test_get_mission_stage_0.png')
    assert result == 0

def test_get_mission_stage_1():
    result = get_mission_stage('tests/images/test_get_mission_stage_1.png')
    assert result == 1

def test_get_mission_stage_2():
    result = get_mission_stage('tests/images/test_get_mission_stage_2.png')
    assert result == 2