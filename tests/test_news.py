from src.player import Player
from src.bitmap_capture import ImageCapture
from datetime import timedelta

def get_news_with_chains(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_news_with_chains()
    
def get_refresh_cooldown(screenshotPath):
    ic = ImageCapture(screenshotPath)
    player = Player(ic, 0)
    return player.get_refresh_cooldown()

def test_news_0_chain():
    poses = get_news_with_chains('tests/images/test_news_0_chain.png')
    assert len(poses) == 0

def test_news_1_chain_1():
    poses = get_news_with_chains('tests/images/test_news_1_chain_1.png')
    assert len(poses) == 1

def test_news_1_chain_2():
    poses = get_news_with_chains('tests/images/test_news_1_chain_2.png')
    assert len(poses) == 1


def test_news_1_chain_3():
    poses = get_news_with_chains('tests/images/test_news_1_chain_3.png')
    assert len(poses) == 1

def test_news_2_chain_1():
    poses = get_news_with_chains('tests/images/test_news_2_chain_1.png')
    assert len(poses) == 2

def test_news_2_chain_2():
    poses = get_news_with_chains('tests/images/test_news_2_chain_2.png')
    assert len(poses) == 2

def test_news_3_chain_1():
    poses = get_news_with_chains('tests/images/test_news_3_chain_1.png')
    assert len(poses) == 3

def test_get_refresh_cooldown():
    res = get_refresh_cooldown('tests/images/test_get_refresh_cooldown.png')
    assert res == timedelta(minutes=23,seconds=21)

def test_get_refresh_cooldown_2():
    res = get_refresh_cooldown('tests/images/test_get_refresh_cooldown_2.png')
    assert res == None