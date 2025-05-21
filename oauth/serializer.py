from rest_framework import serializers


class OAuthTokenRequestSerializer(serializers.Serializer):
    grant_type = serializers.CharField()
    client_secret = serializers.CharField()
    redirect_uri = serializers.URLField()
    code = serializers.CharField()

    def validate_grant_type(self, value):
        if value != 'code':
            raise serializers.ValidationError('invalid grand type')
        return value
