from src.generators.user_store_manager import UserStoreManager
from src.models.data_models import Location, UserProfile, Transaction


def test_create_empty_user_profile():
    user_profile = UserProfile()
    print(user_profile)

    assert isinstance(user_profile, UserProfile)

def test_user_store_create_empty_profile():
    user_store = UserStoreManager()
    empty_profile = user_store.create_empty_profile()

    print(empty_profile)
    assert isinstance(empty_profile, UserProfile)


def test_user_store_update_state_store():
    user_store = UserStoreManager()
    empty_profile = user_store.create_empty_profile()

    user_store.update_state_store(
        user_id= empty_profile.user_id,
        updated_profile= empty_profile
    )

    assert user_store.user_count == 1 

