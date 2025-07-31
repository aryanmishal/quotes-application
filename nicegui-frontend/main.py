from nicegui import ui, app
from api_client import APIClient, AuthAPI, QuotesAPI
from auth_store import auth_store
from quotes_store import quotes_store
import asyncio
from typing import List, Dict, Any, Optional
import random

# Initialize API client
api_client = APIClient()
auth_api = AuthAPI(api_client)
quotes_api = QuotesAPI(api_client)

# Global variables
current_tab = 'home'
current_page = 1
items_per_page = 10
search_query = ''
selected_author = ''
editing_quote = None
delete_quote_id = None

# UI Components
header = None
content_area = None
login_dialog = None
register_dialog = None
new_quote_dialog = None
edit_quote_dialog = None
delete_quote_dialog = None

def setup_theme():
    """Setup theme based on user preference"""
    theme = auth_store.get_theme_preference()
    if theme == 'dark':
        ui.dark_mode().enable()
    else:
        ui.dark_mode().disable()

def create_header():
    """Create the application header"""
    global header
    
    with ui.header().classes('bg-blue-600 text-white p-4'):
        with ui.row().classes('w-full justify-between items-center'):
            # Logo and title
            with ui.row().classes('items-center'):
                ui.icon('format_quote').classes('text-2xl mr-2')
                ui.label('Quotes Application').classes('text-xl font-bold')
            
            # Navigation and user controls
            with ui.row().classes('items-center gap-4'):
                # Theme toggle
                theme_btn = ui.button(
                    icon='dark_mode' if auth_store.get_theme_preference() == 'light' else 'light_mode',
                    on_click=toggle_theme
                ).classes('bg-blue-700 hover:bg-blue-800')
                
                if auth_store.is_authenticated:
                    # User menu
                    with ui.dropdown().classes('bg-white text-gray-900'):
                        ui.button(
                            f'Welcome, {auth_store.get_user_name()}',
                            icon='account_circle'
                        ).classes('bg-blue-700 hover:bg-blue-800')
                        
                        with ui.menu().classes('bg-white text-gray-900'):
                            ui.menu_item('My Quotes', on_click=lambda: switch_tab('manage'))
                            ui.menu_item('Logout', on_click=logout)
                else:
                    # Auth buttons
                    ui.button('Login', on_click=show_login_dialog).classes('bg-blue-700 hover:bg-blue-800')
                    ui.button('Register', on_click=show_register_dialog).classes('bg-green-700 hover:bg-green-800')

def create_navigation():
    """Create the navigation tabs"""
    with ui.tabs().classes('w-full bg-gray-100') as tabs:
        ui.tab('Home', icon='home')
        ui.tab('Quotes', icon='format_quote')
        ui.tab('Authors', icon='person')
        if auth_store.is_authenticated:
            ui.tab('Manage', icon='settings')
    
    tabs.on('change', handle_tab_change)
    return tabs

def create_content_area():
    """Create the main content area"""
    global content_area
    content_area = ui.column().classes('w-full p-4')

def create_dialogs():
    """Create all dialog components"""
    create_login_dialog()
    create_register_dialog()
    create_new_quote_dialog()
    create_edit_quote_dialog()
    create_delete_quote_dialog()

def create_login_dialog():
    """Create login dialog"""
    global login_dialog
    
    with ui.dialog() as dialog:
        with ui.card().classes('w-96'):
            ui.label('Login').classes('text-2xl font-bold mb-4')
            
            email_input = ui.input('Email', type='email').classes('w-full mb-4')
            password_input = ui.input('Password', type='password').classes('w-full mb-4')
            remember_checkbox = ui.checkbox('Remember me')
            
            with ui.row().classes('w-full justify-between'):
                ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                ui.button('Login', on_click=lambda: handle_login(email_input.value, password_input.value, remember_checkbox.value, dialog)).classes('bg-blue-600 hover:bg-blue-700')
    
    login_dialog = dialog

