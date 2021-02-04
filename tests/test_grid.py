from src.player import Player
from src.bitmap_capture import ImageCapture
from datetime import timedelta

def get_warp_command_pos(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_warp_command_pos()

def get_lock_command_pos(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_lock_command_pos()

def get_approach_command_pos(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_approach_command_pos()

def get_locked_target_approach_command_pos(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_locked_target_approach_command_pos()

def get_local(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_local()
    
def test_get_warp_command_pos():
    pos = get_warp_command_pos('tests/images/test_get_warp_command_pos.png')
    assert pos != None

def test_get_warp_command_pos_2():
    pos = get_warp_command_pos('tests/images/test_get_warp_command_pos_2.png')
    assert pos != None


def test_get_lock_command_pos():
    pos = get_lock_command_pos('tests/images/test_get_lock_command_pos.png')
    assert pos != None

def test_get_lock_command_pos_2():
    pos = get_lock_command_pos('tests/images/test_get_lock_command_pos_2.png')
    assert pos != None


def test_get_approach_command_pos():
    pos = get_approach_command_pos('tests/images/test_get_approach_command_pos.png')
    assert pos != None

def test_get_approach_command_pos_2():
    pos = get_approach_command_pos('tests/images/test_get_approach_command_pos_2.png')
    assert pos != None


def test_get_locked_target_approach_command_pos():
    pos = get_locked_target_approach_command_pos('tests/images/test_get_locked_target_approach_command_pos.png')
    assert pos != None

def test_get_locked_target_approach_command_pos_2():
    pos = get_locked_target_approach_command_pos('tests/images/test_get_locked_target_approach_command_pos_2.png')
    assert pos != None


def test_local_1():
    local = get_local('tests/images/test_local_1.png')
    assert local.greens == 1
    assert local.alies == 3
    assert local.neutrals == 1
    assert local.is_friendly == False

def test_local_2():
    local = get_local('tests/images/test_local_2.png')
    assert local.greens == 1
    assert local.alies == 4
    assert local.is_friendly == True

def test_local_3():
    local = get_local('tests/images/test_local_3.png')
    assert local.greens == 1
    assert local.alies == 4
    assert local.is_friendly == True

def test_local_4():
    local = get_local('tests/images/test_local_4.png')
    assert local.alies == 5
    assert local.is_friendly == True

def test_local_5():
    local = get_local('tests/images/test_local_5.png')
    assert local.alies == 3
    assert local.pluses == 1
    assert local.is_friendly == False

def test_local_6():
    local = get_local('tests/images/test_local_6.png')
    assert local.alies == 2
    assert local.pluses == 2
    assert local.greens == 1
    assert local.is_friendly == True

def test_local_7():
    local = get_local('tests/images/test_local_7.png')
    assert local.alies == 4
    assert local.minuses == 1
    assert local.is_friendly == False