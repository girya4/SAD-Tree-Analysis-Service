# Testing Guide - LCT Tree Analysis Service v2.3

## Overview

This document provides comprehensive information about the testing framework and CI/CD pipeline for the LCT Tree Analysis Service.

## Testing Framework

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── unit/                    # Unit tests
│   ├── test_models.py      # Database model tests
│   ├── test_services.py    # Service layer tests
│   └── test_auth.py        # Authentication tests
├── integration/             # Integration tests
│   ├── test_api_routes.py  # API endpoint tests
│   └── test_celery_tasks.py # Celery task tests
└── e2e/                     # End-to-end tests
    └── test_frontend.py     # Frontend E2E tests
```

### Test Categories

#### Unit Tests
- **Purpose**: Test individual components in isolation
- **Scope**: Models, services, utilities
- **Markers**: `@pytest.mark.unit`
- **Run**: `pytest tests/unit/ -m unit`

#### Integration Tests
- **Purpose**: Test component interactions
- **Scope**: API endpoints, database operations, Celery tasks
- **Markers**: `@pytest.mark.integration`
- **Run**: `pytest tests/integration/ -m integration`

#### End-to-End Tests
- **Purpose**: Test complete user workflows
- **Scope**: Frontend interactions, full application flow
- **Markers**: `@pytest.mark.e2e`
- **Run**: `pytest tests/e2e/ -m e2e`

## Running Tests

### Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

### Local Testing

#### Run All Tests
```bash
pytest tests/ -v
```

#### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# E2E tests only
pytest tests/e2e/ -v
```

#### Run Tests with Coverage
```bash
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
```

#### Run Tests by Markers
```bash
# Run only API tests
pytest -m api -v

# Run only slow tests
pytest -m slow -v

# Skip slow tests
pytest -m "not slow" -v
```

### Docker Testing

#### Run Tests in Docker
```bash
# Build and run all tests
docker-compose -f docker-compose.test.yml up --build

# Run only unit tests
docker-compose -f docker-compose.test.yml run test-backend pytest tests/unit/ -v

# Run only E2E tests
docker-compose -f docker-compose.test.yml run test-e2e
```

#### Test Environment Variables
```bash
export DATABASE_URL="postgresql://test_user:test_password@localhost:5433/test_db"
export REDIS_URL="redis://localhost:6380"
export SECRET_KEY="test-secret-key"
export TESTING="true"
```

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Continuous Integration (`ci.yml`)
- **Triggers**: Push to main/develop branches, pull requests
- **Jobs**:
  - **Test**: Unit, integration, and E2E tests
  - **Lint**: Code formatting and style checks
  - **Security**: Security vulnerability scanning
  - **Docker**: Container build and test

#### 2. Continuous Deployment (`cd.yml`)
- **Triggers**: Tag pushes, manual workflow dispatch
- **Jobs**:
  - **Build and Push**: Docker image building and registry push
  - **Deploy Staging**: Automated staging deployment
  - **Deploy Production**: Manual production deployment
  - **Rollback**: Automatic rollback on failure

#### 3. Security Scanning (`security.yml`)
- **Triggers**: Weekly schedule, push to main/develop
- **Jobs**:
  - **Dependency Scan**: Safety and Bandit security checks
  - **Container Scan**: Trivy vulnerability scanning
  - **Code Scan**: CodeQL static analysis

### Pipeline Stages

1. **Code Quality**
   - Black code formatting
   - isort import sorting
   - flake8 linting
   - mypy type checking

2. **Security**
   - Bandit security linting
   - Safety dependency checking
   - Trivy container scanning
   - CodeQL static analysis

3. **Testing**
   - Unit tests with coverage
   - Integration tests
   - End-to-end tests
   - Performance tests

4. **Build & Deploy**
   - Docker image building
   - Container registry push
   - Environment deployment
   - Smoke testing

## Test Configuration

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --asyncio-mode=auto
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    api: API tests
    frontend: Frontend tests
