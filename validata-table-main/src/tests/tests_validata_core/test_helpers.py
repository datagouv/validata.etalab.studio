from validata_core.helpers import to_lower


def test_to_lower():
    test_cases = [{"uppers": [''], "expected": ['']},
        {'uppers': ['A'], 'expected': ['a']},
        {'uppers': ['a'], 'expected': ['a']},
        {'uppers': ['A', ''], 'expected': ['a', '']},
        {'uppers': ['a', ''], 'expected': ['a', '']},
        {'uppers': ['', ''], 'expected': ['', '']},
        {'uppers': ['A', 'A'], 'expected': ['a', 'a']},
        {'uppers': ['a', 'A'], 'expected': ['a', 'a']},
        {'uppers': ['', 'A'], 'expected': ['', 'a']},
        {'uppers': ['A', 'a'], 'expected': ['a', 'a']},
        {'uppers': ['a', 'a'], 'expected': ['a', 'a']},
        {'uppers': ['', 'a'], 'expected': ['', 'a']},
        {'uppers': ["ABC", ''], 'expected': ["abc", '']},
        {'uppers': ["aBc", ''], 'expected': ["abc", '']},
        {'uppers': ["abc", ''], 'expected': ["abc", '']},
        {'uppers': ['ABC', "ABC"], 'expected': ["abc", "abc"]},
        {'uppers': ['aBc', 'aBc'], 'expected': ["abc", 'abc']},
        {'uppers': ['abc', 'abc'], 'expected': ["abc", 'abc']},
    ]
    for test_case in test_cases:
        assert to_lower(test_case["uppers"]) == test_case["expected"]
