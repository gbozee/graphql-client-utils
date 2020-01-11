import typing
from . import utils


def get_class_fields(klass, typed=False) -> typing.Dict[str, typing.Any]:
    if typed:
        result = {}
        for key, value in klass.__annotations__.items():
            if hasattr(value, "__args__"):
                result[key] = value.__args__[0]
            else:
                result[key] = value
        return result
    return {
        key: value
        for key, value in klass.__dict__.items()
        if not callable(value) and not key.startswith("__")
    }


primitive_classes = [str, int, float, bool]


def is_instance_of_primitive_class(value: typing.Union[typing.Any]) -> bool:
    func = lambda klass: isinstance(value, klass)
    return any([func(x) for x in primitive_classes])


def create_single_value(x: typing.Any, value: typing.Callable) -> typing.Any:
    if isinstance(x, dict):
        return value(**x)
    return x


class GQLKlass(object):
    def __init__(self, **kwargs):
        class_fields = get_class_fields(self.__class__, typed=True)
        for key, value in class_fields.items():
            kwargs_value: typing.Optional[typing.Dict[str, typing.Any]] = kwargs.get(
                key
            )
            if kwargs_value:

                if isinstance(kwargs_value, list):
                    setattr(
                        self, key, [create_single_value(x, value) for x in kwargs_value]
                    )
                elif value in primitive_classes:
                    setattr(self, key, kwargs_value)
                else:
                    if all(
                        [
                            is_instance_of_primitive_class(x)
                            for x in kwargs_value.values()
                        ]
                    ):
                        for k, j in kwargs_value.items():
                            setattr(self, k, j)
                    else:
                        setattr(self, key, create_single_value(kwargs_value, value))

            else:
                setattr(self, key, None)

    @classmethod
    def _parse_fields(cls) -> typing.List[typing.Any]:
        annotations = cls.__annotations__
        fields: typing.List[typing.Any] = []
        for key, value in annotations.items():
            if value in primitive_classes:
                fields.append(key)
            else:
                if issubclass(value, GQLKlass):
                    fields.append({"fields": value._parse_fields(), "name": key})

                elif hasattr(value, "__args__"):
                    if all([issubclass(x, GQLKlass) for x in value.__args__]):
                        fields.append(
                            {"fields": value.__args__[0]._parse_fields(), "name": key}
                        )
                    if all([(x in primitive_classes) for x in value.__args__]):
                        fields.append(key)

        return fields

    @classmethod
    def get_input_class_kwargs(cls):
        kwargs = {}
        if hasattr(cls, "Input"):
            if isinstance(cls.Input, type):
                kwargs = get_class_fields(cls.Input)
        return kwargs

    @classmethod
    def as_gql_object(cls) -> typing.Dict[str, typing.Any]:
        kwargs = cls.get_input_class_kwargs()
        fields = []
        for field in cls._parse_fields():
            if isinstance(field, dict):
                if field["name"] in kwargs:
                    fields.append({**field, **kwargs[field["name"]]})
                else:
                    fields.append(field)
            else:
                fields.append(field)
        return {"fields": fields}

    @classmethod
    def as_gql(cls, key="", query_config: typing.Dict = None) -> str:
        _obj = cls.as_gql_object()
        return utils.construct_graphql_query(_obj, queryDict=query_config, key=key)

