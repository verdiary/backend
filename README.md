<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Apache 2.0 License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/verdiary/backend">
    <img src="assets/icon.webp" alt="Verdiary Logo" width="80" height="80">
  </a>
  <h3 align="center">Verdiary</h3>

  <p align="center">
    A Django application with Telegram integration to help users manage and track their plant cultivation activities.
    ·
    <a href="https://github.com/verdiary/backend/issues/new?template=bug-report.yml">Report Bug</a>
    ·
    <a href="https://github.com/verdiary/backend/issues/new?template=feature-request.yml">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#configuration">Configuration</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

This Django application is designed to help users manage and track their plant cultivation activities. It includes features for cataloging plant types and varieties, tracking growth stages, and receiving recommendations for plant care operations. The application also integrates with Telegram for user interaction.

### Built With

* [![Django][Django]][Django-url]
* [![Python][Python]][Python-url]
* [![Docker][Docker]][Docker-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Docker installed on your machine.

### Installation

1. Clone the repository.
   ```sh
   git clone https://github.com/verdiary/backend.git
   cd backend
   ```
2. Create a `.env` file in the root directory and add the following environment variables:
   ```sh
   SECRET_KEY=your_secret_key_here
   BOT_TOKEN=your_bot_token_here
   ```
   Replace `your_secret_key_here` and `your_bot_token_here` with your actual secret key and Telegram bot token.
3. Build and run the Docker containers.
   ```sh
   docker compose up --build
   ```
4. Create a superuser to access the admin interface:
   ```sh
   docker compose exec server python manage.py createsuperuser
   ```
5. Access the application at `http://localhost:8000` and the admin interface at `http://localhost:8000/admin`.

### Configuration

The application can be configured using environment variables in the `.env` file. The following variables are supported:

* `SECRET_KEY`: Django secret key (required)
* `BOT_TOKEN`: Telegram bot token (required)
* `DEBUG`: Enable debug mode (default: True)
* `ALLOWED_HOSTS`: List of allowed hosts (default: "localhost,127.0.0.1")
* `DATABASE_URL`: Database URL (default: sqlite:////app/db.sqlite3)
* `LANGUAGE_CODE`: Language code (default: "ru-ru")
* `TIME_ZONE`: Time zone (default: "UTC")
* `BOT_WEBHOOK_TOKEN`: Telegram bot webhook token (optional)

Additional configuration options are available in `backend/core/settings.py`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

The Django admin interface provides a comprehensive way to manage the application's data. Administrators can:
* Manage plant catalogs, including types, varieties, growth steps, and care operations.
* Oversee user plants, their growth stages, and user profiles.
* View Telegram user information.

Access the admin interface at `http://localhost:8000/admin` after creating a superuser.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

* [ ] Enhance Telegram bot functionality.
* [ ] Add more plant care recommendations.
* [ ] Improve user interface.

See the [open issues](https://github.com/verdiary/backend/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are welcome. Please fork the repository and create a pull request.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Project Link: [https://github.com/verdiary](https://github.com/verdiary)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* Django community for the framework.
* Windsurf for the AI assistant.
* CodeRabbitAI for the AI reviews.
* Docker for containerization.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[Django]: https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white
[Django-url]: https://www.djangoproject.com/
[Python]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Docker]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[contributors-shield]: https://img.shields.io/github/contributors/verdiary/backend.svg?style=for-the-badge
[contributors-url]: https://github.com/verdiary/backend/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/verdiary/backend.svg?style=for-the-badge
[forks-url]: https://github.com/verdiary/backend/network/members
[stars-shield]: https://img.shields.io/github/stars/verdiary/backend.svg?style=for-the-badge
[stars-url]: https://github.com/verdiary/backend/stargazers
[issues-shield]: https://img.shields.io/github/issues/verdiary/backend.svg?style=for-the-badge
[issues-url]: https://github.com/verdiary/backend/issues
[license-shield]: https://img.shields.io/github/license/verdiary/backend.svg?style=for-the-badge
[license-url]: https://github.com/verdiary/backend/blob/master/LICENSE