def create_register_dialog():
    """Create register dialog"""
    global register_dialog
    
    with ui.dialog() as dialog:
        with ui.card().classes('w-96'):
            ui.label('Create Account').classes('text-2xl font-bold mb-4')
            
            name_input = ui.input('Name').classes('w-full mb-4')
            email_input = ui.input('Email', type='email').classes('w-full mb-4')
            password_input = ui.input('Password', type='password').classes('w-full mb-4')
            
            with ui.row().classes('w-full justify-between'):
                ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                ui.button('Register', on_click=lambda: handle_register(name_input.value, email_input.value, password_input.value, dialog)).classes('bg-green-600 hover:bg-green-700')
    
    register_dialog = dialog

def create_new_quote_dialog():
    """Create new quote dialog"""
    global new_quote_dialog
    
    with ui.dialog() as dialog:
        with ui.card().classes('w-96'):
            ui.label('Add New Quote').classes('text-2xl font-bold mb-4')
            
            quote_input = ui.textarea('Quote', rows=4).classes('w-full mb-4')
            author_input = ui.input('Author').classes('w-full mb-4')
            tags_input = ui.input('Tags (comma separated)').classes('w-full mb-4')
            
            with ui.row().classes('w-full justify-between'):
                ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                ui.button('Add Quote', on_click=lambda: handle_create_quote(quote_input.value, author_input.value, tags_input.value, dialog)).classes('bg-blue-600 hover:bg-blue-700')
    
    new_quote_dialog = dialog

def create_edit_quote_dialog():
    """Create edit quote dialog"""
    global edit_quote_dialog
    
    with ui.dialog() as dialog:
        with ui.card().classes('w-96'):
            ui.label('Edit Quote').classes('text-2xl font-bold mb-4')
            
            quote_input = ui.textarea('Quote', rows=4).classes('w-full mb-4')
            author_input = ui.input('Author').classes('w-full mb-4')
            tags_input = ui.input('Tags (comma separated)').classes('w-full mb-4')
            
            with ui.row().classes('w-full justify-between'):
                ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                ui.button('Update Quote', on_click=lambda: handle_update_quote(quote_input.value, author_input.value, tags_input.value, dialog)).classes('bg-blue-600 hover:bg-blue-700')
    
    edit_quote_dialog = dialog

def create_delete_quote_dialog():
    """Create delete quote dialog"""
    global delete_quote_dialog
    
    with ui.dialog() as dialog:
        with ui.card().classes('w-96'):
            ui.label('Delete Quote').classes('text-2xl font-bold mb-4')
            ui.label('Are you sure you want to delete this quote? This action cannot be undone.').classes('mb-4')
            
            with ui.row().classes('w-full justify-between'):
                ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                ui.button('Delete', on_click=lambda: handle_delete_quote(dialog)).classes('bg-red-600 hover:bg-red-700')
    
    delete_quote_dialog = dialog

async def load_quotes():
    """Load quotes from API"""
    try:
        quotes_store.set_loading(True)
        quotes = await asyncio.to_thread(quotes_api.get_quotes)
        quotes_store.set_quotes(quotes)
        
        # Set quote of the day if not already set
        if not quotes_store.quote_of_the_day and quotes:
            quotes_store.set_quote_of_the_day(random.choice(quotes))
            
    except Exception as e:
        ui.notify(f'Error loading quotes: {str(e)}', type='error')
    finally:
        quotes_store.set_loading(False)

