"""
User CRUD Functions Package
Database operations for user self-management
"""

from .user_crud import (
    UserCRUDError,
    create_user,
    get_user_by_id,
    get_user_by_email,
    update_user_profile,
    change_user_password,
    deactivate_user_account,
    delete_user_account,
    get_user_settings,
    update_user_settings,
    get_user_statistics,
    get_user_messages,
    search_user_messages,
    update_user_profile_picture,
    get_user_profile_picture_url
)

__all__ = [
    'UserCRUDError',
    'create_user',
    'get_user_by_id',
    'get_user_by_email',
    'update_user_profile',
    'change_user_password',
    'deactivate_user_account',
    'delete_user_account',
    'get_user_settings',
    'update_user_settings',
    'get_user_statistics',
    'get_user_messages',
    'search_user_messages',
    'update_user_profile_picture',
    'get_user_profile_picture_url'
]