from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import APIKey
import logging

logger = logging.getLogger(__name__)


class APIKeyAuthentication(TokenAuthentication):
    """
    Custom API Key Authentication
    Clients should authenticate by passing the key in the "Authorization"
    HTTP header, prepended with the string "ApiKey".
    
    Example: Authorization: ApiKey 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'ApiKey'
    model = APIKey

    def get_model(self):
        if self.model is not None:
            return self.model
        return APIKey

    def authenticate_credentials(self, key):
        """
        Authenticate the key string with the set API Key model and return
        a two-tuple of (user, token) if authentication succeeds, or raise an
        AuthenticationFailed exception if it fails.
        """
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed('Invalid API key.')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        if not token.is_active:
            raise AuthenticationFailed('API key is inactive.')

        # Update last_used timestamp
        from django.utils import timezone
        token.last_used = timezone.now()
        token.save(update_fields=['last_used'])

        return (token.user, token)