def render_quote_card(quote: Dict[str, Any]) -> ui.card:
    """Render a single quote card"""
    with ui.card().classes('w-full mb-4') as card:
        with ui.column().classes('w-full'):
            # Quote text
            ui.label(f'"{quote.get("quote", "")}"').classes('text-lg font-medium mb-2')
            
            # Author
            ui.label(f'— {quote.get("author", "Unknown")}').classes('text-sm text-gray-600 mb-2')
            
            # Tags
            if quote.get('tags'):
                tags = quote['tags'].split(',')
                with ui.row().classes('flex-wrap gap-1 mb-2'):
                    for tag in tags:
                        if tag.strip():
                            ui.chip(tag.strip()).classes('bg-blue-100 text-blue-800')
            
            # User info
            if quote.get('user_name'):
                ui.label(f'Added by {quote["user_name"]}').classes('text-xs text-gray-500 mb-2')
            
            # Actions row
            with ui.row().classes('w-full justify-between items-center'):
                # Like/Dislike buttons
                with ui.row().classes('gap-2'):
                    like_btn = ui.button(
                        icon='thumb_up',
                        on_click=lambda q=quote: handle_like_quote(q['_id'])
                    ).classes('bg-green-100 hover:bg-green-200 text-green-800')
                    
                    ui.label(str(quote.get('likes', 0))).classes('text-sm')
                    
                    dislike_btn = ui.button(
                        icon='thumb_down',
                        on_click=lambda q=quote: handle_dislike_quote(q['_id'])
                    ).classes('bg-red-100 hover:bg-red-200 text-red-800')
                    
                    ui.label(str(quote.get('dislikes', 0))).classes('text-sm')
                
                # Edit/Delete buttons (only for quote owner)
                if auth_store.is_authenticated and quote.get('user_id') == auth_store.get_user_id():
                    with ui.row().classes('gap-2'):
                        ui.button(
                            icon='edit',
                            on_click=lambda q=quote: show_edit_quote_dialog(q)
                        ).classes('bg-blue-100 hover:bg-blue-200 text-blue-800')
                        
                        ui.button(
                            icon='delete',
                            on_click=lambda q=quote: show_delete_quote_dialog(q['_id'])
                        ).classes('bg-red-100 hover:bg-red-200 text-red-800')
    
    return card

def render_home_tab():
    """Render the home tab content"""
    content_area.clear()
    
    with content_area:
        # Quote of the day
        if quotes_store.quote_of_the_day:
            with ui.card().classes('w-full mb-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white'):
                ui.label('Quote of the Day').classes('text-xl font-bold mb-4')
                ui.label(f'"{quotes_store.quote_of_the_day.get("quote", "")}"').classes('text-lg mb-2')
                ui.label(f'— {quotes_store.quote_of_the_day.get("author", "Unknown")}').classes('text-sm opacity-90')
        
        # Add new quote button (if authenticated)
        if auth_store.is_authenticated:
            ui.button('Add New Quote', icon='add', on_click=show_new_quote_dialog).classes('mb-4 bg-blue-600 hover:bg-blue-700')
        
        # Recent quotes
        ui.label('Recent Quotes').classes('text-xl font-bold mb-4')
        
        if quotes_store.loading:
            ui.spinner('dots').classes('text-2xl')
        elif quotes_store.quotes:
            for quote in quotes_store.quotes[:5]:  # Show first 5 quotes
                render_quote_card(quote)
        else:
            ui.label('No quotes available').classes('text-gray-500')

def render_quotes_tab():
    """Render the quotes tab content"""
    content_area.clear()
    
    with content_area:
        # Search and filter controls
        with ui.row().classes('w-full mb-4 gap-4'):
            search_input = ui.input('Search quotes...', on_change=handle_search_change).classes('flex-1')
            ui.button('Search', on_click=lambda: handle_search(search_input.value)).classes('bg-blue-600 hover:bg-blue-700')
        
        # Quotes list
        if quotes_store.loading:
            ui.spinner('dots').classes('text-2xl')
        elif quotes_store.quotes:
            for quote in quotes_store.quotes:
                render_quote_card(quote)
        else:
            ui.label('No quotes found').classes('text-gray-500')

