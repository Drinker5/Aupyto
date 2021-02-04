from src.player import Player
from src.bitmap_capture import ImageCapture


def is_tip_dialog_showing(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.is_confirm_dialog_showing()

def is_npc_dialog_with_reply_showing(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.is_npc_dialog_with_reply_showing()

def is_docked(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.is_docked()

def is_docked_citadel(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.is_docked_citadel()

def is_inventory_visible(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.is_inventory_visible()

def get_inventory_load_percent(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_inventory_load_percent()


def test_is_tip_dialog_showing():
    res = is_tip_dialog_showing('tests/images/test_is_tip_dialog_showing.png')
    assert res == True

def test_is_tip_dialog_showing_not():
    res = is_tip_dialog_showing('tests/images/test_is_tip_dialog_showing_not.png')
    assert res == False

def test_is_npc_dialog_with_reply_showing():
    res = is_npc_dialog_with_reply_showing('tests/images/test_is_npc_dialog_with_reply_showing.png')
    assert res == True

def test_is_npc_dialog_with_reply_showing_not():
    res = is_npc_dialog_with_reply_showing('tests/images/test_is_npc_dialog_with_reply_showing_not.png')
    assert res == False

def test_is_docked():
    res = is_docked('tests/images/test_is_docked.png')
    assert res == True

def test_is_docked_not():
    res = is_docked('tests/images/test_is_docked_not.png')
    assert res == False

def test_is_docked_citadel():
    res = is_docked_citadel('tests/images/test_is_docked_citadel.png')
    assert res == True

def test_is_docked_citadel_not():
    res = is_docked_citadel('tests/images/test_is_docked_not.png')
    assert res == False

def test_is_inventory_visible():
    res = is_inventory_visible('tests/images/test_is_inventory_visible.png')
    assert res == True

def test_is_inventory_visible_not():
    res = is_inventory_visible('tests/images/test_is_inventory_visible_not.png')
    assert res == False

def test_get_inventory_load_percent_1():
    res = get_inventory_load_percent('tests/images/test_get_inventory_load_percent_1.png')
    assert res >= 0.04 and res <= 0.06

def test_get_inventory_load_percent_2():
    res = get_inventory_load_percent('tests/images/test_get_inventory_load_percent_2.png')
    assert res == 1.0

def test_get_inventory_load_percent_3():
    res = get_inventory_load_percent('tests/images/test_get_inventory_load_percent_3.png')
    assert res == 0.0