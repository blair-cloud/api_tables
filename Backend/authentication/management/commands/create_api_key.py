from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import APIKey


class Command(BaseCommand):
    help = 'Generate API key for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to generate API key for')
        parser.add_argument('--regenerate', action='store_true', help='Regenerate key if it already exists')

    def handle(self, *args, **options):
        username = options['username']
        regenerate = options.get('regenerate', False)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            return

        # Check if API key already exists
        api_key, created = APIKey.objects.get_or_create(user=user)

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ API key generated for user "{username}"'))
        elif regenerate:
            api_key.key = APIKey.generate_key()
            api_key.save()
            self.stdout.write(self.style.SUCCESS(f'✓ API key regenerated for user "{username}"'))
        else:
            self.stdout.write(self.style.WARNING(f'API key already exists for user "{username}". Use --regenerate to create a new one.'))

        self.stdout.write(self.style.SUCCESS(f'\nAPI Key: {api_key.key}'))
        self.stdout.write(f'User: {username}')
        self.stdout.write(f'Created: {api_key.created}')
        self.stdout.write(f'Active: {api_key.is_active}')
        self.stdout.write(f'\nUsage: Add header "Authorization: ApiKey {api_key.key}" to your requests')
