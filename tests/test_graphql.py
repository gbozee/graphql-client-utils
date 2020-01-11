import typing
from graphql_client_utils import GQLKlass


class Base(GQLKlass):
    id: str
    name: str


class Node(GQLKlass):
    node: Base


class Business(GQLKlass):
    edges: typing.List[Node]


class Query(GQLKlass):
    businesses: typing.List[Business]
    business: Node

    class Input:
        businesses = {"params": {"$id": "ID!"}, "useQuote": False}


class StringArray(GQLKlass):
    strings: typing.List[str]


def test_graphql_class_to_string():
    assert Node.as_gql_object() == {
        "fields": [{"fields": ["id", "name"], "name": "node"}]
    }
    assert Business.as_gql_object() == {
        "fields": [
            {"name": "edges", "fields": [{"fields": ["id", "name"], "name": "node"}]}
        ]
    }
    assert Query.as_gql_object() == {
        "fields": [
            {
                "name": "businesses",
                "params": {"$id": "ID!"},
                "useQuote": False,
                "fields": [
                    {
                        "name": "edges",
                        "fields": [{"fields": ["id", "name"], "name": "node"}],
                    }
                ],
            },
            {
                "name": "business",
                "fields": [{"fields": ["id", "name"], "name": "node"}],
            },
        ]
    }
    assert StringArray.as_gql_object() == {"fields": ["strings"]}


def test_graphql_string_generation():
    assert Node.as_gql() == "{\nnode{\nid,\nname,\n}\n}\n"
    assert Business.as_gql() == "{\nedges{\nnode{\nid,\nname,\n}\n}\n}\n"
    assert (
        Query.as_gql()
        == "{\nbusinesses($id:ID!){\nedges{\nnode{\nid,\nname,\n}\n}\n}\nbusiness{\nnode{\nid,\nname,\n}\n}\n}\n"
    )
    assert (
        Query.as_gql(key="query")
        == "query{\nbusinesses($id:ID!){\nedges{\nnode{\nid,\nname,\n}\n}\n}\nbusiness{\nnode{\nid,\nname,\n}\n}\n}\n"
    )
    assert (
        Query.as_gql(
            key="query", query_config={"name": "Business", "params": {"$id": "ID!"}}
        )
        == "query Business($id:ID!){\nbusinesses($id:ID!){\nedges{\nnode{\nid,\nname,\n}\n}\n}\nbusiness{\nnode{\nid,\nname,\n}\n}\n}\n"
    )


def test_process_grapqhl_result():
    result = {
        "data": {
            "businesses": {
                "edges": [
                    {
                        "node": {
                            "id": "QnVzaW5lc3M6M2RlYjMxNDktOGYzMi00ZjRlLWJiNTgtYjE2YmI2MjBiZDY2",
                            "name": "Personal",
                        }
                    },
                    {
                        "node": {
                            "id": "QnVzaW5lc3M6YzVlNWQxZWItNTVjMi00NjE4LTg4M2MtODMxNWU5OWNkZTM4",
                            "name": "Tuteria Limited",
                        }
                    },
                ]
            }
        }
    }
    instance = Query(**result["data"])
    assert len(instance.businesses.edges) == 2
    node = instance.businesses.edges[0]
    assert node.id == "QnVzaW5lc3M6M2RlYjMxNDktOGYzMi00ZjRlLWJiNTgtYjE2YmI2MjBiZDY2"
    assert node.name == "Personal"
    string_array = StringArray(strings=["a", "b", "c"])
    assert string_array.strings[0] == "a"