```

### Test Fixtures

#### Database Fixtures
- `db_session`: Fresh database session for each test
- `client`: FastAPI test client with database override
- `sample_task_data`: Sample task data for testing
- `sample_user_data`: Sample user data for testing

#### File Fixtures
- `temp_upload_dir`: Temporary directory for file uploads
- `sample_image_file`: Sample image file for testing

#### Mock Fixtures
- `mock_redis`: Mock Redis connection
- `mock_celery`: Mock Celery task

## Writing Tests

### Unit Test Example
```python
@pytest.mark.unit
def test_create_user(self, db_session):
    """Test creating a new user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.username == "testuser"
```

### Integration Test Example
```python
@pytest.mark.integration
@pytest.mark.api
def test_create_task_success(self, client, sample_image_file):
    """Test successful task creation."""
    files = {"file": ("test.jpg", sample_image_file, "image/jpeg")}
    response = client.post("/api/tasks", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "PENDING"
```

### E2E Test Example
```python
@pytest.mark.e2e
@pytest.mark.frontend
def test_file_upload_success(self, page: Page, sample_image_file):
    """Test successful file upload."""
    page.goto("http://localhost:8000")
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        tmp_file.write(sample_image_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        page.locator("#file-input").set_input_files(tmp_file_path)
        page.locator("#upload-btn").click()
        
        page.wait_for_selector("#upload-status", timeout=10000)
        upload_status = page.locator("#upload-status")
        assert upload_status.is_visible()
    finally:
        os.unlink(tmp_file_path)
```

## Best Practices

### Test Organization
1. **One test per functionality**: Each test should verify one specific behavior
2. **Descriptive names**: Test names should clearly describe what is being tested
3. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
4. **Independent tests**: Tests should not depend on each other

### Test Data
1. **Use fixtures**: Leverage pytest fixtures for common test data
2. **Mock external dependencies**: Use mocks for external services and APIs
3. **Clean up resources**: Ensure proper cleanup of temporary files and database state

### Performance
1. **Mark slow tests**: Use `@pytest.mark.slow` for tests that take >5 seconds
2. **Parallel execution**: Use `pytest-xdist` for parallel test execution
3. **Database optimization**: Use transactions for faster database tests

### Coverage
1. **Aim for 80%+ coverage**: Set minimum coverage threshold
2. **Focus on critical paths**: Prioritize testing business logic
3. **Exclude generated code**: Don't test auto-generated or trivial code

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database is running
docker-compose -f docker-compose.test.yml ps

# Reset test database
docker-compose -f docker-compose.test.yml down -v
docker-compose -f docker-compose.test.yml up -d test-db
```

#### Playwright Browser Issues
```bash
# Reinstall browsers
playwright install chromium

# Run with debug mode
pytest tests/e2e/ -v -s --headed
```

#### Coverage Issues
```bash
# Generate detailed coverage report
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Debug Mode
```bash
# Run tests with debug output
pytest tests/ -v -s --tb=long

# Run specific test with debug
pytest tests/unit/test_models.py::TestUserModel::test_create_user -v -s
```

## Continuous Integration

### Local CI Simulation
```bash
# Run all CI checks locally
make ci

# Individual checks
make lint
make test
make security
make docker-build
```

### GitHub Actions Debugging
1. Check workflow logs in GitHub Actions tab
2. Use `act` to run workflows locally
3. Enable debug logging with `ACTIONS_STEP_DEBUG=true`

## Deployment Testing

### Staging Environment
- Automated deployment on develop branch
- Smoke tests after deployment
- Performance monitoring

### Production Environment
- Manual deployment approval
- Blue-green deployment strategy
- Rollback capability on failure

## Monitoring and Metrics

### Test Metrics
- Test execution time
- Coverage percentage
- Flaky test detection
- Test failure trends

### Quality Gates
- Minimum 80% code coverage
- Zero critical security vulnerabilities
- All tests must pass
- Performance benchmarks met

## Contributing

### Adding New Tests
1. Follow the existing test structure
2. Use appropriate markers and fixtures
3. Write descriptive test names and docstrings
4. Ensure tests are independent and repeatable

### Test Review Checklist
- [ ] Tests cover the intended functionality
- [ ] Tests are properly isolated
- [ ] Appropriate fixtures are used
- [ ] Error cases are tested
- [ ] Performance implications considered

For more information, see the main [README.md](README.md) file.
