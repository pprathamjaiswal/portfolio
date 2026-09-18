import os

from portfolio.env import env_bool, env_int, env_list, env_str


def test_env_readers_parse_values():
    os.environ["PORTFOLIO_TEST_STR"] = "  hello  "
    os.environ["PORTFOLIO_TEST_BOOL"] = "YeS"
    os.environ["PORTFOLIO_TEST_INT"] = "42"
    os.environ["PORTFOLIO_TEST_LIST"] = "a, b ,, c"

    assert env_str("PORTFOLIO_TEST_STR") == "hello"
    assert env_bool("PORTFOLIO_TEST_BOOL") is True
    assert env_int("PORTFOLIO_TEST_INT", 0) == 42
    assert env_list("PORTFOLIO_TEST_LIST") == ["a", "b", "c"]
