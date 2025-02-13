import os, requests as req
def test_reverse():
    url = os.environ.get("OPSDEV_HOST") + "/api/my/mgrecucci/reverse"
    res = req.get(url).json()
    res = req.post(url, {"input": "ciao"}).json()
    assert res.get("output") == "oaic"
