import jsonschema
from jasonutils.domain.interfaces import ICommandValidator
from jasonutils.domain.exceptions import ValidationError

class JsonSchemaValidator(ICommandValidator):
    def __init__(self, schema: dict):
        self._schema = schema

    def validate(self, raw_data: dict) -> None:
        try:
            jsonschema.validate(instance=raw_data, schema=self._schema)
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Ошибка валидации JSON Schema: {e.message}")