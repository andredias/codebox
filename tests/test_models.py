from codebox.models import Response


def test_response():
    resp1 = Response(stdout='Hello World!', stderr='', exit_code=0)
    resp2 = Response(stdout='Hello World!', stderr='', exit_code=0, elapsed_time=0.1)
    assert resp1 == resp2
    assert resp1 != Response(stdout='Hello World!', stderr='', exit_code=1)
    assert '100ms' in str(resp2)
