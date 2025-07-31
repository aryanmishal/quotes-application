from typing import List, Dict, Any, Optional
from datetime import datetime, date
import json
import os

class QuotesStore:
    def __init__(self):
        self.quotes: List[Dict[str, Any]] = []
        self.loading: bool = False
        self.quote_of_the_day: Optional[Dict[str, Any]] = None
        self.author_filter: Optional[str] = None
        self._load_quote_of_the_day()
    
    def _get_storage_file(self) -> str:
        """Get the path to the storage file"""
        return os.path.join(os.path.dirname(__file__), 'quote_of_the_day.json')
    
    def _save_quote_of_the_day(self):
        """Save quote of the day to file"""
        if self.quote_of_the_day:
            storage_data = {
                'quote': self.quote_of_the_day,
                'date': date.today().isoformat()
            }
            try:
                with open(self._get_storage_file(), 'w') as f:
                    json.dump(storage_data, f)
            except Exception as e:
                print(f"Error saving quote of the day: {e}")
    
    def _load_quote_of_the_day(self):
        """Load quote of the day from file"""
        try:
            if os.path.exists(self._get_storage_file()):
                with open(self._get_storage_file(), 'r') as f:
                    data = json.load(f)
                    stored_date = data.get('date')
                    if stored_date == date.today().isoformat():
                        self.quote_of_the_day = data.get('quote')
        except Exception as e:
            print(f"Error loading quote of the day: {e}")
    
    def set_quotes(self, quotes: List[Dict[str, Any]]):
        """Set quotes list"""
        self.quotes = quotes
    
    def add_quote(self, quote: Dict[str, Any]):
        """Add a new quote"""
        self.quotes.insert(0, quote)
    
    def update_quote(self, quote_id: str, updated_quote: Dict[str, Any]):
        """Update a quote"""
        for i, quote in enumerate(self.quotes):
            if quote.get('_id') == quote_id:
                self.quotes[i] = {**quote, **updated_quote}
                break
    
    def remove_quote(self, quote_id: str):
        """Remove a quote"""
        self.quotes = [q for q in self.quotes if q.get('_id') != quote_id]
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        self.loading = loading
    
    def set_quote_of_the_day(self, quote: Dict[str, Any]):
        """Set quote of the day"""
        self.quote_of_the_day = quote
        self._save_quote_of_the_day()
    
    def get_quotes_by_author(self, author: str) -> List[Dict[str, Any]]:
        """Get quotes by author"""
        return [q for q in self.quotes if q.get('author', '').lower() == author.lower()]
    
    def get_my_quotes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get quotes by current user"""
        return [q for q in self.quotes if q.get('user_id') == user_id]
    
    def get_liked_quotes(self) -> List[Dict[str, Any]]:
        """Get quotes liked by current user"""
        return [q for q in self.quotes if q.get('is_liked', False)]
    
    def search_quotes(self, query: str, search_by: str = "all") -> List[Dict[str, Any]]:
        """Search quotes by text with a specific filter."""
        query_lower = query.lower()
        if not query_lower:
            return self.quotes

        if search_by == 'quote':
            return [q for q in self.quotes if query_lower in q.get('quote', '').lower()]
        if search_by == 'author':
            return [q for q in self.quotes if query_lower in q.get('author', '').lower()]
        if search_by == 'tags':
            # Handle tags as a list, checking for None
            return [q for q in self.quotes if any(query_lower in tag.lower() for tag in (q.get('tags') or []))]

        # Default to 'all'
        return [
            q for q in self.quotes
            if query_lower in q.get('quote', '').lower() or
               query_lower in q.get('author', '').lower() or
               any(query_lower in tag.lower() for tag in (q.get('tags') or []))
        ]
    
    def get_authors(self) -> List[str]:
        """Get list of all authors"""
        authors = set()
        for quote in self.quotes:
            if quote.get('author'):
                authors.add(quote['author'])
        return sorted(list(authors))
    
    def get_quote_by_id(self, quote_id: str) -> Optional[Dict[str, Any]]:
        """Get quote by ID"""
        for quote in self.quotes:
            if quote.get('_id') == quote_id:
                return quote
        return None
    
    def set_author_filter(self, author: Optional[str]):
        """Set the author filter"""
        self.author_filter = author

# Global quotes store instance
quotes_store = QuotesStore() 