def render_authors_tab():
    """Render the authors tab content"""
    content_area.clear()
    
    with content_area:
        authors = quotes_store.get_authors()
        
        if authors:
            ui.label('All Authors').classes('text-xl font-bold mb-4')
            
            for author in authors:
                author_quotes = quotes_store.get_quotes_by_author(author)
                with ui.card().classes('w-full mb-4'):
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label(author).classes('text-lg font-medium')
                        ui.label(f'{len(author_quotes)} quotes').classes('text-sm text-gray-600')
                    
                    # Show first quote as preview
                    if author_quotes:
                        preview_quote = author_quotes[0]
                        ui.label(f'"{preview_quote.get("quote", "")[:100]}..."').classes('text-sm text-gray-700 mt-2')
        else:
            ui.label('No authors found').classes('text-gray-500')

def render_manage_tab():
    """Render the manage tab content"""
    content_area.clear()
    
    with content_area:
        if not auth_store.is_authenticated:
            ui.label('Please login to manage your quotes').classes('text-gray-500')
            return
        
        # My quotes
        my_quotes = quotes_store.get_my_quotes(auth_store.get_user_id())
        
        ui.label('My Quotes').classes('text-xl font-bold mb-4')
        
        if my_quotes:
            for quote in my_quotes:
                render_quote_card(quote)
        else:
            ui.label('You haven\'t added any quotes yet').classes('text-gray-500')

def handle_tab_change(e):
    """Handle tab change"""
    global current_tab
    current_tab = e.value
    
    if current_tab == 'home':
        render_home_tab()
    elif current_tab == 'quotes':
        render_quotes_tab()
    elif current_tab == 'authors':
        render_authors_tab()
    elif current_tab == 'manage':
        render_manage_tab()

def switch_tab(tab_name: str):
    """Switch to a specific tab"""
    global current_tab
    current_tab = tab_name
    handle_tab_change(type('Event', (), {'value': tab_name})())

async def handle_login(email: str, password: str, remember_me: bool, dialog):
    """Handle login"""
    try:
        response = await asyncio.to_thread(auth_api.login, email, password)
        
        if response.get('access_token') and response.get('user'):
            auth_store.login(response['user'], response['access_token'], remember_me)
            api_client.set_token(response['access_token'])
            
            dialog.close()
            ui.notify('Successfully logged in!', type='positive')
            
            # Refresh UI
            create_header()
            render_home_tab()
        else:
            ui.notify('Invalid response from server', type='error')
    except Exception as e:
        ui.notify(f'Login failed: {str(e)}', type='error')

async def handle_register(name: str, email: str, password: str, dialog):
    """Handle registration"""
    try:
        await asyncio.to_thread(auth_api.register, name, email, password)
        dialog.close()
        ui.notify('Account created successfully! Please login.', type='positive')
        show_login_dialog()
    except Exception as e:
        ui.notify(f'Registration failed: {str(e)}', type='error')

def logout():
    """Handle logout"""
    auth_store.logout()
    api_client.clear_token()
    ui.notify('Logged out successfully', type='positive')
    
    # Refresh UI
    create_header()
    render_home_tab()

def toggle_theme():
    """Toggle between light and dark themes"""
    current_theme = auth_store.get_theme_preference()
    new_theme = 'dark' if current_theme == 'light' else 'light'
    
    auth_store.update_theme(new_theme)
    
    if new_theme == 'dark':
        ui.dark_mode().enable()
    else:
        ui.dark_mode().disable()
    
    # Update theme button icon
    create_header()

def show_login_dialog():
    """Show login dialog"""
    login_dialog.open()

def show_register_dialog():
    """Show register dialog"""
    register_dialog.open()

def show_new_quote_dialog():
    """Show new quote dialog"""
    new_quote_dialog.open()

