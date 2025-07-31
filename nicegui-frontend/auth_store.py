from typing import Optional, Dict, Any
import json
import os

class AuthStore:
    def __init__(self):
        self.token: Optional[str] = None
        self.user: Optional[Dict[str, Any]] = None
        self.is_authenticated: bool = False
        self.remember_me: bool = False
        self._load_from_storage()
    
    def _get_storage_file(self) -> str:
        """Get the path to the storage file"""
        return os.path.join(os.path.dirname(__file__), 'auth_storage.json')
    
    def _save_to_storage(self):
        """Save authentication state to file"""
        storage_data = {
            'token': self.token,
            'user': self.user,
            'is_authenticated': self.is_authenticated,
            'remember_me': self.remember_me
        }
        
        try:
            with open(self._get_storage_file(), 'w') as f:
                json.dump(storage_data, f)
        except Exception as e:
            print(f"Error saving auth state: {e}")
    
    def _load_from_storage(self):
        """Load authentication state from file"""
        try:
            if os.path.exists(self._get_storage_file()):
                with open(self._get_storage_file(), 'r') as f:
                    data = json.load(f)
                    if data.get('remember_me') and data.get('is_authenticated'):
                        self.token = data.get('token')
                        self.user = data.get('user')
                        self.is_authenticated = data.get('is_authenticated', False)
                        self.remember_me = data.get('remember_me', False)
        except Exception as e:
            print(f"Error loading auth state: {e}")
    
    def login(self, user: Dict[str, Any], token: str, remember_me: bool = False):
        """Login user"""
        self.user = user
        self.token = token
        self.is_authenticated = True
        self.remember_me = remember_me
        self._save_to_storage()
    
    def logout(self):
        """Logout user"""
        self.user = None
        self.token = None
        self.is_authenticated = False
        self.remember_me = False
        self._save_to_storage()
        
        # Remove storage file
        try:
            if os.path.exists(self._get_storage_file()):
                os.remove(self._get_storage_file())
        except Exception as e:
            print(f"Error removing auth storage: {e}")
    
    def get_user_id(self) -> Optional[str]:
        """Get current user ID"""
        return self.user.get('id') if self.user else None
    
    def get_user_name(self) -> Optional[str]:
        """Get current user name"""
        return self.user.get('name') if self.user else None
    
    def get_user_email(self) -> Optional[str]:
        """Get current user email"""
        return self.user.get('email') if self.user else None
    
    def get_theme_preference(self) -> str:
        """Get user theme preference"""
        return self.user.get('theme_preference', 'light') if self.user else 'light'
    
    def update_theme(self, theme: str):
        """Update user theme preference"""
        if self.user:
            self.user['theme_preference'] = theme
            self._save_to_storage()

# Global auth store instance
auth_store = AuthStore() 