# Pe Viitor - Job Scraping API
![Pe Viitor logo](https://peviitor.ro/static/media/peviitor_logo.df4cd2d4b04f25a93757bb59b397e656.svg)

**A comprehensive Django REST API for managing job scrapers, companies, and job listings with real-time search capabilities.**

Pe Viitor is a robust web service designed to automate job data collection from various websites and provide powerful search and filtering capabilities. The platform allows you to manage job scrapers, track companies, and serve job data through a modern REST API with real-time search powered by Apache Solr.

## ✨ Features

### 🏢 Company Management
- Create, update, and delete company profiles
- Track company job statistics and historical data
- Link companies to their data sources and scrapers
- Company-specific job clearing and synchronization

### 💼 Job Management
- Add jobs programmatically via scrapers or manual input
- Edit job details including location, remote options, and publication status
- Publish/unpublish jobs with automatic Solr search index updates
- Filter jobs by company, location, remote work options, and publication status
- Advanced job search with infinite scroll pagination

### 🤖 Scraper Management
- Support for Python and JavaScript scrapers
- Automated dependency installation (requirements.txt, package.json)
- Git repository integration for scraper code management
- Containerized scraper execution with Docker
- Scraper testing and validation framework
- Automatic updates from Git repositories

### 🔍 Real-time Search
- Apache Solr-powered job search engine
- Fast, full-text search across job titles, companies, and locations
- Advanced filtering by multiple criteria
- Optimized for high-performance queries

### 👥 User Management
- Custom user authentication with email-based login
- JWT token authentication for API access
- Role-based permissions (superuser, company-specific access)
- User-company and user-scraper associations

### 📱 Additional Features
- Real-time notifications via WebSockets (Django Channels)
- Newsletter subscription management
- Mobile API endpoints
- City/location management (orase module)
- Background task scheduling with APScheduler

## 🛠️ Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: MySQL/PostgreSQL with PyMySQL connector
- **Search Engine**: Apache Solr for real-time job search
- **Cache/Message Broker**: Redis for caching and WebSocket support
- **Real-time Features**: Django Channels with WebSocket support
- **Authentication**: JWT tokens with Django REST Framework SimpleJWT
- **Task Scheduling**: APScheduler for background jobs
- **Containerization**: Docker for scraper execution
- **Image Processing**: Pillow for company logos and images

## 🚀 Quick Setup

### Prerequisites

- Python 3.9+ 
- MySQL or PostgreSQL database
- Apache Solr instance
- Redis server (for real-time features)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/peviitor-ro/scraper_Api.git
cd scraper_Api/scraper_Api
```

### 2. Install Dependencies

#### Option A: Using System Packages (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y python3-django python3-djangorestframework python3-pymysql \
                    python3-dotenv python3-requests python3-pil python3-redis \
                    python3-channels python3-channels-redis
```

#### Option B: Using pip
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DEBUG=True
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306

# Solr Configuration
DATABASE_SOLR=http://localhost:8983
DATABASE_SOLR_USERNAME=your_solr_username
DATABASE_SOLR_PASSWORD=your_solr_password

# Email Configuration (for notifications)
EMAIL_HOST_USER=your_email@domain.com
EMAIL_HOST_PASSWORD=your_email_password

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

### 4. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create a superuser account
python manage.py createsuperuser
```

### 5. Start the Development Server

```bash
# Start the Django development server
python manage.py runserver

# The API will be available at http://localhost:8000
```

## 📖 API Documentation

### Authentication

The API uses JWT token authentication. First, obtain a token:

```bash
curl -X POST http://localhost:8000/get_token \
  -H "Content-Type: application/json" \
  -d '{"email": "your_email@domain.com", "password": "your_password"}'
```

Use the token in subsequent requests:
```bash
curl -H "Authorization: Bearer your_jwt_token" http://localhost:8000/endpoint
```

### 🏢 Company Endpoints

#### List Companies
```bash
curl -H "Authorization: Bearer your_jwt_token" \
  "http://localhost:8000/companies/"
```

#### Add a New Company
```bash
curl -X POST http://localhost:8000/companies/add/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tech Corp",
    "scname": "TechCorp",
    "website": "https://techcorp.com",
    "description": "Leading technology company"
  }'
```

#### Update Company
```bash
curl -X PUT http://localhost:8000/companies/update/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "company": "Updated Tech Corp",
    "website": "https://newtechcorp.com"
  }'
