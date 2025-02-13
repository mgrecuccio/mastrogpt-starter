import sys 
sys.path.append("packages/mgrecucci/reverse")
import reverse

def test_reverse():
    args = {"input": "ciao"}
    res = reverse.reverse(args)
    assert res["output"] == "oaic"
