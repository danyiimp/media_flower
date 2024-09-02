
from inspect import signature
from fastapi.exceptions import HTTPException
from pydantic_core import ValidationError


def make_dependable(cls):
    """
    Pydantic BaseModels are very powerful because we get lots of validations and type checking right out of the box.
    FastAPI can accept a BaseModel as a route Dependency and it will automatically handle things like documentation
    and error handling. However, if we define custom validators then the errors they raise are not handled, leading
    to HTTP 500's being returned.

    To better understand this issue, you can visit https://github.com/tiangolo/fastapi/issues/1474 for context.
    This function automates the creation of a workaround method with a matching signature so that you
    can avoid code duplication.

    usage:
    async def fetch(thing_request: ThingRequest = Depends(make_dependable(ThingRequest))):
    """ # noqa

    def init_cls_and_handle_errors(*args, **kwargs):
        try:
            signature(init_cls_and_handle_errors).bind(*args, **kwargs)
            return cls(*args, **kwargs)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                error["loc"] = ["query"] + list(error["loc"])
                error["ctx"]["error"] = str(error["ctx"]["error"])
                errors.append(error)
            raise HTTPException(422, detail=errors) from e

    init_cls_and_handle_errors.__signature__ = signature(cls)
    return init_cls_and_handle_errors
