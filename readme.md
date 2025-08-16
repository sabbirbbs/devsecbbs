# Django BlogX: A Feature-Rich Blogging Platform

Django BlogX is a powerful, open-source blogging platform built with Django. It's designed for developers who want a robust, customizable, and feature-rich foundation for their own blogging projects. Whether you're looking to start a personal blog, a community site, or a technical publication, BlogX provides the tools you need to get started quickly.

## Features

This project is packed with features to provide a modern and complete blogging experience:

*   **User Management**:
    *   Full authentication suite: user registration, login/logout, email verification, and password reset.
    *   Customizable user profiles with bios, profile pictures, and social media links.
    *   Follower/following system to build a community.
    *   User roles and permissions (Contributor, Author, Moderator, Admin).

*   **Content Creation & Management**:
    *   A powerful WYSIWYG editor (SunEditor) for writing posts.
    *   Support for Markdown.
    *   Organize posts with nested categories, tags, and series.
    *   Image uploads and gallery.
    *   Post statuses (Draft, Published, Pending).

*   **Community & Interaction**:
    *   Nested comments for engaging discussions.
    *   Like and dislike system for posts.
    *   Email subscriptions for newsletters.

*   **Moderation & Administration**:
    *   Dashboard for managing posts, comments, and users.
    *   Moderation queues for pending content.
    *   System for users to report inappropriate content.

*   **Notifications**:
    *   Real-time notifications for likes, comments, and follows.

## Tech Stack

*   **Backend**: Django
*   **Database**: SQLite (easy to switch to other databases)
*   **Frontend**: Django Templates, Tailwind CSS
*   **Key Django Packages**:
    *   `django-mptt` for nested categories and comments.
    *   `django-taggit` for tagging.
    *   `Pillow` for image processing.
    *   `markdown2` for Markdown rendering.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

*   Python 3.8+
*   pip

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the database migrations:**
    ```sh
    python manage.py migrate
    ```

5.  **Create a superuser to access the admin panel:**
    ```sh
    python manage.py createsuperuser
    ```

6.  **Run the development server:**
    ```sh
    python manage.py runserver
    ```

    The application will be available at `http://127.0.0.1:8000/`.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
