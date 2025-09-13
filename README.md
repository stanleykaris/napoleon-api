# Napoleon API

A gamified backend service that helps people reconnect with nature through quests. Designed for busy professionals (e.g., office workers), the app balances outdoor mini-adventures with indoor trivia challenges, while fostering partnerships with game parks and eco-organizations.

## Features

- **User Management**: User registration, authentication, and profile management
- **Quests & Challenges**: Create and manage outdoor and indoor challenges
- **Progress Tracking**: Track user progress through quests and challenges
- **Partner Organizations**: Manage partnerships with game parks and eco-organizations
- **Gamification**: Experience points, levels, and achievements

## Tech Stack

- **Backend**: Django REST Framework
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Storage**: Local file system (development), S3 compatible storage (production ready)

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtualenv (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/napoleon-api.git
   cd napoleon-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the API at http://localhost:8000/api/

## API Documentation

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. To authenticate your requests, include the following header:

```
Authorization: Bearer <your_access_token>
```

### Available Endpoints

- `POST /api/auth/token/` - Obtain JWT token (username & password required)
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `POST /api/auth/token/verify/` - Verify JWT token
- `GET /api/users/` - List all users (admin only)
- `POST /api/users/` - Register a new user
- `GET /api/users/me/` - Get current user profile
- `GET /api/quests/` - List all quests
- `GET /api/challenges/` - List all challenges
- `GET /api/partners/` - List partner organizations
- `GET /api/partnerships/` - List active partnerships

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Running Tests

```bash
python manage.py test
```

## Deployment

For production deployment, you'll need to set up:

1. A production-ready database (PostgreSQL recommended)
2. A production-ready web server (Gunicorn + Nginx recommended)
3. Environment variables for sensitive settings
4. SSL/TLS for secure connections

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
