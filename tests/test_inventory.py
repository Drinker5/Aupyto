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

def is_item_compact_mode(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.is_item_compact_mode()

def get_selected_item_move_to_button_position(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_selected_item_move_to_button_position()

def is_load_amount_window_showing(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.is_load_amount_window_showing()


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

def test_is_item_compact_mode():
    res = is_item_compact_mode('tests/images/test_is_item_compact_mode.png')
    assert res == True

def test_is_item_big_mode():
    res = is_item_compact_mode('tests/images/test_is_item_big_mode.png')
    assert res == False

def test_get_selected_item_move_to_button_position_1():
    res = get_selected_item_move_to_button_position('tests/images/test_get_selected_item_move_to_button_position_1.png')
    assert res != None

def test_get_selected_item_move_to_button_position_2():
    res = get_selected_item_move_to_button_position('tests/images/test_get_selected_item_move_to_button_position_2.png')
    assert res != None

def test_get_selected_item_move_to_button_position_3():
    res = get_selected_item_move_to_button_position('tests/images/test_get_selected_item_move_to_button_position_3.png')
    assert res == None

def test_is_load_amount_window_showing_1():
    res = is_load_amount_window_showing('tests/images/test_is_load_amount_window_showing_1.png')
    assert res == True

def test_is_load_amount_window_showing_2():
    res = is_load_amount_window_showing('tests/images/test_is_load_amount_window_showing_2.png')
    assert res == False

def test_find_ore_hold_menu_button_1():
    ic = ImageCapture('tests/images/test_find_ore_hold_menu_button_1.png')
    player = Player(ic, 0)
    assert player.find_ore_hold_menu_button() != None

def test_find_ore_hold_menu_button_2():
    ic = ImageCapture('tests/images/test_find_ore_hold_menu_button_2.png')
    player = Player(ic, 0)
    assert player.find_ore_hold_menu_button() == None

def test_find_mineral_hold_menu_button_1():
    ic = ImageCapture('tests/images/test_find_mineral_hold_menu_button_1.png')
    player = Player(ic, 0)
    assert player.find_mineral_hold_menu_button() != None

def test_find_mineral_hold_menu_button_2():
    ic = ImageCapture('tests/images/test_find_ore_hold_menu_button_2.png')
    player = Player(ic, 0)
    assert player.find_mineral_hold_menu_button() == None