import pandas as pd

from utils.preprocessing import clean_text, detect_language, normalize_arabic, remove_duplicates


def test_clean_removes_links_and_symbols():
    assert clean_text("Hello!! https://x.com/a <b>World</b>") == "Hello World"


def test_clean_keeps_arabic():
    assert "فلسطين" in clean_text("أخبار فلسطين!!!")


def test_detect_language():
    assert detect_language("Gaza ceasefire talks") == "en"
    assert detect_language("محادثات وقف إطلاق النار") == "ar"


def test_normalize_arabic():
    assert normalize_arabic("أحمد") == normalize_arabic("احمد")


def test_remove_duplicates():
    df = pd.DataFrame({
        "url": ["a", "b", "c"],
        "title": ["Israel strikes Gaza overnight", "Israel strikes Gaza overnight!", "Peace talks resume"],
    })
    assert len(remove_duplicates(df)) == 2
