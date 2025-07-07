import uuid
from import_export import resources, fields
from django.utils.timezone import now

class BaseModelResource(resources.ModelResource):
    """Base class for handling common fields during import."""
    def before_import_row(self, row, **kwargs):
        print(f"Processing row: {row}")  # Debugging output

        if 'id' not in row or not row['id']:
            row['id'] = str(uuid.uuid4())  # Generate UUID if not provided
            print(f"Generated new UUID: {row['id']}")
        row.setdefault('active', True)
        row.setdefault('_created_by', None)
        row.setdefault('_updated_by', None)
        row.setdefault('_created_at', now())
        row.setdefault('_updated_at', now())

        print(f"Updated row: {row}")  # Debugging output

        super().before_import_row(row, **kwargs)