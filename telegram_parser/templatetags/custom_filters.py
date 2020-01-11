from django import template
from datetime import datetime
register = template.Library()


@register.filter
def to_datetime(tiemstamp) -> str:
    return(datetime.fromtimestamp(tiemstamp))
