from langgraph.graph import START,END

def convert_key(key: str):
    if key == 'START':
        return START
    if key == 'END':
        return END
    return key
