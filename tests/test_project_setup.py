from django.contrib.auth import get_user_model


def test_custom_user_model_is_active() -> None:
    user_model = get_user_model()

    assert user_model.__name__ == "User"
    assert user_model._meta.app_label == "accounts"
