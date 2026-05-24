from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class ActiveUserJWTAuthentication(JWTAuthentication):
    """Reject JWTs for deactivated (soft-deleted) accounts."""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not user.is_active:
            raise AuthenticationFailed(
                "This account was deactivated. Contact the dealer to restore access.",
                code="account_deactivated",
            )
        return user
