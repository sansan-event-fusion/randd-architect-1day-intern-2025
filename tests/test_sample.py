from streamlit.testing.v1 import AppTest


def test_ui_components() -> None:
    at = AppTest.from_file("main.py")
    at.run()

    assert len(at.title.values) > 0
