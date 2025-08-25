from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser

from core.paginations import CustomLimitOffsetPagination
from history.models import UserEmailHistory, ContactEmailHistory
from history.serializers import UserEmailHistorySerializer, ContactEmailHistorySerializer


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASS: UserEmailHistoryViewSet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UserEmailHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = UserEmailHistorySerializer
    queryset = UserEmailHistory.objects.all()  # .prefetch_related('_updated_by', '_created_by')
    pagination_class = CustomLimitOffsetPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('user_id', 'status', 'email_to', 'email_from')
    ordering_fields = ('user_id', 'status', 'email_to', 'email_from')
    search_fields = ('status', 'email_to', 'email_from', 'subject', 'body')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASS: ContactEmailHistoryViewSet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ContactEmailHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = ContactEmailHistorySerializer
    queryset = ContactEmailHistory.objects.all()  # .prefetch_related('_updated_by', '_created_by')
    pagination_class = CustomLimitOffsetPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('contact_id', 'correspondents', 'status', 'email_to', 'email_from')
    ordering_fields = ('contact_id', 'correspondents', 'status', 'email_to', 'email_from')
    search_fields = ('contact_id', 'correspondents', 'status', 'email_to', 'email_from', 'subject', 'body')
