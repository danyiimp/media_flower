from typing import Optional
from typing_extensions import Self
from pydantic import BaseModel, PrivateAttr, model_validator


class FileTypeMetadata(BaseModel):
    extension: Optional[str] = None
    mime_type: Optional[str] = None

    _omitted: Optional[bool] = PrivateAttr(None)

    @model_validator(mode="after")
    def check_both_provided_or_omitted(self) -> Self:
        if (self.mime_type is None) and (self.extension is None):
            self._omitted = True
        elif (self.mime_type is not None) and (self.extension is not None):
            self._omitted = False
        else:
            raise ValueError(
                "Both extension and mimetype must be provided or omitted"
            )
        return self

    def is_omitted(self) -> bool:
        if self._omitted is None:
            raise ValueError("Validate the model first")
        return self._omitted
