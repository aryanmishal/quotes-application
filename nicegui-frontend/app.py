from nicegui import ui
from api_client import APIClient, AuthAPI, QuotesAPI
from auth_store import auth_store
from quotes_store import quotes_store
import asyncio
import random
import os

# Initialize API client
api_client = APIClient()
auth_api = AuthAPI(api_client)
quotes_api = QuotesAPI(api_client)

# State
current_tab = 'home'
header_container = None
tabs_container = None
content_container = None
login_dialog = None
register_dialog = None
new_quote_dialog = None
edit_quote_dialog = None
delete_quote_dialog = None
editing_quote = None
delete_quote_id = None
search_query = ""
search_by = "all"
quote_list_container = None
myquotes_subtab = 'my'
current_theme = 'light'

# Dialog references
login_email = None
login_password = None
remember_checkbox = None
reg_name = None
reg_email = None
reg_password = None
nq_quote = None
nq_author = None
nq_tags = None
eq_quote = None
eq_author = None
eq_tags = None

# --- Helper Functions ---
async def validate_stored_token():
    """Validate the stored token and clear authentication if invalid"""
    if auth_store.is_authenticated and auth_store.token:
        try:
            # Try to get current user info to validate token
            await asyncio.to_thread(auth_api.get_me)
            # If successful, set the token in API client
            api_client.set_token(auth_store.token)
        except Exception as e:
            print(f"Token validation failed: {e}")
            # Clear invalid authentication state
            auth_store.logout()
            api_client.clear_token()

def show_quotes_by_author(author_name: str):
    """Filter quotes by author and switch to quotes tab."""
    global current_tab
    quotes_store.set_author_filter(author_name)
    current_tab = 'quotes'
    if tabs_container:
        tabs_container.set_value('quotes')
    render_content()

# --- Async Data Loader ---
async def load_quotes():
    try:
        quotes_store.set_loading(True)
        quotes = await asyncio.to_thread(quotes_api.get_quotes)
        quotes_store.set_quotes(quotes)
        if not quotes_store.quote_of_the_day and quotes:
            quotes_store.set_quote_of_the_day(random.choice(quotes))
    except Exception as e:
        # Show notification in UI context
        if content_container:
            with content_container:
                ui.notify(f'Error loading quotes: {str(e)}', type='error')
    finally:
        quotes_store.set_loading(False)
        # Use the new refresh function to avoid focus stealing
        refresh_ui()

# --- UI Functions ---
def refresh_ui():
    """Intelligently refresh the UI to avoid focus-stealing bugs."""
    # On the quotes tab, only update the list.
    # For all other tabs, a full re-render is safe and necessary.
    if current_tab == 'quotes':
        update_quote_list()
    else:
        render_content()

