from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone", "address", "avatar_url", "frequent_journeys", "created_at"]
        read_only_fields = ["id", "role", "created_at"]


class AdminUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ["id", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "phone"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data, role=User.Role.PASSENGER)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier") or attrs.get("email")
        if not identifier:
            raise serializers.ValidationError("Enter your username or email.")

        login_email = identifier
        if "@" not in identifier:
            user_row = User.objects.filter(username__iexact=identifier).first()
            if user_row:
                login_email = user_row.email

        user = authenticate(username=login_email, password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid username/email or password.")
        attrs["user"] = user
        return attrs
