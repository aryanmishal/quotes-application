# Quotes Application - NiceGUI Frontend

A modern quotes management application built with **NiceGUI** (Python) frontend and **FastAPI** backend. This application allows users to browse, create, manage, and interact with quotes in a beautiful, responsive interface.

## 🏗️ Architecture

```
quote-system/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── auth.py         # Authentication logic
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # MongoDB connection
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   └── schemas/        # Pydantic schemas
│   └── requirements.txt    # Backend dependencies
└── nicegui-frontend/       # NiceGUI Frontend
    ├── app.py             # Main application
    ├── api_client.py      # API communication
    ├── auth_store.py      # Authentication state management
    ├── quotes_store.py    # Quotes data management
    ├── config.py          # Frontend configuration
    └── requirements.txt   # Frontend dependencies
```

## ✨ Features

### 🔐 Authentication
- **User Registration & Login**: Secure user account creation and authentication
- **Remember Me**: Persistent login sessions across browser sessions
- **JWT Token Management**: Automatic token validation and refresh
- **Theme Persistence**: User theme preferences saved per account

### 📚 Quotes Management
- **Browse Quotes**: View all quotes with pagination and filtering
- **Create Quotes**: Add new quotes with author and tags
- **Edit Quotes**: Modify existing quotes (for quote owners)
- **Delete Quotes**: Remove quotes (for quote owners)
- **Search & Filter**: Search by quote text, author, or tags
- **Quote of the Day**: Daily featured quote display

### 💬 Social Features
- **Like/Dislike System**: React to quotes with likes and dislikes
- **User Quotes**: View and manage your own quotes
- **Author Pages**: Browse quotes by specific authors

### 🎨 User Interface
- **Dark/Light Theme**: Toggle between themes with system-wide persistence
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, intuitive interface with smooth animations
- **Real-time Updates**: Live character counters and instant feedback

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB database
- Backend server running

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create `.env` file):
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=quotes_db
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

The backend will be available at `http://127.0.0.1:8000`

### Frontend Setup
1. Navigate to the NiceGUI frontend directory:
   ```bash
   cd nicegui-frontend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the API endpoint in `config.py`:
   ```python
   API_BASE_URL = "http://127.0.0.1:8000"
   ```

5. Start the NiceGUI application:
   ```bash
   python app.py
   ```

The frontend will be available at `http://127.0.0.1:3001`

## 📁 Project Structure

### Backend (`backend/`)
- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database for storing quotes and user data
- **JWT Authentication**: Secure token-based authentication
- **Pydantic**: Data validation and serialization
- **Motor**: Async MongoDB driver

### NiceGUI Frontend (`nicegui-frontend/`)

#### Core Files
- **`app.py`**: Main application entry point and UI components
- **`api_client.py`**: HTTP client for backend communication
- **`auth_store.py`**: Authentication state management
- **`quotes_store.py`**: Quotes data management and caching
- **`config.py`**: Application configuration

#### Key Components

**Authentication Store (`auth_store.py`)**
- Manages user authentication state
- Handles token storage and retrieval
- Supports "Remember Me" functionality
- Theme preference persistence

**API Client (`api_client.py`)**
- Centralized HTTP client for backend communication
- Automatic token management
- Error handling and response processing
- Supports all CRUD operations

**Quotes Store (`quotes_store.py`)**
- Local state management for quotes data
- Caching and filtering capabilities
- Search and pagination support
- Real-time data synchronization

## 🔧 Configuration

### Backend Configuration
The backend uses environment variables for configuration:
- `MONGODB_URL`: MongoDB connection string
- `DATABASE_NAME`: Database name
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Frontend Configuration
Edit `config.py` to customize:
- `API_BASE_URL`: Backend API endpoint
- Theme preferences
- Application settings

## 🎯 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/update-theme` - Update theme preference
- `GET /auth/me` - Get current user info

### Quotes
- `GET /quotes/` - Get all quotes
- `POST /quotes/` - Create new quote
- `GET /quotes/{id}/` - Get specific quote
- `PATCH /quotes/{id}/` - Update quote
- `DELETE /quotes/{id}/` - Delete quote
- `POST /quotes/{id}/likes/up` - Like quote
- `POST /quotes/{id}/dislike/up` - Dislike quote
- `GET /quotes/search/` - Search quotes

## 🎨 UI Features

### Theme System
- **Light Mode**: Clean, bright interface
- **Dark Mode**: Easy on the eyes, modern look
- **Automatic Persistence**: Theme preference saved per user
- **System Integration**: Respects user's system theme

### Responsive Design
- **Mobile-Friendly**: Optimized for touch devices
- **Desktop Optimized**: Full-featured desktop experience
- **Adaptive Layout**: Automatically adjusts to screen size

### User Experience
- **Real-time Feedback**: Instant notifications and updates
- **Character Counters**: Live feedback for text inputs
- **Loading States**: Visual feedback during operations
- **Error Handling**: User-friendly error messages

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password encryption
- **Token Validation**: Automatic token verification
- **Session Management**: Secure session handling
- **Input Validation**: Server-side data validation

## 🚀 Deployment

### Backend Deployment
1. Set up MongoDB database
2. Configure environment variables
3. Deploy using uvicorn or gunicorn
4. Set up reverse proxy (nginx recommended)

### Frontend Deployment
1. Install dependencies
2. Configure API endpoint
3. Run with NiceGUI's built-in server
4. For production, consider using a reverse proxy

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
The NiceGUI application can be tested manually through the web interface.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## 🔄 Updates

Stay updated with the latest features and bug fixes by regularly pulling from the main branch.

---

**Built with ❤️ using NiceGUI and FastAPI** 