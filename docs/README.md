# Access Key Manager

## Documentation

## Project Overview

Access Key Manager is a web application developed for Micro-Focus Inc. to manage access keys for their multitenant school management platform. It allows schools to purchase and manage access keys to activate their accounts.

## Features

### School IT Personnel

- Account management (signup, login, email verification, password reset)
- View all granted access keys (active, expired, revoked)
- See key details (status, procurement date, expiry date)
- One active key limit per user

### Micro-Focus Admin

- Secure login
- Manually revoke keys
- View all generated keys and their details
- API endpoint to check active key status for a given school email

## Technologies Used

- Django 5.0.6
- Python 3.10+
- PostgreSQL (for production)
- Paystack (for payment processing)
- Celery (for background tasks)

## Project Structure

Our project consists of the following main Django apps:

- `users`: Handles user authentication, profiles, and billing information
- `access_keys`: Manages the creation, distribution, verification, and payment processing of access keys

## Data Models

### User Model (users app)

- Custom user model extending AbstractUser
- Additional fields: is_school_personnel, is_admin, school, staff_id

### School Model (users app)

- Represents a school with a name field

### BillingInformation Model (users app)

- Stores billing information for users
- Fields: payment method, mobile money number, card details

### AccessKey Model (access_keys app)

- Represents an access key for a school
- Fields: key, school, status, assigned_to, procurement_date, expiry_date, revoked_by, revoked_on, price

### KeyLog Model (access_keys app)

- Logs actions performed on access keys
- Fields: action, user, access_key, timestamp

## API Endpoints

### Check Key Status

- Endpoint: `/access-keys/api/status/<email>/`
- Method: GET
- Description: Checks the status of an active access key for a given user email
- Response:
  - 200 OK: Returns active key details if found
  - 404 Not Found: If no active key is found for the given email

## Background Tasks

### update_key_statuses

- Periodically checks and updates the status of access keys
- Expires keys that have reached their expiry date
- Schedules the next run based on upcoming expiries

### monitor_memory

- Monitors the memory and CPU usage of the Celery worker

## Installation

### Prerequisites

- Python 3.10+
- Django 5.0.6
- pip

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/khaeyMensah/access-key-manager.git
   cd access-key-manager
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory and add the following:

   ```plaintext
   SECRET_KEY = your_secret_key
   DEBUG = True
   ALLOWED_HOSTS = localhost, 127.0.0.1
   CSRF_TRUSTED_ORIGINS = http://localhost, http://127.0.0.1, https://your-deployed-url
   EMAIL_BACKEND = django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST = smtp.gmail.com
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = your-email@gmail.com
   EMAIL_HOST_PASSWORD = your-app-password
   DEFAULT_FROM_EMAIL = your-email@gmail.com
   PAYSTACK_PUBLIC_KEY = your_paystack_public_key
   PAYSTACK_SECRET_KEY = your_paystack_secret_key
   CALLBACK_URL = https://your-url/access-keys/paystack/callback/
   DJANGO_SETTINGS_MODULE = access_key_manager.settings
   ```

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**

   ```bash
   python manage.py runserver
   ```

## Usage

1. Register as School Personnel or Admin
2. Complete your profile after email verification
3. Manage access keys (Admin only)
4. Use API endpoint /access-keys/api/status/<email>/ to check key status

## Testing

To run the test suite:

```bash
python manage.py test
```

## Contribution Guidelines

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes and write tests if applicable
4. Submit a pull request with a clear description of your changes

## Troubleshooting

- If you encounter email sending issues, ensure your Gmail account is set up for less secure apps or use an App Password.
- For Paystack integration issues, verify your public and secret keys.
- If Celery tasks are not running, check your Celery and Redis configurations.

## Security Considerations

- Always use environment variables for sensitive information.
- Keep the DEBUG setting to False in production.
- Regularly update dependencies to patch security vulnerabilities.
- Ensure that only authorized users can access admin functionalities.

## Diagrams

### Database Design

![ER Diagram](/docs/ER_diagram.png)

## Deployment

- [Deployed Application Link](https://mfocusmanager.onrender.com)

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

...
