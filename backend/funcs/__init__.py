"""
MyBella Functions Package
CRUD operations for users and administrative functions
"""

# Import user functions
from .users import (
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
    search_user_messages
)

# Import admin functions
from .admin import (
    AdminCRUDError,
    create_admin_user,
    get_all_users,
    get_user_details,
    admin_update_user,
    admin_reset_user_password,
    admin_delete_user,
    get_system_statistics,
    get_user_messages_admin,
    get_all_messages,
    search_all_messages,
    bulk_user_action,
    export_user_data
)

__all__ = [
    # User CRUD
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
    
    # Admin CRUD
    'AdminCRUDError',
    'create_admin_user',
    'get_all_users',
    'get_user_details',
    'admin_update_user',
    'admin_reset_user_password',
    'admin_delete_user',
    'get_system_statistics',
    'get_user_messages_admin',
    'get_all_messages',
    'search_all_messages',
    'bulk_user_action',
    'export_user_data'
]