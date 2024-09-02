from bson import ObjectId
from pydantic_core import core_schema
from typing import Annotated, Any, Callable


class _ObjectIdPydanticAnnotation:
    # Based on https://docs.pydantic.dev/latest/usage/types/custom/#handling-third-party-types. # noqa

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> ObjectId:
            try:
                return ObjectId(input_value)
            except Exception as e:
                raise ValueError(e)

        return core_schema.union_schema(
            [
                core_schema.no_info_plain_validator_function(
                    validate_from_str
                ),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )


PyObjectId = Annotated[ObjectId, _ObjectIdPydanticAnnotation]
