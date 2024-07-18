from streamlit.testing.v1 import AppTest

def test_session_state_equals_false():
    """Initial session state should equal false when app starts"""
    at = AppTest.from_file("myApp.py").run()
    assert at.radio(key=0) == False