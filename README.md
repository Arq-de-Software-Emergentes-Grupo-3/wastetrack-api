# WasteTrack API
This repository contains the backend API for the WasteTrack application, a waste management and tracking system.

## Features
- Container management
- User authentication
- Waste tracking
- Geolocation services

## Prerequisites
- Python 3.8+ installed
- MySQL database
- pip (Python package manager)

## Installation
1. Clone the repository:

    ``` git
    git clone https://github.com/yourusername/wastetrack-api.git
    cd wastetrack-api
    ```

2. Create and activate a virtual environment (recommended):
    ### On Windows
    ``` git
    python -m venv venv
    venv\Scripts\activate
    ```

3. Install dependencies:

    ``` git
    pip install -r requirements.txt
    ```

4. Create a .env file in the root directory and configure your environment variables:

    ``` 
    SECRET_KEY=yoursecretkey
    ALGORITHM=value
    ACCESS_TOKEN_EXPIRE_MINUTES=value
    DATABASE_URL=mysql+pymysql://username:password@localhost:3306/database_name
    ```

## Running the Application

Start the application with:

``` git
python -m uvicorn app:app --reload
```

The API will be available at: http://localhost:8000

- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

## API Endpoints
The API provides the following main endpoints:

- `/auth` - Authentication routes
- `/container` - Container management
- `/users` - User management

For detailed API documentation, visit the `/docs` endpoint when the server is running.