```

### 💼 Job Endpoints

#### Get Jobs with Filters
```bash
# Get all published jobs
curl -H "Authorization: Bearer your_jwt_token" \
  "http://localhost:8000/jobs/get/"

# Filter jobs by company
curl -H "Authorization: Bearer your_jwt_token" \
  "http://localhost:8000/jobs/get/?company=1"

# Filter jobs by city and remote options
curl -H "Authorization: Bearer your_jwt_token" \
  "http://localhost:8000/jobs/get/?city=Bucharest&remote=true"

# Pagination and sorting
curl -H "Authorization: Bearer your_jwt_token" \
  "http://localhost:8000/jobs/get/?page=1&limit=20&sort=created_date"
```

#### Add a Job
```bash
curl -X POST http://localhost:8000/jobs/add/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "company": 1,
    "job_title": "Python Developer",
    "job_link": "https://company.com/jobs/python-dev",
    "country": "Romania",
    "city": "Bucharest, Cluj-Napoca",
    "county": "Bucharest, Cluj",
    "remote": "hybrid, full-remote"
  }'
```

#### Publish/Unpublish Job
```bash
# Publish job (makes it searchable)
curl -X POST http://localhost:8000/jobs/publish/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"job_id": 123}'
```

#### Synchronize Company Jobs
```bash
# Sync all jobs for a company with Solr search index
curl -X POST http://localhost:8000/jobs/sync/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"company": 1}'
```

### 🤖 Scraper Endpoints

#### Add a Scraper Repository
```bash
curl -X POST http://localhost:8000/scraper/add/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/username/job-scraper.git"}'
```

#### List Scraper Files
```bash
# List files in a scraper repository
curl -H "Authorization: Bearer your_jwt_token" \
  "http://localhost:8000/scraper/your-repo-name/"
```

#### Run a Scraper
```bash
# Run a specific scraper file
curl -X POST http://localhost:8000/scraper/your-repo-name/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"file": "scraper.py"}'

# Force run a scraper (ignore recent runs)
curl -X POST http://localhost:8000/scraper/your-repo-name/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"file": "scraper.py", "force": "true"}'
```

#### Update Scraper Repository
```bash
# Pull latest changes from Git
curl -X POST http://localhost:8000/scraper/your-repo-name/ \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"update": "true"}'
```

### Python API Examples

```python
import requests

# Configuration
API_BASE = "http://localhost:8000"
TOKEN = "your_jwt_token"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Get companies
response = requests.get(f"{API_BASE}/companies/", headers=HEADERS)
companies = response.json()

# Add a new job
job_data = {
    "company": 1,
    "job_title": "Senior Django Developer",
    "job_link": "https://example.com/job/123",
    "country": "Romania",
    "city": "Bucharest",
    "county": "Bucharest",
    "remote": "hybrid"
}
response = requests.post(f"{API_BASE}/jobs/add/", json=job_data, headers=HEADERS)

# Search jobs with filters
params = {
    "city": "Bucharest",
    "remote": "true",
    "company": 1,
    "page": 1,
    "limit": 20
}
response = requests.get(f"{API_BASE}/jobs/get/", params=params, headers=HEADERS)
jobs = response.json()

