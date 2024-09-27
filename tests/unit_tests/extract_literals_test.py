from kenkenpa.builder import extract_literals

def test_extract_literals_single_result():
    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]},
                    {"eq": ["10", "10"]},
                    {"eq": ["10", "10"]},
                ],
            },
            "result": "Result_Value"
        },
        {"default": "Default_Value"}
    ]
    assert extract_literals(conditions) == ["Result_Value", "Default_Value"]

def test_extract_literals_result_as_list():
    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]},
                    {"eq": ["10", "10"]},
                    {"eq": ["10", "10"]},
                ],
            },
            "result": ["Result_Value"]
        },
        {"default": ["Default_Value"]}
    ]
    assert extract_literals(conditions) == ["Result_Value", "Default_Value"]

def test_extract_literals_multiple_results():
    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]},
                ],
            },
            "result": "Result_Value_A"
        },
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]},
                ],
            },
            "result": "Result_Value_B"
        },
        {"default": "Default_Value"}
    ]
    assert extract_literals(conditions) == ["Result_Value_A", "Result_Value_B", "Default_Value"]

def test_extract_literals_mixed_results():
    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]},
                ],
            },
            "result": ["Result_Value_A_1", "Result_Value_A_2"]
        },
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]},
                ],
            },
            "result": "Result_Value_B"
        },
        {"default": "Default_Value"}
    ]
    assert extract_literals(conditions) == ["Result_Value_A_1", "Result_Value_A_2", "Result_Value_B", "Default_Value"]

def test_extract_literals_all_results_as_lists():
    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]},
                ],
            },
            "result": ["Result_Value_A_1", "Result_Value_A_2"]
        },
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]},
                ],
            },
            "result": ["Result_Value_B"]
        },
        {"default": "Default_Value"}
    ]
    assert extract_literals(conditions) == ["Result_Value_A_1", "Result_Value_A_2", "Result_Value_B", "Default_Value"]

def test_extract_literals_with_different_expressions():
    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "9"]},
                ],
            },
            "result": ["Result_Value_A_1", "Result_Value_A_2"]
        },
        {
            "expression": {
                "and": [
                    {"eq": ["10", "9"]},
                ],
            },
            "result": ["Result_Value_B"]
        },
        {"default": "Default_Value"}
    ]
    assert extract_literals(conditions) == ["Result_Value_A_1", "Result_Value_A_2", "Result_Value_B", "Default_Value"]

def test_extract_literals_with_multiple_defaults():
    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "9"]},
                ],
            },
            "result": ["Result_Value_A_1", "Result_Value_A_2"]
        },
        {
            "expression": {
                "and": [
                    {"eq": ["10", "9"]},
                ],
            },
            "result": ["Result_Value_B"]
        },
        {"default": ["Default_Value_1", "Default_Value_2"]}
    ]
    assert extract_literals(conditions) == ["Result_Value_A_1", "Result_Value_A_2", "Result_Value_B", "Default_Value_1", "Default_Value_2"]

def test_extract_literals_with_nested_expressions():
    conditions = [
        {
            "expression": {
                "and": [
                    {
                        "or": [
                            {
                                "and": [
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
    assert extract_literals(conditions) == ["Result_Value", "Default_Value"]