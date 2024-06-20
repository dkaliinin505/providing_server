from marshmallow import ValidationError


def validate_nested_structure(data):
    if data.get('nested_structure') and not data.get('nested_folder'):
        raise ValidationError('nested_folder must be provided if nested_structure is True')
    elif not data.get('nested_structure'):
        data.pop('nested_folder', None)
