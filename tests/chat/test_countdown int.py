import os, requests as req

def test_countdown_int():
    url = os.environ.get("OPSDEV_HOST") + "/api/my/chat/countdown"
    out = req.get(url).json().get("output")
    assert out.startswith("Input a number > 0 to countdown")

    args = {"input": "3"}
    req.post(url,json=args).json();
    
    out = req.get(url).json().get("output")
    assert out.find("Go!")