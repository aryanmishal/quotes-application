# Quote System

A modern full-stack application for managing and sharing quotes, built with Next.js and FastAPI.

## Features

- **User Authentication**
  - Secure registration and login system
  - JWT-based authentication
  - Password hashing with bcrypt

- **Quote Management**
  - Create, read, update, and delete quotes
  - Add authors and tags to quotes
  - Automatic hashtag prefixing for tags
  - Search and filter quotes by author, content, or tags

- **Interactive Features**
  - Like/dislike functionality
  - User reaction tracking
  - View who liked/disliked quotes
  - Prevention of self-liking/disliking

- **Personalized Experience**
  - "My Quotes" section with three views:
    - My Uploaded Quotes
    - Liked Quotes
    - Disliked Quotes
  - Quote of the Day feature prioritizing:
    1. User's liked quotes
    2. User's uploaded quotes
    3. Random quotes
    - Prevents repetition from previous two days

- **Modern UI/UX**
  - Responsive design
  - Dark/Light theme support
  - Clean and intuitive interface
  - Real-time updates

## Tech Stack

### Frontend
- **Framework**: Next.js 15.3.3
- **UI Libraries**:
  - Radix UI components
  - Tailwind CSS
  - Shadcn UI
- **State Management**: Zustand
- **API Integration**: React Query
- **Form Handling**: React Hook Form with Zod validation

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT with python-jose
- **Password Hashing**: Passlib with bcrypt
- **API Documentation**: Swagger UI (automatic with FastAPI)

## Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB 4.4+

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   source venv/bin/activate     # Unix/macOS
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a .env file in the backend directory with:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DB_NAME=quotesAppv101
   SECRET_KEY=your-secret-key-here
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

1. Access the application at `http://localhost:3000`
2. Register a new account or login
3. Start creating and interacting with quotes
4. Use the search functionality to find specific quotes
5. Visit your profile to see your quotes and interactions

## API Documentation

Once the backend is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Running Tests
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest
```

### Code Style
- Frontend follows ESLint configuration
- Backend follows PEP 8 guidelines

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with modern web technologies
- Inspired by the need for a clean, user-friendly quote management system
- Thanks to all contributors and users of the application