def render_header():
    def get_theme_js():
        return '''
            let theme = localStorage.getItem('theme-guest') || 'light';
            if (theme === 'dark') {
                document.body.classList.add('dark');
            } else {
                document.body.classList.remove('dark');
            }
            return theme;
        '''
    def set_theme_js():
        return '''
            let theme = document.body.classList.contains('dark') ? 'light' : 'dark';
            if (theme === 'dark') {
                document.body.classList.add('dark');
            } else {
                document.body.classList.remove('dark');
            }
            localStorage.setItem('theme-guest', theme);
            return theme;
        '''
    # On header render, set the theme class from user/localStorage and sync Python state
    theme = ui.run_javascript(get_theme_js())
    if auth_store.is_authenticated and auth_store.get_theme_preference():
        theme = auth_store.get_theme_preference()
        ui.run_javascript(f"if ('{theme}' === 'dark') {{ document.body.classList.add('dark'); }} else {{ document.body.classList.remove('dark'); }}")
    set_theme(theme)
    theme_emoji = '☀️' if current_theme == 'light' else '🌙'
    with ui.row().classes('justify-between items-center w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-800 text-white dark:bg-gradient-to-r dark:from-gray-900 dark:to-gray-800 dark:text-white'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('format_quote').classes('text-3xl dark:text-white')
            ui.label('Quotes Application').classes('text-2xl font-bold tracking-tight dark:text-white')
        with ui.row().classes('items-center gap-2'):
            theme_btn = ui.button(theme_emoji)
            async def toggle_theme():
                new_theme = await ui.run_javascript(set_theme_js())
                set_theme(new_theme)
                theme_btn.text = '☀️' if new_theme == 'light' else '🌙'
                if auth_store.is_authenticated:
                    try:
                        await asyncio.to_thread(auth_api.update_theme, new_theme)
                        auth_store.update_theme(new_theme)
                        ui.notify('Theme preference saved', type='positive')
                    except Exception as e:
                        ui.notify(f'Failed to save theme preference: {str(e)}', type='error')
            theme_btn.on('click', toggle_theme)
            theme_btn.classes('bg-white text-blue-800 rounded-full px-2 py-1 dark:bg-gray-700 dark:text-yellow-300')
            if auth_store.is_authenticated:
                ui.label(f"Hello, {auth_store.get_user_name()}").classes('font-semibold text-white text-base dark:text-yellow-200')
                ui.button('Logout', icon='logout', on_click=logout).classes('bg-blue-700 hover:bg-blue-900 text-white font-semibold px-4 py-2 rounded')
            else:
                ui.button('Login', on_click=lambda: login_dialog.open()).classes('bg-blue-700 hover:bg-blue-900 text-white font-semibold px-4 py-2 rounded')
                ui.button('Register', on_click=lambda: register_dialog.open()).classes('bg-green-600 hover:bg-green-800 text-white font-semibold px-4 py-2 rounded')


def render_tabs():
    tab_names = ['home', 'quotes', 'authors']
    if auth_store.is_authenticated:
        tab_names.append('manage')
        tab_names.append('myquotes')
    tab_labels = {
        'home': ('Home', 'home'),
        'quotes': ('Quotes', 'format_quote'),
        'authors': ('Authors', 'person'),
        'manage': ('Manage', 'settings'),
        'myquotes': ('My Quotes', 'favorite'),
    }
    def on_tab_change(e):
        global current_tab
        try:
            current_tab = e.value
            render_content()
        except Exception as e:
            print(f"Error changing tab: {e}")
            try:
                render_content()
            except:
                pass
    with ui.tabs(value=current_tab, on_change=on_tab_change).classes('w-full bg-gray-100 px-6 pt-2 dark:bg-gray-800') as tabs:
        globals()['tabs_container'] = tabs
        for name in tab_names:
            label, icon = tab_labels[name]
            ui.tab(name, label=label, icon=icon)


def render_content():
    try:
        if content_container is not None:
            content_container.clear()
    except Exception as e:
        print(f"Warning: Could not clear content container: {e}")
    if current_tab == 'home':
        render_home()
    elif current_tab == 'quotes':
        render_quotes()
    elif current_tab == 'authors':
        render_authors()
    elif current_tab == 'manage':
        render_manage()
    elif current_tab == 'myquotes':
        render_myquotes()


def update_quote_list():
    """Clear and re-populate the quote list container based on current filters."""
    if quote_list_container is None:
        return

    quote_list_container.clear()
    with quote_list_container:
        if quotes_store.loading:
            ui.spinner('dots').classes('text-2xl')
            return

        # Apply author filter first
        display_quotes = quotes_store.quotes
        if quotes_store.author_filter:
            with ui.row().classes('w-full mb-2 gap-2 items-center'):
                ui.label(f"Filtered by author: {quotes_store.author_filter}").classes('text-sm font-semibold')
                ui.button('Clear', on_click=clear_author_filter, icon='close').classes('text-xs')
            display_quotes = quotes_store.get_quotes_by_author(quotes_store.author_filter)

        # Apply search query on top of the (potentially filtered) list
        if search_query:
            query_lower = search_query.lower()
            if search_by == 'all':
                display_quotes = [q for q in display_quotes if query_lower in q.get('quote', '').lower() or query_lower in q.get('author', '').lower() or any(query_lower in t.lower() for t in (q.get('tags') or []))]
            elif search_by == 'quote':
                display_quotes = [q for q in display_quotes if query_lower in q.get('quote', '').lower()]
            elif search_by == 'author':
                display_quotes = [q for q in display_quotes if query_lower in q.get('author', '').lower()]
            elif search_by == 'tags':
                display_quotes = [q for q in display_quotes if any(query_lower in t.lower() for t in (q.get('tags') or []))]

        if display_quotes:
            for quote in display_quotes:
                render_quote_card(quote)
        else:
            ui.label('No quotes found').classes('text-gray-500')


def render_home():
    with content_container:
        if quotes_store.quote_of_the_day:
            with ui.card().classes('w-full max-w-2xl mx-auto mb-8 bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg dark:bg-gradient-to-r dark:from-gray-900 dark:to-gray-800 dark:text-white'):
                with ui.column().classes('w-full text-center items-center'):
                    ui.label('Quote of the Day').classes('text-xl font-bold mb-2')
                    ui.label(f'"{quotes_store.quote_of_the_day.get("quote", "")}"').classes('text-lg mb-1')
                    ui.label(f'— {quotes_store.quote_of_the_day.get("author", "Unknown")}').classes('text-sm opacity-90 mb-2')


def render_quotes():
    global quote_list_container
    with content_container:
        # Search and filter UI (will not be cleared on search)
        with ui.row().classes('w-full mb-4 gap-2 items-center'):
            search_input_id = 'search-input-quotes'
            search_filter_id = 'search-filter-quotes'
            search_input = ui.input(
                placeholder='Search quotes...',
                value=search_query,
                on_change=lambda e: handle_search(e.value, search_by)
            ).classes('flex-grow rounded-lg px-4 py-2 bg-white text-gray-900 dark:!bg-gray-700 dark:!text-white dark:placeholder-gray-400 border border-gray-300 dark:!border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500').props(f'id={search_input_id}')

            with search_input:
                pass

            filter_options = {'all': 'All', 'quote': 'Quote', 'author': 'Author', 'tags': 'Tags'}
            search_filter = ui.select(
                options=filter_options,
                value=search_by if search_by in filter_options else 'all',
                on_change=lambda e: handle_search(search_query, e.value)
            ).classes('w-28 ml-2 rounded-lg px-3 py-2 bg-white text-gray-900 dark:!bg-gray-700 dark:!text-white border border-gray-300 dark:!border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500').props(f'id={search_filter_id}')

            # Force dark mode styling with JavaScript if theme is dark
            if current_theme == 'dark':
                ui.run_javascript(f'''
                    document.getElementById('{search_input_id}').style.backgroundColor = '#374151';
                    document.getElementById('{search_input_id}').style.color = 'white';
                    document.getElementById('{search_filter_id}').style.backgroundColor = '#374151';
                    document.getElementById('{search_filter_id}').style.color = 'white';
                ''')
                ui.add_head_html('''
                    <style>
                        .dark select option {
                            background-color: #374151 !important;
                            color: white !important;
                        }
                        .dark input::placeholder {
                            color: #9ca3af !important;
                        }
                    </style>
                ''')
        
        # Container for the list of quotes (will be cleared and updated)
        quote_list_container = ui.column().classes('w-full')
        update_quote_list()


def render_authors():
    with content_container:
        ui.label('All Authors').classes('text-xl font-bold mb-4 dark:text-white')
        authors = quotes_store.get_authors()
        if authors:
            with ui.grid(columns=3).classes('gap-4'):
                for author in authors:
                    author_quotes = quotes_store.get_quotes_by_author(author)
                    with ui.card().classes('w-full bg-white shadow cursor-pointer hover:shadow-lg transition dark:!bg-gray-800 dark:!border-gray-600 dark:!text-white dark:shadow-lg'):
                        with ui.row().classes('w-full justify-between items-center'):
                            ui.label(author).classes('text-lg font-medium dark:text-white')
                            ui.badge(f'{len(author_quotes)} quotes').classes('bg-blue-100 text-blue-800 dark:bg-gray-700 dark:text-yellow-200')
        else:
            ui.label('No authors found').classes('text-gray-500 dark:text-gray-400')


def render_manage():
    with content_container:
        if not auth_store.is_authenticated:
            ui.label('Please login to manage your quotes').classes('text-gray-500')
            return
        
        # Add "Add New Quote" button here
        ui.button('Add New Quote', icon='add', on_click=lambda: new_quote_dialog.open()).classes('mb-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded self-start')

        my_quotes = quotes_store.get_my_quotes(auth_store.get_user_id())
        ui.label('My Quotes').classes('text-xl font-bold mb-4')
        if my_quotes:
            for quote in my_quotes:
                render_quote_card(quote)
        else:
            ui.label('You haven\'t added any quotes yet').classes('text-gray-500')


def render_quote_card(quote):
    with ui.card().classes('w-full max-w-2xl mx-auto mb-4 bg-white shadow border border-gray-200 dark:!bg-gray-900 dark:!border-gray-800 dark:!text-white'):
        with ui.column().classes('w-full text-center items-center'):
            ui.label(f'"{quote.get("quote", "")}"').classes('text-lg font-medium mb-2 text-gray-900 dark:text-white')
            ui.label(f'— {quote.get("author", "Unknown")}').classes('text-sm text-gray-600 mb-2 dark:text-gray-300')
            if quote.get('tags'):
                tags = quote['tags'].split(',')
                with ui.row().classes('flex-wrap gap-1 mb-2 justify-center'):
                    for tag in tags:
                        if tag.strip():
                            ui.label(tag.strip()).classes('inline-block px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 text-xs font-semibold mr-1 dark:bg-gray-700 dark:text-yellow-200')
            if quote.get('user_name'):
                ui.label(f'Added by {quote["user_name"]}').classes('text-xs text-gray-500 mb-2 dark:text-gray-400')
            with ui.row().classes('w-full justify-center items-center gap-4'):
                with ui.row().classes('gap-2'):
                    is_own_quote = auth_store.is_authenticated and quote.get('user_id') == auth_store.get_user_id()
                    if current_tab == 'manage':
                        ui.icon('thumb_up').classes('text-green-800')
                        ui.label(str(quote.get('likes', 0))).classes('text-sm')
                        ui.icon('thumb_down').classes('text-red-800')
                        ui.label(str(quote.get('dislikes', 0))).classes('text-sm')
                    else:
                        if is_own_quote:
                            ui.icon('thumb_up').classes('text-green-800')
                            ui.label(str(quote.get('likes', 0))).classes('text-sm')
                            ui.icon('thumb_down').classes('text-red-800')
                            ui.label(str(quote.get('dislikes', 0))).classes('text-sm')
                        else:
                            ui.button(icon='thumb_up', on_click=lambda qid=quote['_id']: handle_like_quote(qid)).classes('bg-green-100 hover:bg-green-200 text-green-800 rounded dark:bg-green-900 dark:text-green-200')
                            ui.label(str(quote.get('likes', 0))).classes('text-sm')
                            ui.button(icon='thumb_down', on_click=lambda qid=quote['_id']: handle_dislike_quote(qid)).classes('bg-red-100 hover:bg-red-200 text-red-800 rounded dark:bg-red-900 dark:text-red-200')
                            ui.label(str(quote.get('dislikes', 0))).classes('text-sm')
                if current_tab == 'manage' and auth_store.is_authenticated and quote.get('user_id') == auth_store.get_user_id():
                    with ui.row().classes('gap-2'):
                        ui.button(icon='edit', on_click=lambda q=quote: open_edit_dialog(q)).classes('bg-blue-100 hover:bg-blue-200 text-blue-800 rounded dark:bg-blue-900 dark:text-blue-200')
                        ui.button(icon='delete', on_click=lambda qid=quote['_id']: open_delete_dialog(qid)).classes('bg-red-100 hover:bg-red-200 text-red-800 rounded dark:bg-red-900 dark:text-red-200')

def render_myquotes():
    global myquotes_subtab
    with content_container:
        if not auth_store.is_authenticated:
            ui.label('Please login to view your quotes').classes('text-gray-500')
            return
        user_id = auth_store.get_user_id()
        my_quotes = quotes_store.get_my_quotes(user_id)
        liked_quotes = quotes_store.get_liked_quotes()
        disliked_quotes = [q for q in quotes_store.quotes if q.get('is_disliked', False)]
        def on_subtab_change(e):
            global myquotes_subtab
            myquotes_subtab = e.value
            render_content()  # re-render to update content
        with ui.tabs(value=myquotes_subtab, on_change=on_subtab_change).classes('mb-4'):
            ui.tab('my', label=f'My Quotes ({len(my_quotes)})', icon='person')
            ui.tab('liked', label=f'Liked Quotes ({len(liked_quotes)})', icon='thumb_up')
            ui.tab('disliked', label=f'Disliked Quotes ({len(disliked_quotes)})', icon='thumb_down')
        if myquotes_subtab == 'my':
            ui.label('My Quotes').classes('text-xl font-bold mb-4')
            if my_quotes:
                for quote in my_quotes:
                    render_quote_card(quote)
            else:
                ui.label("You haven't created any quotes yet").classes('text-gray-500')
        elif myquotes_subtab == 'liked':
            ui.label('Liked Quotes').classes('text-xl font-bold mb-4')
            if liked_quotes:
                for quote in liked_quotes:
                    render_quote_card(quote)
            else:
                ui.label("You haven't liked any quotes yet").classes('text-gray-500')
        elif myquotes_subtab == 'disliked':
            ui.label('Disliked Quotes').classes('text-xl font-bold mb-4')
            if disliked_quotes:
                for quote in disliked_quotes:
                    render_quote_card(quote)
            else:
                ui.label("You haven't disliked any quotes yet").classes('text-gray-500')

# --- Character Counter Functions ---
def update_nq_char_count():
    """Update character count for new quote dialog"""
    global nq_quote, nq_char_count
    try:
        remaining = 300 - len(nq_quote.value)
        nq_char_count.text = f'{remaining} characters remaining'
        if remaining < 0:
            nq_char_count.classes('text-red-500 dark:text-red-400')
        else:
            nq_char_count.classes('text-gray-500 dark:text-gray-400')
        print(f"New quote char count updated: {remaining} remaining")
    except Exception as e:
        print(f"Error updating new quote char count: {e}")

def update_eq_char_count():
    """Update character count for edit quote dialog"""
    global eq_quote, eq_char_count
    try:
        remaining = 300 - len(eq_quote.value)
        eq_char_count.text = f'{remaining} characters remaining'
        if remaining < 0:
            eq_char_count.classes('text-red-500 dark:text-red-400')
        else:
            eq_char_count.classes('text-gray-500 dark:text-gray-400')
        print(f"Edit quote char count updated: {remaining} remaining")
    except Exception as e:
        print(f"Error updating edit quote char count: {e}")

# --- Dialogs ---
def setup_dialogs():
    global login_dialog, register_dialog, new_quote_dialog, edit_quote_dialog, delete_quote_dialog
    global login_email, login_password, remember_checkbox, reg_name, reg_email, reg_password
    global nq_quote, nq_author, nq_tags, eq_quote, eq_author, eq_tags
    global nq_char_count, eq_char_count
    
    # Login Dialog
    login_dialog = ui.dialog()
    with login_dialog:
        with ui.card().classes('w-96 dark:bg-gray-800 dark:text-white'):
            ui.label('Login').classes('text-2xl font-bold mb-4')
            login_email = ui.input('Email').classes('w-full mb-4 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400')
            login_password = ui.input('Password', password=True).classes('w-full mb-4 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400')
            remember_checkbox = ui.checkbox('Remember me')
            with ui.row().classes('w-full justify-between'):
                ui.button('Cancel', on_click=login_dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                ui.button('Login', on_click=lambda: handle_login(login_email.value, login_password.value, remember_checkbox.value, login_dialog)).classes('bg-blue-600 hover:bg-blue-700')
    # Register Dialog
    register_dialog = ui.dialog()
    with register_dialog:
        with ui.card().classes('w-96 dark:bg-gray-800 dark:text-white'):
            ui.label('Create Account').classes('text-2xl font-bold mb-4')
            reg_name = ui.input('Name').classes('w-full mb-4 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400')
            reg_email = ui.input('Email').classes('w-full mb-4 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400')
            reg_password = ui.input('Password', password=True).classes('w-full mb-4 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400')
            with ui.row().classes('w-full justify-between'):
                ui.button('Cancel', on_click=register_dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                ui.button('Register', on_click=lambda: handle_register(reg_name.value, reg_email.value, reg_password.value, register_dialog)).classes('bg-green-600 hover:bg-green-700')
    # New Quote Dialog
    new_quote_dialog = ui.dialog()
    with new_quote_dialog:
        with ui.card().classes('w-96 dark:bg-gray-800 dark:text-white'):
            ui.label('Add New Quote').classes('text-2xl font-bold mb-4 dark:text-white')
            
            # Quote textarea with character limit
            nq_quote = ui.textarea('Quote').classes('w-full mb-2 h-32 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400').props('maxlength=300')
            nq_char_count = ui.label('300 characters remaining').classes('text-sm text-gray-500 dark:text-gray-400 mb-4')
            
            # Bind the character counter update
            nq_quote.on('update:model-value', update_nq_char_count)
            
            nq_author = ui.input('Author').classes('w-full mb-4 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400')
            nq_tags = ui.input('Tags (comma separated)').classes('w-full mb-4 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400')
            with ui.row().classes('w-full justify-between'):
                ui.button('Cancel', on_click=new_quote_dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                ui.button('Add Quote', on_click=lambda: handle_create_quote(nq_quote.value, nq_author.value, nq_tags.value, new_quote_dialog)).classes('bg-blue-600 hover:bg-blue-700')
    # Edit Quote Dialog
    edit_quote_dialog = ui.dialog()
    with edit_quote_dialog:
        with ui.card().classes('w-96 dark:bg-gray-800 dark:text-white'):
            ui.label('Edit Quote').classes('text-2xl font-bold mb-4 dark:text-white')
            
            # Quote textarea with character limit
            eq_quote = ui.textarea('Quote').classes('w-full mb-2 h-32 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400').props('maxlength=300')
            eq_char_count = ui.label('300 characters remaining').classes('text-sm text-gray-500 dark:text-gray-400 mb-4')
            
            # Bind the character counter update
            eq_quote.on('update:model-value', update_eq_char_count)
            
            eq_author = ui.input('Author').classes('w-full mb-4 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400')
            eq_tags = ui.input('Tags (comma separated)').classes('w-full mb-4 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400')
            with ui.row().classes('w-full justify-between'):
                ui.button('Cancel', on_click=edit_quote_dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                ui.button('Update Quote', on_click=lambda: handle_update_quote(eq_quote.value, eq_author.value, eq_tags.value, edit_quote_dialog)).classes('bg-blue-600 hover:bg-blue-700')
    # Delete Quote Dialog
    delete_quote_dialog = ui.dialog()
    with delete_quote_dialog:
        with ui.card().classes('w-96 dark:bg-gray-800 dark:text-white'):
            ui.label('Delete Quote').classes('text-2xl font-bold mb-4')
            ui.label('Are you sure you want to delete this quote? This action cannot be undone.').classes('mb-4')
            with ui.row().classes('w-full justify-between'):
                ui.button('Cancel', on_click=delete_quote_dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                ui.button('Delete', on_click=lambda: handle_delete_quote(delete_quote_dialog)).classes('bg-red-600 hover:bg-red-700')

# --- Dialog Openers ---
def open_edit_dialog(quote):
    global editing_quote
    try:
        editing_quote = quote
        # Set dialog values using stored references
        eq_quote.value = quote.get('quote', '')
        eq_author.value = quote.get('author', '')
        
        # Handle tags properly - they might be a list or already a string
        tags = quote.get('tags', [])
        if isinstance(tags, list):
            eq_tags.value = ', '.join(tags)
        elif isinstance(tags, str):
            eq_tags.value = tags
        else:
            eq_tags.value = ''
        
        # Update character counter for existing text
        remaining = 300 - len(eq_quote.value)
        eq_char_count.text = f'{remaining} characters remaining'
        if remaining < 0:
            eq_char_count.classes('text-red-500 dark:text-red-400')
        else:
            eq_char_count.classes('text-gray-500 dark:text-gray-400')
        
        edit_quote_dialog.open()
        ui.notify('Edit dialog opened', type='info')
    except Exception as e:
        ui.notify(f'Error opening edit dialog: {str(e)}', type='error')
        print(f"Error in open_edit_dialog: {e}")

def open_delete_dialog(quote_id):
    global delete_quote_id
    delete_quote_id = quote_id
    delete_quote_dialog.open()

# --- API Handlers ---
async def handle_login(email, password, remember_me, dialog):
    try:
        response = await asyncio.to_thread(auth_api.login, email, password)
        if response.get('access_token') and response.get('user'):
            auth_store.login(response['user'], response['access_token'], remember_me)
            api_client.set_token(response['access_token'])
            dialog.close()
            ui.notify('Successfully logged in!', type='positive')
            header_container.clear(); 
            with header_container: render_header()
            tabs_container.clear(); 
            with tabs_container: render_tabs()
            render_content()
        else:
            ui.notify('Invalid response from server', type='error')
    except Exception as e:
        ui.notify(f'Login failed: {str(e)}', type='error')

async def handle_register(name, email, password, dialog):
    try:
        await asyncio.to_thread(auth_api.register, name, email, password)
        dialog.close()
        ui.notify('Account created successfully! Please login.', type='positive')
        login_dialog.open()
    except Exception as e:
        ui.notify(f'Registration failed: {str(e)}', type='error')

def logout():
    global current_tab
    auth_store.logout()
    api_client.clear_token()
    ui.notify('Logged out successfully', type='positive')
    
    # Update header and tabs
    header_container.clear(); 
    with header_container: render_header()
    tabs_container.clear(); 
    with tabs_container: render_tabs()
    
    # Redirect to home page
    current_tab = 'home'
    tabs_container.set_value('home')
    render_content()
    initialize_theme()  # Set theme for guest

async def handle_create_quote(quote_text, author, tags, dialog):
    try:
        new_quote = await asyncio.to_thread(quotes_api.create_quote, quote_text, author, tags)
        quotes_store.add_quote(new_quote)
        dialog.close()
        ui.notify('Quote created successfully!', type='positive')
        render_content()
    except Exception as e:
        ui.notify(f'Failed to create quote: {str(e)}', type='error')

async def handle_update_quote(quote_text, author, tags, dialog):
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
            render_content()
    except Exception as e:
        ui.notify(f'Failed to update quote: {str(e)}', type='error')

async def handle_delete_quote(dialog):
    try:
        if delete_quote_id:
            await asyncio.to_thread(quotes_api.delete_quote, delete_quote_id)
            quotes_store.remove_quote(delete_quote_id)
            dialog.close()
            ui.notify('Quote deleted successfully!', type='positive')
            render_content()
    except Exception as e:
        ui.notify(f'Failed to delete quote: {str(e)}', type='error')

async def handle_like_quote(quote_id):
    try:
        if not auth_store.is_authenticated:
            ui.notify('Please login to like quotes', type='warning')
            return
        quote = quotes_store.get_quote_by_id(quote_id)
        user_id = auth_store.get_user_id()
        if quote and quote.get('user_id') == user_id:
            ui.notify('You cannot like your own quote.', type='warning')
            return
        await asyncio.to_thread(quotes_api.like_quote, quote_id)
        await load_quotes()  # Refetch all quotes
        ui.notify('Quote liked!', type='positive')
        refresh_ui()
    except Exception as e:
        ui.notify(f'Failed to like quote: {str(e)}', type='error')

async def handle_dislike_quote(quote_id):
    try:
        if not auth_store.is_authenticated:
            ui.notify('Please login to dislike quotes', type='warning')
            return
        quote = quotes_store.get_quote_by_id(quote_id)
        user_id = auth_store.get_user_id()
        if quote and quote.get('user_id') == user_id:
            ui.notify('You cannot dislike your own quote.', type='warning')
            return
        await asyncio.to_thread(quotes_api.dislike_quote, quote_id)
        await load_quotes()  # Refetch all quotes
        ui.notify('Quote disliked!', type='positive')
        refresh_ui()
    except Exception as e:
        ui.notify(f'Failed to dislike quote: {str(e)}', type='error')

def handle_search(query: str, search_by_filter: str):
    global search_query, search_by
    search_query = query
    search_by = search_by_filter
    update_quote_list()

def clear_author_filter():
    """Clear the author filter and update the list."""
    quotes_store.set_author_filter(None)
    update_quote_list()

# --- Theme Management ---
def set_theme(theme: str):
    global current_theme
    current_theme = theme
    # Set body background and border directly for true edge-to-edge dark mode
    if theme == 'dark':
        ui.run_javascript("document.body.style.background = '#111827'; document.body.style.border = 'none'; document.body.style.margin = '0'; document.body.style.padding = '0';")
        # Force dark mode styling for search elements
        ui.run_javascript('''
            const searchInput = document.getElementById('search-input-quotes');
            const searchFilter = document.getElementById('search-filter-quotes');
            if (searchInput) {
                searchInput.style.backgroundColor = '#374151';
                searchInput.style.color = 'white';
            }
            if (searchFilter) {
                searchFilter.style.backgroundColor = '#374151';
                searchFilter.style.color = 'white';
            }
        ''')
        # Add dark mode CSS for form elements
        ui.add_head_html('''
            <style>
                .dark select option {
                    background-color: #374151 !important;
                    color: white !important;
                }
                .dark input::placeholder {
                    color: #9ca3af !important;
                }
                .dark select {
                    background-color: #374151 !important;
                    color: white !important;
                }
                /* Dark mode dialog styling */
                .dark .q-card {
                    color: white !important;
                }
                .dark .q-card * {
                    color: white !important;
                }
                .dark .q-card label {
                    color: white !important;
                }
                .dark .q-card input {
                    color: white !important;
                }
                .dark .q-card textarea {
                    color: white !important;
                }
            </style>
        ''')
    else:
        ui.run_javascript("document.body.style.background = '#f3f4f6'; document.body.style.border = 'none'; document.body.style.margin = '0'; document.body.style.padding = '0';")
        # Reset to light mode styling for search elements
        ui.run_javascript('''
            const searchInput = document.getElementById('search-input-quotes');
            const searchFilter = document.getElementById('search-filter-quotes');
            if (searchInput) {
                searchInput.style.backgroundColor = 'white';
                searchInput.style.color = '#111827';
            }
            if (searchFilter) {
                searchFilter.style.backgroundColor = 'white';
                searchFilter.style.color = '#111827';
            }
        ''')

# --- On App Start: Set initial theme ---
def initialize_theme():
    if auth_store.is_authenticated and auth_store.get_theme_preference():
        set_theme(auth_store.get_theme_preference())
    else:
        set_theme('light')
    # Inject comprehensive CSS into the head to force body background and border immediately
    css = '''
        html, body {
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            overflow-x: hidden !important;
        }
        body {
            background: #f3f4f6 !important;
        }
        body.dark {
            background: #111827 !important;
        }
        .nicegui-content {
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
        }
        .nicegui-content > * {
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
        }
        #__nicegui {
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
        }
        #__nicegui > * {
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
        }
        /* Remove any default NiceGUI borders */
        .q-page, .q-layout, .q-header, .q-footer {
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Dark mode form elements */
        .dark select option {
            background-color: #374151 !important;
            color: white !important;
        }
        .dark input::placeholder {
            color: #9ca3af !important;
        }
        .dark select {
            background-color: #374151 !important;
            color: white !important;
        }
    '''
    ui.add_head_html(f'<style>{css}</style>')

# --- Main Page ---
@ui.page('/')
def main():
    global header_container, tabs_container, content_container
    
    # Validate stored token and initialize API client
    asyncio.create_task(validate_stored_token())
    
    # Add comprehensive CSS to remove all borders and margins
    ui.add_head_html('''
        <style>
            html, body {
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
                overflow-x: hidden !important;
            }
            body {
                background: #f3f4f6 !important;
            }
            body.dark {
                background: #111827 !important;
            }
            .nicegui-content {
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
            }
            .nicegui-content > * {
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
            }
            #__nicegui {
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
            }
            #__nicegui > * {
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
            }
            * {
                box-sizing: border-box;
            }
            /* Remove any default NiceGUI borders */
            .q-page, .q-layout, .q-header, .q-footer {
                border: none !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            /* Dark mode form elements */
            .dark select option {
                background-color: #374151 !important;
                color: white !important;
            }
            .dark input::placeholder {
                color: #9ca3af !important;
            }
            .dark select {
                background-color: #374151 !important;
                color: white !important;
            }
            /* Dark mode dialog styling */
            .dark .q-card {
                color: white !important;
            }
            .dark .q-card * {
                color: white !important;
            }
            .dark .q-card label {
                color: white !important;
            }
            .dark .q-card input {
                color: white !important;
            }
            .dark .q-card textarea {
                color: white !important;
            }
        </style>
    ''')
    
    # Wrap the entire page in a full-width, full-height column with no margins or padding
    with ui.column().classes('min-h-screen w-full bg-gray-100 dark:bg-gray-900 dark:text-white m-0 p-0 border-0'):
        header_container = ui.row().classes('w-full')
        tabs_container = ui.row().classes('w-full')
        with header_container:
            render_header()
        with tabs_container:
            render_tabs()
        # Remove bg-white/shadow/rounded from content_container for seamless dark mode
        content_container = ui.column().classes('w-full max-w-3xl mx-auto py-8')
        setup_dialogs()
        
        # Wait for token validation to complete before loading data and rendering
        async def initialize_app():
            await validate_stored_token()
            # Refresh UI after token validation
            render_content()
            # Load quotes after authentication is confirmed
            await load_quotes()
        
        asyncio.create_task(initialize_app())
        initialize_theme()  # Set initial theme

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='Quotes Application',
        port=3001,
        reload=True,
        show=True
    ) 