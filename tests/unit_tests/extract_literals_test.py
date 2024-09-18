from kenkenpa.builder import extract_literals


def test_extract_literals():
    conditions = [
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "10"]},
                        {"eq": ["10", "10"]},
                        {"eq": ["10", "10"]},
                    ],
                },
                "result": "Result_Value"
            },
            {"default": "Default_Value"} 
        ]
    
    assert extract_literals(conditions) == ["Result_Value","Default_Value"]

    conditions = [
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "10"]},
                        {"eq": ["10", "10"]},
                        {"eq": ["10", "10"]},
                    ],
                },
                "result": ["Result_Value"]
            },
            {"default": ["Default_Value"]} 
        ]
    
    assert extract_literals(conditions) == ["Result_Value","Default_Value"]

    conditions = [
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "10"]},
                    ],
                },
                "result": "Result_Value_A"
            },
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "10"]},
                    ],
                },
                "result": "Result_Value_B"
            },
            {"default": "Default_Value"} 
        ]
    
    assert extract_literals(conditions) == ["Result_Value_A","Result_Value_B","Default_Value"]

    conditions = [
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "10"]},
                    ],
                },
                "result": ["Result_Value_A_1","Result_Value_A_2"]
            },
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "10"]},
                    ],
                },
                "result": "Result_Value_B"
            },
            {"default": "Default_Value"} 
        ]
    
    assert extract_literals(conditions) == ["Result_Value_A_1","Result_Value_A_2","Result_Value_B","Default_Value"]

    conditions = [
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "10"]},
                    ],
                },
                "result": ["Result_Value_A_1","Result_Value_A_2"]
            },
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "10"]},
                    ],
                },
                "result": ["Result_Value_B"] # arry
            },
            {"default": "Default_Value"} 
        ]
    
    assert extract_literals(conditions) == ["Result_Value_A_1","Result_Value_A_2","Result_Value_B","Default_Value"]

    conditions = [
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "9"]},
                    ],
                },
                "result": ["Result_Value_A_1","Result_Value_A_2"]
            },
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "9"]},
                    ],
                },
                "result": ["Result_Value_B"] # arry
            },
            {"default": "Default_Value"} 
        ]
    
    assert extract_literals(conditions) == ["Result_Value_A_1","Result_Value_A_2","Result_Value_B","Default_Value"]

    conditions = [
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "9"]},
                    ],
                },
                "result": ["Result_Value_A_1","Result_Value_A_2"]
            },
            {
                "expression": {
                    "and":[
                        {"eq": ["10", "9"]},
                    ],
                },
                "result": ["Result_Value_B"] # arry
            },
            {"default": ["Default_Value_1","Default_Value_2"]} 
        ]
    
    assert extract_literals(conditions) == ["Result_Value_A_1","Result_Value_A_2","Result_Value_B","Default_Value_1","Default_Value_2"]


    conditions = [
            {
                "expression": {
                    "and":[
                        {
                            "or":[
                                {
                                    "and":[
                                        {"eq": ["10", "10"]},
                                        ]
                                },
                                {"eq": ["10", "10"]}
                                ]
                        },
                        {"eq": ["10", "10"]},
                    ],
                },
                "result": "Result_Value"
            },
            {"default": "Default_Value"} 
        ]
    
    assert extract_literals(conditions) == ["Result_Value","Default_Value"]

