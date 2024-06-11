# Access Key Manager

## Documentation

## Project Overview

Micro-Focus Inc., a software company, has built a school management platform that is multitenant, allowing various schools to set up on the platform as though it was built specifically for them. They have decided to monetize it using an access key-based approach rather than building payment features into the school software. Micro-Focus Inc. has outsourced the project to build a key manager, a web application that schools can use to purchase access keys to activate their school account.

## Customer Requirements

### School IT Personnel

1. Signup & Login with email and password, with account verification and password reset feature.
2. View a list of all access keys granted: active, expired, or revoked.
3. For each access key, see the status, date of procurement, and expiry date.
4. Restriction: Only one active key at a time.

### Micro-Focus Admin

1. Login with email and password.
2. Manually revoke a key.
3. View all keys generated on the platform with their status, date of procurement, and expiry date.
4. API endpoint to check active key status given a school email.

## Deliverables

1. Web application source code (GitHub)
2. ER diagram of database design
3. Deployed link

## Installation

### Prerequisites

- Python 3.10
- Django 5.0.6
- pip

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/access-key-manager.git
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
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   EMAIL_HOST_USER=your-email@example.com
   EMAIL_HOST_PASSWORD=your-email-password
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

8. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

## Usage

### Register a User

1. Navigate to the registration page.
2. Choose either "Register as School Personnel" or "Register as Admin".
3. Complete the registration form and submit.

### Complete Profile

1. After registration and email verification, log in to the application.
2. Admin users will be redirected to complete their profile if not already done.
3. Fill in the necessary details (first name, last name, staff ID).

### Access Key Management

1. Admins can manage access keys from the admin dashboard.
2. To check the status of an access key, use the API endpoint `/access-keys/api/status/<email>/`.

## Diagrams

### ER Diagram

The following diagram illustrates the entity relationships in the Access Key Manager database:

![ER Diagram](/docs/ER_diagram.png)

### Use Case Diagram

The following diagram illustrates the use cases and interactions for the Access Key Manager application:

![Use Case Diagram](/docs/use_case_diagram.png)

### Class Diagram

The following diagram illustrates the main classes and their relationships in the Access Key Manager application:

![Class Diagram](/docs/class_diagram.png)

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Deployment

- [Deployed Application Link](#)

...
