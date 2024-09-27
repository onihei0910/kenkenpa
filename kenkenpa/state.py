"""
This module provides a StateBuilder class for
dynamically creating state classes with specified types and reducers.
"""
import types
from typing import Annotated, Dict
from typing_extensions import TypedDict

class StateBuilder():
    """
    StateBuilder is a class that helps in creating dynamic state classes with
    specified types and reducers.

    Attributes:
        primitive_type_list (Dict[str, type]): A dictionary of primitive types.
        type_list (Dict[str, type]): A dictionary of user-defined types.
        reducer_list (Dict[str, callable]): A dictionary of reducers.
    """
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
    def __init__(self,type_map:Dict=None,reducers:Dict=None):
        """
        Initializes the StateBuilder with optional user-defined types and reducers.

        Args:
            type_map (Dict, optional): A dictionary of user-defined types.
                Defaults to an empty dictionary.
            reducers (Dict, optional): A dictionary of reducers.
                Defaults to an empty dictionary.
        """
        if type_map:
            self.type_list = type_map
        else:
            self.type_list = {}

        if reducers:
            self.reducer_list = reducers
        else:
            self.reducer_list = {}

    def add_reducer(self,name:str,function):
        """
        Adds a reducer function to the reducer list.

        Args:
            name (str): The name of the reducer function.
            function (callable): The reducer function to be added.

        Raises:
            ValueError: If the reducer function name is already registered.
        """
        if name in self.reducer_list:
            raise ValueError(f"Registered function: {name}")

        self.reducer_list[name] = function

    def add_type(self,name:str,type_):
        """
        Adds a user-defined type to the type list.

        Args:
            name (str): The name of the type.
            type_ (type): The type to be added.

        Raises:
            ValueError: If the type name is reserved or already registered.
        """
        if name in self.primitive_type_list:
            raise ValueError(f"Reserved type: {name}")

        if name in self.type_list:
            raise ValueError(f"Registered type: {name}")

        self.type_list[name] = type_

    def gen_state(self,params):
        """
        Generates a new state class based on the provided parameters.

        Args:
            params (List[Dict[str, Union[str, Optional[str]]]]):
                A list of dictionaries containing field names, types, and optional reducers.

        Returns:
            Type[TypedDict]: A new state class with the specified annotations.
        """
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
        """
        Retrieves a reducer function by name.

        Args:
            name (str): The name of the reducer function.

        Returns:
            callable: The reducer function.

        Raises:
            ValueError: If the reducer function name is not registered.
        """
        if name in self.reducer_list:
            return self.reducer_list[name]

        raise ValueError(f"Unregistered function: {name}")

    def _get_type(self,name:str):
        """
        Retrieves a type by name.

        Args:
            name (str): The name of the type.

        Returns:
            type: The type.

        Raises:
            ValueError: If the type name is not registered.
        """
        if name in self.primitive_type_list:
            return self.primitive_type_list[name]

        if name in self.type_list:
            return self.type_list[name]

        raise ValueError(f"Unregistered type: {name}")
