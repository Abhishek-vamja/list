from django.db import models
from django.core.exceptions import ValidationError
from core.models import BaseModel


class Module(BaseModel):
    module_name = models.CharField(max_length=255, unique=True)
    module_fields = models.JSONField(default=dict)  # Example: {"name": "string", "category": "string"}

    def __str__(self):
        return self.module_name


class CRUD(BaseModel):
    module_type = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="records")
    values = models.JSONField()

    def clean(self):
        """
        Validate that `values` matches the structure defined in `module_fields`.
        """
        expected_fields = self.module_type.module_fields  # Expected schema
        provided_values = self.values  # User-provided values

        # Check if required keys are present
        missing_fields = set(expected_fields.keys()) - set(provided_values.keys())
        if missing_fields:
            raise ValidationError(f"Missing required fields: {missing_fields}")

        # Optional: Check field types (basic validation)
        for field, field_type in expected_fields.items():
            if field in provided_values:
                if field_type == "string" and not isinstance(provided_values[field], str):
                    raise ValidationError(f"Field '{field}' must be a string.")
                elif field_type == "integer" and not isinstance(provided_values[field], int):
                    raise ValidationError(f"Field '{field}' must be an integer.")

    def save(self, *args, **kwargs):
        self.clean()  # Run validation before saving
        super().save(*args, **kwargs)
