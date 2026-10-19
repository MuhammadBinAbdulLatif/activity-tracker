from rest_framework import serializers


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=200)
    password = serializers.CharField(required=True, max_length=200)


class LoginSerializer(SignUpSerializer):
    # not a good practive but i like to remove any ambiguity
    pass
