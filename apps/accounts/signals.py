from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User
from apps.characters.models import CharacterProfile


@receiver(post_save, sender=User)
def create_character_profile(sender, instance: User, created: bool, **kwargs) -> None:
    if not created:
        return

    CharacterProfile.objects.create(
        user=instance,
        character_name=instance.username,
    )
