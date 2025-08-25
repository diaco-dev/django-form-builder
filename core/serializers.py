
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from rest_framework_extensions.serializers import PartialUpdateSerializerMixin
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
# ---------------------------------------------------------------------------------------------------------------------
# refresh token
# ---------------------------------------------------------------------------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = user.user_type
        token['exp_time'] = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        return token




class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
        A ModelSerializer that takes an additional `fields` argument that
        controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        if fields is None:
            try:
                fields = kwargs['context']['request'].query_params.get('fields', None)

                if fields:
                    fields = fields.split(',')
            except:
                fields = None

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        request = self.context.get('request')
        if request and request.method == 'POST':
            self.Meta.depth = 0
        else:
            self.Meta.depth = 0


#  Order must be -> 1-PartialUpdateSerializerMixin, 2-DynamicFieldsModelSerializer, 3-FlexFieldsModelSerializer
class CustomSerializer(PartialUpdateSerializerMixin, DynamicFieldsModelSerializer, FlexFieldsModelSerializer):
    pass