# Run a scraper
scraper_data = {"file": "companies/example_scraper.py"}
response = requests.post(
    f"{API_BASE}/scraper/example-repo/",
    json=scraper_data,
    headers=HEADERS
)
```

## 📁 Project Structure

```
scraper_Api/
├── scraper_Api/                 # Main Django project
│   ├── scraper_Api/            # Project settings and configuration
│   │   ├── settings.py         # Main settings
│   │   ├── test_settings.py    # Test-specific settings
│   │   ├── urls.py             # URL routing
│   │   └── wsgi.py/asgi.py     # WSGI/ASGI configuration
│   │
│   ├── company/                # Company management app
│   │   ├── models.py           # Company, Source, DataSet models
│   │   ├── views.py            # Company CRUD operations
│   │   ├── serializers.py      # API serializers
│   │   └── urls.py             # Company endpoints
│   │
│   ├── jobs/                   # Job management app
│   │   ├── models.py           # Job model with Solr integration
│   │   ├── views.py            # Job CRUD, search, publish operations
│   │   ├── serializer.py       # Job serializers
│   │   └── urls.py             # Job endpoints
│   │
│   ├── scraper/                # Scraper management app
│   │   ├── models.py           # Scraper model
│   │   ├── views.py            # Scraper execution and management
│   │   ├── utils/              # Scraper utilities
│   │   │   └── scraper.py      # Core scraper logic
│   │   └── urls.py             # Scraper endpoints
│   │
│   ├── users/                  # User management app
│   │   ├── models.py           # CustomUser model
│   │   ├── managers.py         # Custom user manager
│   │   ├── views.py            # Authentication endpoints
│   │   ├── middleware.py       # Rate limiting middleware
│   │   └── urls.py             # User/auth endpoints
│   │
│   ├── newsletter/             # Newsletter management
│   ├── mobile/                 # Mobile-specific endpoints
│   ├── notifications/          # Real-time notifications
│   ├── orase/                  # City/location management
│   ├── utils/                  # Shared utilities
│   │   └── pagination.py       # Custom pagination
│   │
│   ├── static/                 # Static files
│   ├── templates/              # Django templates
│   └── manage.py               # Django management script
│
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── README.md                   # This file
```

### Key Models

#### Company Model (`company/models.py`)
- **Company**: Main company entity with name, website, description
- **Source**: Data source tracking for companies
- **DataSet**: Historical job count data for companies

#### Job Model (`jobs/models.py`)
- **Job**: Core job entity with title, link, location, company relationship
- Integrates with Solr search engine for real-time search
- Supports publish/unpublish workflow
- Automatic ID generation using MD5 hash of job link

#### User Model (`users/models.py`)
- **CustomUser**: Extends Django's AbstractBaseUser
- Email-based authentication
- Many-to-many relationships with companies and scrapers
- Automatic superuser permissions for all companies/scrapers

#### Scraper Model (`scraper/models.py`)
- **Scraper**: Tracks scraper repositories and metadata
- Supports Python, JavaScript, and JMeter scripts
- Linked to users for access control

## 🔧 Development & Deployment

### Local Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pre-commit install

# Run with debug mode
export DEBUG=True
python manage.py runserver

# Access Django admin
http://localhost:8000/admin/
```

### Running with Docker (if available)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run scrapers in containers
docker run -it your-scraper-image python scraper.py
```

### Environment Configuration

#### Development (.env)
```env
DEBUG=True
DB_NAME=scraper_dev
DB_USER=dev_user
DB_PASSWORD=dev_password
DB_HOST=localhost
DATABASE_SOLR=http://localhost:8983
```

#### Production (.env)
```env
DEBUG=False
DB_NAME=scraper_prod
DB_USER=prod_user
DB_PASSWORD=secure_password
DB_HOST=your-db-host
DATABASE_SOLR=https://your-solr-host
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=secure_email_password
```

## 🧪 Testing

This project includes comprehensive automated tests for all Django apps to ensure code quality and prevent regressions.

### Running Tests Locally

#### Option 1: Using Django's built-in test runner

```bash
# Navigate to the project directory
cd scraper_Api

# Set the test settings
export DJANGO_SETTINGS_MODULE=scraper_Api.test_settings

# Run all tests
python manage.py test

# Run tests with verbose output
python manage.py test --verbosity=2

# Run specific app tests
python manage.py test scraper
python manage.py test users
python manage.py test company

# Run specific test classes
python manage.py test scraper.tests.ScraperModelTest
python manage.py test users.tests.CustomUserModelTest
```

#### Option 2: Using pytest

```bash
# Navigate to the project directory
cd scraper_Api

# Run all tests with pytest
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific tests
python -m pytest scraper/tests.py
python -m pytest users/tests.py -v
```

### Running Tests with Coverage

```bash
# Navigate to the project directory
cd scraper_Api

# Run tests with coverage measurement
export DJANGO_SETTINGS_MODULE=scraper_Api.test_settings
python -m coverage run --source='.' manage.py test

# Generate coverage report
python -m coverage report

# Generate HTML coverage report
python -m coverage html
# Open htmlcov/index.html in your browser

# Generate XML coverage report (for CI/CD)
python -m coverage xml
```

### Test Structure

The project includes tests for:

- **Models**: Validation, relationships, constraints, and business logic
- **Views**: API endpoints, authentication, and response handling  
- **Forms**: Data validation and processing
- **Managers**: Custom user management functionality
- **Middleware**: Rate limiting and request processing
- **Background tasks**: Newsletter sending and scheduled operations
- **WebSocket consumers**: Real-time notifications (when channels is available)

### Current Test Coverage

- **Overall**: 33% code coverage
- **Models**: 80%+ coverage on critical business logic
- **User Management**: 95% coverage
- **Job Models**: 81% coverage including Solr integration

### Test Configuration

Tests use a separate configuration (`scraper_Api.test_settings.py`) that:

- Uses SQLite in-memory database for speed
- Disables migrations for faster test execution
- Mocks external services (Solr, Redis, Email)
- Uses simplified authentication for testing
- Provides minimal URL configuration

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help improve Pe Viitor:

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/scraper_Api.git
   cd scraper_Api
   ```
