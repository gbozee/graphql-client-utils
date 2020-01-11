from graphql_client_utils import utils


def test_resolve_graphql_field_works():
    value = "age"
    result = utils.resolve_graphql_field(value)
    assert result == "age,\n"
    value = {"name": "age", "fields": ["name", "school"]}
    result = utils.resolve_graphql_field(value)
    assert result == "age{\nname,\nschool,\n}\n"


def test_construct_graphql_query_works():
    w = "biola"
    value = {
        "name": "wallet",
        "key": "username",
        "value": "%s" % w,
        "fields": [
            "owner",
            "upcoming_earnings",
            {"name": "transactions", "key": None, "fields": ["display", "type"]},
        ],
    }
    result = utils.construct_graphql_query(value)
    assert result == (
        'query{\nwallet(username:"biola")'
        "{\nowner,\nupcoming_earnings,\ntransactions{\ndisplay,\ntype,\n}\n}\n}\n"
    )
    value = {
        "name": "Business",
        "key": "$id",
        "value": "ID!",
        "fields": ["name", "age"],
        "useQuote": False,
    }
    result = utils.construct_graphql_query(
        value, {"name": "Business", "key": "$id", "value": "ID!", "fields": []}
    )
    assert result == (
        "query Business($id:ID!){\nBusiness($id:ID!){\nname,\nage,\n}\n}\n"
    )
    assert (
        utils.construct_graphql_query(
            {
                "name": "Business",
                "params": {"$id": "ID!", "$age": "String!"},
                "useQuote": False,
            }
        )
        == "query{\nBusiness($id:ID!,$age:String!){\n}\n}\n"
    )


def test_construct_graphql_dict_works():
    result = utils.construct_graphql_dict(
        "wallet",
        [
            "total_earned",
            "total_withdrawn",
            {"name": "transaction", "fields": ["total", "type"]},
        ],
    )
    assert result == {
        "name": "wallet",
        "key": None,
        "fields": [
            "total_earned",
            "total_withdrawn",
            {"name": "transaction", "key": None, "fields": ["total", "type"]},
        ],
    }


def test_get_field_value_works_on_dict():
    transactions = {"name": "transactions", "fields": ["total", "type"]}
    data = {
        "name": "wallet",
        "key": "username",
        "value": "biola",
        "fields": ["total_earned", "total_withdrawn", transactions],
    }
    result = utils.get_field_value(data)
    assert result == {
        "name": "wallet",
        "key": "username",
        "value": "biola",
        "fields": [
            "total_earned",
            "total_withdrawn",
            {"name": "transactions", "key": None, "fields": ["total", "type"]},
        ],
    }

