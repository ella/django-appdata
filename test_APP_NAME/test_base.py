from nose import tools

def test_failing():
    tools.assert_equals(1*1, 2)

def test_passing():
    tools.assert_equals(1+1, 2)

