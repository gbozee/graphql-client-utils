import os
import typing


class TuteriaApiException(Exception):
    pass


def get_value(val):
    if isinstance(val, str):
        return val
    return val.get("value")


def wrapQuotes(useQuote):
    if useQuote:
        return '"%s"'
    return "%s"


def build_key_value_pair(pair: typing.Dict[str, typing.Any], useQuote=True):
    return "(%s)" % ",".join(
        [("%s:" + wrapQuotes(useQuote)) % (key, value) for key, value in pair.items()]
    )


def resolve_graphql_field(field, value=None, useQuote=True):
    if isinstance(field, str):
        return "%s,\n" % field
    # assuming it is a dict
    has_name = bool(field.get("name"))
    base = ""
    if has_name:
        base = "%s{\n" % (field.get("name") or "")
    params = field.get("params") or {}
    if value:
        if field.get("key") and field.get("value"):
            params[field["key"]] = field["value"]
        # if field.get("keyPair"):
        #     key = ["%"]
    if params:
        variables = build_key_value_pair(params, useQuote)
        base = ("%s%s{\n") % (field["name"], variables)
    if field.get("fields"):
        for f in field["fields"]:
            _useQuote = False
            if isinstance(f, dict):
                _useQuote = bool(f.get("useQuote"))
            base += resolve_graphql_field(f, get_value(f), useQuote=_useQuote)
    if has_name:
        base += "}\n"
    return base


def construct_graphql_query(dict_object, queryDict=None, key="query"):
    """
    {"name": "wallet",
    "key": "username",
    "fields": ["owner", "upcoming_earnings",
    {'name': "transactions",
    'key': None,
    "fields": ["display", "type"] }]}
    :returns
        query{
            wallet(username:""){
                total_earned,
                total_withdrawn,
                total_credit_used_to_hire,
                total_used_to_hire,
                total_payed_to_tutor,
                upcoming_earnings,
                transactions{
                    total,
                    type,
                    display,
                    to_string,
                    amount
                }
            }
        }
    """
    query = key
    if queryDict:
        query = f'{key} {resolve_graphql_field(queryDict, queryDict.get("value"), useQuote=False)}'.replace(
            "{\n}\n", ""
        )
    useQuote = dict_object.pop("useQuote", True)
    base = resolve_graphql_field(
        dict_object, dict_object.get("value"), useQuote=useQuote
    )
    return "%s{\n%s}\n" % (query, base)


def get_field_value(value):
    if isinstance(value, str):
        return value
    return construct_graphql_dict(
        value["name"], value["fields"], key=value.get("key"), value=value.get("value")
    )


def construct_graphql_dict(name, fields, key=None, value=None):
    options = {"name": name, "key": key, "fields": [get_field_value(x) for x in fields]}
    if value:
        options.update(value=value)
    return options
