from marshmallow import ValidationError


def validate_nested_structure(data):
    errors = {}
    if data.get('is_nested_structure') and not data.get('nested_folder'):
        errors['nested_folder'] = 'nested_folder must be provided if is_nested_structure is True'
    elif not data.get('is_nested_structure') and 'nested_folder' in data:
        errors['nested_folder'] = 'nested_folder should not be provided if is_nested_structure is False'
    if errors:
        raise ValidationError(errors)