def show_edit_quote_dialog(quote: Dict[str, Any]):
    """Show edit quote dialog"""
    global editing_quote
    editing_quote = quote
    
    # Populate dialog fields
    dialog_content = edit_quote_dialog.content
    quote_input = dialog_content.find_child('textarea')
    author_input = dialog_content.find_child('input', lambda x: x.props.get('label') == 'Author')
    tags_input = dialog_content.find_child('input', lambda x: x.props.get('label') == 'Tags')
    
    if quote_input:
        quote_input.value = quote.get('quote', '')
    if author_input:
        author_input.value = quote.get('author', '')
    if tags_input:
        tags_input.value = quote.get('tags', '')
    
    edit_quote_dialog.open()

def show_delete_quote_dialog(quote_id: str):
    """Show delete quote dialog"""
    global delete_quote_id
    delete_quote_id = quote_id
    delete_quote_dialog.open()

async def handle_create_quote(quote_text: str, author: str, tags: str, dialog):
    """Handle creating a new quote"""
    try:
        new_quote = await asyncio.to_thread(quotes_api.create_quote, quote_text, author, tags)
        quotes_store.add_quote(new_quote)
        
        dialog.close()
        ui.notify('Quote created successfully!', type='positive')
        
        # Refresh current tab
        handle_tab_change(type('Event', (), {'value': current_tab})())
    except Exception as e:
        ui.notify(f'Failed to create quote: {str(e)}', type='error')

async def handle_update_quote(quote_text: str, author: str, tags: str, dialog):
    """Handle updating a quote"""
    try:
        if editing_quote:
            updated_quote = await asyncio.to_thread(
                quotes_api.update_quote, 
                editing_quote['_id'], 
                quote_text, 
                author, 
                tags
            )
            quotes_store.update_quote(editing_quote['_id'], updated_quote)
            
            dialog.close()
            ui.notify('Quote updated successfully!', type='positive')
            
            # Refresh current tab
            handle_tab_change(type('Event', (), {'value': current_tab})())
    except Exception as e:
        ui.notify(f'Failed to update quote: {str(e)}', type='error')

async def handle_delete_quote(dialog):
    """Handle deleting a quote"""
    try:
        if delete_quote_id:
            await asyncio.to_thread(quotes_api.delete_quote, delete_quote_id)
            quotes_store.remove_quote(delete_quote_id)
            
            dialog.close()
            ui.notify('Quote deleted successfully!', type='positive')
            
            # Refresh current tab
            handle_tab_change(type('Event', (), {'value': current_tab})())
    except Exception as e:
        ui.notify(f'Failed to delete quote: {str(e)}', type='error')

async def handle_like_quote(quote_id: str):
    """Handle liking a quote"""
    try:
        await asyncio.to_thread(quotes_api.like_quote, quote_id)
        await load_quotes()  # Refresh quotes to get updated like status
        ui.notify('Quote liked!', type='positive')
    except Exception as e:
        ui.notify(f'Failed to like quote: {str(e)}', type='error')

async def handle_dislike_quote(quote_id: str):
    """Handle disliking a quote"""
    try:
        await asyncio.to_thread(quotes_api.dislike_quote, quote_id)
        await load_quotes()  # Refresh quotes to get updated dislike status
        ui.notify('Quote disliked!', type='positive')
    except Exception as e:
        ui.notify(f'Failed to dislike quote: {str(e)}', type='error')

def handle_search_change(e):
    """Handle search input change"""
    global search_query
    search_query = e.value

def handle_search(query: str):
    """Handle search"""
    if query:
        filtered_quotes = quotes_store.search_quotes(query)
        quotes_store.set_quotes(filtered_quotes)
    else:
        # Reload all quotes
        asyncio.create_task(load_quotes())
    
    render_quotes_tab()

@ui.page('/')
def main_page():
    """Main application page"""
    # Setup theme
    setup_theme()
    
    # Create UI components
    create_header()
    create_navigation()
    create_content_area()
    create_dialogs()
    
    # Load initial data
    asyncio.create_task(load_quotes())
    
    # Render initial content
    render_home_tab()

if __name__ == '__main__':
    ui.run(
        title='Quotes Application',
        port=3001,
        reload=False,
        show=True
    ) 