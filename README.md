# This repository contains a Django-based API service for a social media platform. 
The API service allows users to create profiles, post content, like and comment on posts, and follow other users. It's built using Django, Django Rest Framework (DRF), Celery, and Redis for asynchronous task scheduling(not working).


## Installation
Clone the repository to your local machine:
```shell
git clone https://github.com/Dmytry95/Social-Media-API.git
```

Navigate to the project directory:
```shell
cd social-media-api
```

Create a virtual environment:
```shell
python -m venv venv
source venv/bin/activate # For Windows: venv\Scripts\activate.bat
```

Install the required packages using pip:
```shell
pip install -r requirements.txt
```

Set up the database and run migrations:
```shell
python manage.py migrate
```
Start the development server:
```shell
python manage.py runserver
```

## Deployment

This project is designed for development purposes, but it can be deployed to a production server with proper settings and configurations. Ensure to set up appropriate settings for production environments, such as using a more secure database, enabling HTTPS, and handling static and media files.

## API Endpoints

The API provides the following endpoints:

### User Registration and Authentication

- **Register a new user:** `POST /api/user/register/`
- **Obtain an access token:** `POST /api/token/`
- **Refresh an access token:** `POST /api/token/refresh/`
- **Log out and invalidate the refresh token:** `POST /api/logout/`

DO NOT FORGET TO ADD AUTHORIZATION HEADER WITH TOKEN TO ALL REQUESTS(with "Bearer" prefix)
### User Profile

- **List all user profiles:** `GET /api/social_media/profiles/`
- **Create a new user profile:** `POST /social_media/api/profiles/`
- **Retrieve details of a specific user profile:** `GET /api/social_media/profiles/{profile.id}/`
- **Update a user profile (authentication required):** `PUT /api/social_media/profiles/{profile.id}/`
- **Delete a user profile (authentication required):** `DELETE /api/social_media/profiles/{profile.id}/`

### Following and Followers

- **Follow another user (authentication required):** `POST /api/social_media/profiles/{profile.id}/follow/`
- **Unfollow a user (authentication required):** `POST /api/social_media/profiles/{profile.id}/unfollow/`

### Posts

- **List all posts by users followed by the authenticated user:** `GET /api/social_media/posts/`
- **Create a new post with optional scheduled time (authentication required):** `POST /api/social_media/posts/`
- **Retrieve details of a specific post:** `GET /api/social_media/posts/{post.id}/`
- **Update a post (authentication required):** `PUT /api/social_media/posts/{post.id}/`
- **Delete a post (authentication required):** `DELETE /api/social_media/posts/{post.id}/`
- **Upload an image for a post (authentication required):** `POST /api/social_media/posts/{post.id}/upload-image/`
- **Add a comment to a post (authentication required):** `POST /api/social_media/posts/{post.id}/comment/`
- **Like or unlike a post (authentication required):** `POST /api/social_media/posts/{post.id}/like-unlike/`
- **List all posts liked by the authenticated user:** `GET /api/social_media/posts/liked/`

## Asynchronous Post Scheduling(not working)

The API allows users to schedule posts for future creation using Celery and Redis. When creating a post, you can include the `scheduled_time` field in the request body, and the post will be created at the specified time. The Celery worker is responsible for processing these scheduled tasks.

## Acknowledgments

This project was developed as part of a learning exercise and is not intended for real-world use. It serves as an example of building a Django-based API service for a social media platform. Special thanks to the Django community and the DRF team for their excellent tools and documentation.

