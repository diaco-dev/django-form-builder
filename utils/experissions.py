from django.db import models


class ConcatExpression(models.Func):
    arg_joiner = " || "
    function = None
    output_field = models.CharField(max_length=300)
    template = "%(expressions)s"
