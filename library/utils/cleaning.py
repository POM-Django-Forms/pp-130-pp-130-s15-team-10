def clean_str_field(value):
    """Очищує рядок: якщо None, повертає пустий рядок, інакше повертає value.strip()."""
    if value is None:
        return ''
    return value.strip()
