from src.utils import text_utils

def test_window_slide_basic():
    text = "hello world Spring yolo whatzup I'm a coder that you trust to power"
    slides = text_utils.window_slide_split(text=text, step=3, chunk_size=5)
    assert len(slides) == 4
    assert slides[0] == "hello world Spring yolo whatzup"
    assert slides[-1] == "you trust to power"

def test_window_slide_equal():
    text = "hello world Spring yolo whatzup I'm a coder that you"
    slides = text_utils.window_slide_split(text=text, step=5, chunk_size=5)
    assert len(slides) == 2
    assert slides[0] == "hello world Spring yolo whatzup"
    assert slides[-1] == "I'm a coder that you"