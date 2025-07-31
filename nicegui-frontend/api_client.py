import requests
import json
from typing import Dict, List, Optional, Any
from config import API_BASE_URL

class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.token = None
        
    def set_token(self, token: str):
        """Set the authentication token"""
        self.token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})
        
    def clear_token(self):
        """Clear the authentication token"""
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make a request to the API"""
        url = f"{self.base_url}{endpoint}"
        print(f'[DEBUG] Request headers: {self.session.headers}')
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, data=data)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    self.clear_token()
                raise Exception(f"API Error: {e.response.status_code} - {e.response.text}")
            else:
                raise Exception(f"Network Error: {str(e)}")

class AuthAPI:
    def __init__(self, client: APIClient):
        self.client = client
    
    def login(self, email: str, password: str) -> Dict:
        """Login user"""
        data = {
            'username': email,  # OAuth2 expects 'username' field
            'password': password
        }
        return self.client._make_request('POST', '/auth/login', data=data)
    
    def register(self, name: str, email: str, password: str) -> Dict:
        """Register new user"""
        data = {
            'name': name,
            'email': email,
            'password': password
        }
        return self.client._make_request('POST', '/auth/register', data=data)
    
    def update_theme(self, theme: str) -> Dict:
        """Update user theme preference"""
        return self.client._make_request('POST', f'/auth/update-theme?theme={theme}')
    
    def get_me(self) -> Dict:
        """Get current user info"""
        return self.client._make_request('GET', '/auth/me')

class QuotesAPI:
    def __init__(self, client: APIClient):
        self.client = client
    
    def get_quotes(self) -> List[Dict]:
        """Get all quotes"""
        return self.client._make_request('GET', '/quotes/')
    
    def get_quote(self, quote_id: str) -> Dict:
        """Get a specific quote"""
        return self.client._make_request('GET', f'/quotes/{quote_id}/')
    
    def create_quote(self, quote: str, author: str, tags: str = '') -> Dict:
        """Create a new quote"""
        data = {
            'quote': quote,
            'author': author,
            'tags': tags
        }
        return self.client._make_request('POST', '/quotes/', data=data)
    
    def update_quote(self, quote_id: str, quote: str = None, author: str = None, tags: str = None) -> Dict:
        """Update a quote"""
        data = {}
        if quote is not None:
            data['quote'] = quote
        if author is not None:
            data['author'] = author
        if tags is not None:
            data['tags'] = tags
        return self.client._make_request('PATCH', f'/quotes/{quote_id}/', data=data)
    
    def delete_quote(self, quote_id: str) -> None:
        """Delete a quote"""
        return self.client._make_request('DELETE', f'/quotes/{quote_id}/')
    
    def like_quote(self, quote_id: str) -> Dict:
        """Like a quote"""
        endpoint = f'/quotes/{quote_id}/likes/up'
        print(f'[DEBUG] Like endpoint: {self.client.base_url}{endpoint}')
        return self.client._make_request('POST', endpoint)
    
    def dislike_quote(self, quote_id: str) -> Dict:
        """Dislike a quote"""
        endpoint = f'/quotes/{quote_id}/dislike/up'
        print(f'[DEBUG] Dislike endpoint: {self.client.base_url}{endpoint}')
        return self.client._make_request('POST', endpoint)
    
    def get_quote_reactions(self, quote_id: str) -> Dict:
        """Get quote reactions"""
        return self.client._make_request('GET', f'/quotes/{quote_id}/reactions/')
    
    def search_quotes(self, author: str = None, quote: str = None, tags: str = None) -> List[Dict]:
        """Search quotes"""
        params = {}
        if author:
            params['author'] = author
        if quote:
            params['quote'] = quote
        if tags:
            params['tags'] = tags
        return self.client._make_request('GET', '/quotes/search/', params=params) 