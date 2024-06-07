# Access Key Manager

## Documentation

### Use Case Diagram

The following diagram illustrates the use cases and interactions for the Access Key Manager application:

![Use Case Diagram](/docs/use_case_diagram.png)

### Class Diagram

The following diagram illustrates the main classes and their relationships in the Access Key Manager application:

![Class Diagram](/docs/class_diagram.png)

### ER Diagram

The following diagram illustrates the entity relationships in the Access Key Manager database:

![ER Diagram](/docs/ER_diagram.png)

## Project Overview

Micro-Focus Inc., a software company, has built a school management platform that is multitenant. Various schools can set up on the platform as though it was built specifically for them. They have agreed to use an access key-based approach to monetize it rather than building payment features into the school software. They have decided to outsource the project to you, to build a key manager, a web application that schools can use to purchase access keys to activate their school account.

## Customer Requirements

### School IT Personnel

1. Should be able to sign up & log in with an email and password with account verification. There should be a reset password feature to recover lost passwords.
2. Should be able to see a list of all access keys granted: active, expired, or revoked.
3. For each access key, the personnel should be able to see the status, date of procurement, and expiry date.
4. A user should not be able to get a new key if there is an active key already assigned to him/her. Only one key can be active at a time.

### Micro-Focus Admin

1. Should be able to log in with an email and password.
2. Should be able to manually revoke a key.
3. Should be able to see all keys generated on the platform and see the status, date of procurement, and expiry date.
4. Should be able to access an endpoint such that if the school email is provided, the endpoint should return status code 200 and details of the active key if any is found, else it should return 404. This is to enable them to integrate their school software with your key manager.

...
