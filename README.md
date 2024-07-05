# Ed-Tech App Backend

This is the backend for the Ed-Tech App, which supports multiple coaching institutes. It includes functionalities for user authentication, lecture management, attendance tracking, and fee payments with Razorpay integration.

## Prerequisites

- Python 3.10+
- Docker
- Django
- Razorpay Python SDK

## Installation

1. **Clone the repository**

    ```sh
    git clone https://github.com/DivyanshuLohani/ed-tech-app-backend.git
    cd ed-tech-app-backend
    ```

2. **Create a virtual environment**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**

    ```sh
    pip install -r requirements.txt
    ```

<!-- 4. **Set up environment variables**

    Create a `.env` file in the root of the project and add the necessary environment variables. Here is an example:

    ```sh
    SECRET_KEY=your_secret_key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    DATABASE_URL=postgres://user:password@localhost:5432/dbname
    RAZORPAY_API_KEY=your_razorpay_api_key
    RAZORPAY_API_SECRET=your_razorpay_api_secret
    REDIS_URL=redis://localhost:6379/0
    ``` -->

## Starting the Server

1. **Start Redis using Docker**

    ```sh
    docker run -d -p 6379:6379 redis
    ```

2. **Start Celery**

    ```sh
    celery -A server worker --loglevel=info
    ```

3. **Start the Django server**

    ```sh
    python manage.py migrate
    python manage.py runserver
    ```

## API Endpoints

### User Authentication

- `POST /auth/login/` - Login
- `POST /auth/register/` - Register
- `POST /auth/refresh/` - Refresh Token
- `GET /auth/user/` - Get logged-in user details

### Batch Management

- `POST /batches/create/` - Create batch
- `GET /batches/` - Get all the batches which you are enrolled in (teachers will get all the batches)
- `GET /batches/:id/` - Get batch details with subjects inside it
- `GET /batches/subjects/:id/` - Get all the chapters inside the subject
- `POST /batches/subjects/` - Create a new subject
- `POST /batches/chapters/` - Create a new chapter

### Lecture Management

- `POST /lectures/` - Create a new lecture
- `GET /lectures/:uid/` - Get a lecture with ID
- `GET /batches/chapters/:uid/lectures/` - Get all the lectures in the chapter

### Notes Management

- `GET /batches/chapters/:uid/notes` - Get all the notes in the chapter
- `POST /documents/notes/` - Create notes
- `GET /documents/notes/:uid` - Get note with ID

### DPP Management

- `GET /batches/chapters/:uid/dpps` - Get all the DPPs in the chapter
- `POST /documents/dpps/` - Create DPP
- `GET /documents/dpps/:uid` - Get DPP with ID

## Testing

To run tests, use the following command:

```sh
python manage.py test
```
