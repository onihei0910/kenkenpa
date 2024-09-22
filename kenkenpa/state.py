import types
from typing import Annotated, Dict
from typing_extensions import TypedDict

class StateBuilder():
    primitive_type_list = {
        "int":int,
        "float":float,
        "complex":complex,
        "str":str,
        "list":list,
        "tuple":tuple,
        "dict":dict,
        "set":set,
        "frozenset":frozenset,
        "bool":bool,
    }
    def __init__(self,types:Dict=None,reducers:Dict=None):
        if types:
            self.type_list = types
        else:
            self.type_list = {}
        
        if reducers:
            self.reducer_list = reducers
        else:
            self.reducer_list = {}

    def add_reducer(self,name:str,function):
        if name in self.reducer_list:
            raise ValueError(f"登録済みの関数: {name}")

        self.reducer_list[name] = function

    def add_type(self,name:str,type):
        if name in self.primitive_type_list:
            raise ValueError(f"予約済みの型: {name}")

        if name in self.type_list:
            raise ValueError(f"登録済みの型: {name}")

        self.type_list[name] = type

    def gen_state(self,params):
        annotations = {
            param['field_name']: (
                Annotated[
                    self._get_type(param['type']), 
                    self._get_reducer(param['reducer'])
                    ]
                if 'reducer' in param else
                self._get_type(param['type'])
            )
            for param in params
        }

        new_class = types.new_class(
            'State',
            (TypedDict,),
            exec_body=lambda ns: ns.update({
                '__annotations__': annotations,
            })
        )
        return new_class

    def _get_reducer(self,name:str):
        if name in self.reducer_list:
            return self.reducer_list[name]
        
        raise ValueError(f"登録されていない関数: {name}")
    
    def _get_type(self,name:str):
        if name in self.primitive_type_list:
            return self.primitive_type_list[name]

        if name in self.type_list:
            return self.type_list[name]

        raise ValueError(f"登録されていない型: {name}")