3. **Create a virtual environment** and install dependencies
4. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Guidelines

#### Code Style

- Follow **PEP 8** for Python code style
- Use **meaningful variable and function names**
- Add **docstrings** to all functions and classes
- Keep functions small and focused on a single responsibility
- Use **type hints** where appropriate

#### Code Quality

```bash
# Run code formatting (if available)
black .
isort .

# Run linting
flake8 .
pylint your_app/

# Check for security issues
bandit -r .
```

#### Testing

- **Write tests** for all new features and bug fixes
- Ensure **test coverage** doesn't decrease
- All tests must pass before submitting a PR

```bash
# Run tests before committing
python manage.py test --settings=scraper_Api.test_settings

# Check test coverage
python -m coverage run --source='.' manage.py test
python -m coverage report
```

### Pull Request Process

1. **Update documentation** if you're changing APIs or adding features
2. **Update the README.md** if necessary
3. **Add tests** for new functionality
4. **Ensure all tests pass** and coverage is maintained
5. **Create a pull request** with:
   - Clear description of changes
   - Link to any related issues
   - Screenshots for UI changes
   - Updated documentation

### Types of Contributions

#### 🐛 Bug Reports
- Use the GitHub issue tracker
- Include detailed reproduction steps
- Provide environment details (OS, Python version, etc.)
- Include relevant error messages and logs

#### ✨ Feature Requests
- Check existing issues first
- Provide clear use case and rationale
- Include mockups or examples if applicable

#### 📖 Documentation
- Fix typos and improve clarity
- Add examples and tutorials
- Translate documentation
- Improve API documentation

#### 🔧 Code Contributions
- Fix bugs and implement features
- Improve performance
- Add tests and improve coverage
- Refactor and clean up code

### Coding Standards

#### Django Best Practices
- Use Django's built-in features (ORM, forms, admin)
- Follow Django naming conventions
- Use class-based views appropriately
- Implement proper error handling

#### API Design
- Follow RESTful principles
- Use appropriate HTTP status codes
- Implement consistent response formats
- Add proper validation and error messages

#### Database
- Write efficient queries
- Use database indexes appropriately
- Handle migrations carefully
- Document schema changes

### Development Setup for Contributors

```bash
# Fork and clone the repository
git clone https://github.com/your-username/scraper_Api.git
cd scraper_Api/scraper_Api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Set up pre-commit hooks
pre-commit install

# Create test database and run migrations
export DJANGO_SETTINGS_MODULE=scraper_Api.test_settings
python manage.py migrate

# Run tests to ensure everything works
python manage.py test
```

### Community Guidelines

- **Be respectful** and inclusive
- **Help others** learn and grow
- **Share knowledge** and experiences
- **Follow the code of conduct**

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

- ✅ **Commercial use** - Use for commercial purposes
- ✅ **Distribution** - Distribute the software
- ✅ **Modification** - Modify the source code
- ✅ **Private use** - Use privately
- ❗ **License and copyright notice** - Include license and copyright notice
- ❌ **Liability** - No warranty or liability
- ❌ **Warranty** - No warranty provided

```
MIT License

Copyright (c) 2023 peviitor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👥 Authors & Acknowledgments

### Pe Viitor Team

Our team is composed of specialists and education enthusiasts who aim to make a significant contribution in the field of job market transparency and accessibility.

- **[Pe Viitor Team](https://github.com/peviitor-ro)** - Core development team
- **Community Contributors** - Thank you to all our contributors!

### Special Thanks

- Django and Django REST Framework communities
- Apache Solr community
- All contributors who have helped improve this project

### Contact

- **Website**: [peviitor.ro](https://peviitor.ro)
- **GitHub**: [github.com/peviitor-ro](https://github.com/peviitor-ro)
- **Issues**: [GitHub Issues](https://github.com/peviitor-ro/scraper_Api/issues)

---

**Made with ❤️ by the Pe Viitor team**

We are dedicated to the continuous improvement and development of this project to provide the best resources for everyone interested in job market data and transparency.
