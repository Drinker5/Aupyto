from src.player import Player
from src.bitmap_capture import ImageCapture


def is_select_all_active(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.is_select_all_active()

def get_additional_cargo_position(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_additional_cargo_position()

def get_delivery_hold_additional_cargo_position(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_delivery_hold_additional_cargo_position()

def test_is_select_all_active():
    res = is_select_all_active('tests/images/test_is_select_all_active.png')
    assert res == True

def test_is_select_all_active_not():
    res = is_select_all_active('tests/images/test_is_select_all_active_not.png')
    assert res == False

def test_get_additional_cargo_position():
    pos = get_additional_cargo_position('tests/images/test_get_additional_cargo_position.png')
    assert pos != None

def test_get_additional_cargo_position_2():
    pos = get_additional_cargo_position('tests/images/test_get_additional_cargo_position_2.png')
    assert pos != None

def test_get_additional_cargo_position_3():
    pos = get_additional_cargo_position('tests/images/test_get_additional_cargo_position_2.png')
    assert pos != None

def test_get_additional_cargo_position_none():
    pos = get_additional_cargo_position('tests/images/test_get_additional_cargo_position_none.png')
    assert pos == None

def test_get_delivery_hold_additional_cargo_position():
    pos = get_delivery_hold_additional_cargo_position('tests/images/test_get_delivery_hold_additional_cargo_position.png')
    assert pos != None
def test_get_delivery_hold_additional_cargo_position_2():
    pos = get_delivery_hold_additional_cargo_position('tests/images/test_get_delivery_hold_additional_cargo_position_2.png')
    assert pos != None
def test_get_delivery_hold_additional_cargo_position_none():
    pos = get_delivery_hold_additional_cargo_position('tests/images/test_get_delivery_hold_additional_cargo_position_none.png')
    assert pos == None