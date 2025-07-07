from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

def _positive_int(integer_string):
    ret = int(integer_string)
    if ret < 1:
        raise ValueError()
    return ret


class CustomLimitOffsetPagination(LimitOffsetPagination):
    limit_query_param = 'limit'
    offset_query_param = 'offset'

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None
        self.count = self.get_count(queryset)
        self.offset = self.get_offset(request)
        self.request = request

        if self.count == 0 or self.offset >= self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit])
    def get_offset(self, request):
        try:
            return _positive_int(request.query_params[self.offset_query_param])
        except (KeyError, ValueError):
            return 0

    def get_limit(self, request):
        if self.limit_query_param:
            try:
                return _positive_int(request.query_params[self.limit_query_param])
            except (KeyError, ValueError):
                pass

        return self.default_limit

    def get_paginated_response(self, data):
        pages_count = (
            0 if self.count == 0 else (self.count + self.limit - 1) // self.limit
        )
        current_page = (
            0 if self.count == 0 else (self.offset // self.limit) + 1
        )

        return Response({
            'pages_count': pages_count,
            'items_per_page': self.limit,
            'current_page_items_count': len(data),
            'current_page': current_page,
            'total_items': self.count,
            'items': data,
        })