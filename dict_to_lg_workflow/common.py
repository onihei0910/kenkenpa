from langgraph.graph import START,END

def convert_key(point:str):
    if point == 'START':
        return START
    if point == 'END':
        return END
    return point