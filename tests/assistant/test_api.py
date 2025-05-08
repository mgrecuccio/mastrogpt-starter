import sys
import streamock 
sys.path.append("packages/assistant/api")
import chat

def test_api():
    args = streamock.args()
    mock = streamock.start(args)

    ch = chat.Chat(args)
    msg = "user:What is the capital of Italy"
    ch.add(msg)
    ch.complete()

    stream = streamock.stop(mock).decode("utf-8")
    assert stream.find("Rom") != -1

    assert len(ch.messages) == 3
    assert ch.messages[0]['role'] == 'system'
    assert ch.messages[1]['role'] == 'user'
    assert ch.messages[2]['role'] == 'assistant'
    
