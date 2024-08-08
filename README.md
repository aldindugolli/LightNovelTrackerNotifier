# Light Novel Chapter Tracker

This project is a web application that allows users to track light novels and receive email notifications whenever a new chapter is released. The application is built using Flask for the backend, SQLAlchemy for database management, Selenium for web scraping, and smtplib for sending emails.

## Features

- **Track Light Novels**: Users can add the URL of a light novel and their email address to receive notifications.
- **Regular Updates**: The application checks for new chapters every 30 minutes and sends an email notification whether a new chapter is released or not.
- **Web Scraping**: Uses Selenium to scrape the latest chapter information from the light novel website.
- **Email Notifications**: Automatically sends an email to the user when a new chapter is detected.

## Technologies Used

- **Backend**: Flask
- **Database**: SQLite (using SQLAlchemy)
- **Web Scraping**: Selenium with Chrome WebDriver
- **Email Sending**: smtplib
- **HTML/CSS**: Simple front-end using Flask templates

## Setup Instructions

### Prerequisites

- Python 3.x
- pip (Python package manager)
- Google Chrome (for Selenium WebDriver)

### Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/light-novel-tracker.git
    cd light-novel-tracker
    ```

2. **Install the Required Packages**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up the Database**

    The database will be automatically created when you first run the application. It's an SQLite database (`novels.db`) used to store the URLs, email addresses, and the latest chapter of the tracked novels.

4. **Configure Email Settings**

    Edit the `app.py` file and replace the email credentials with your own:

    ```python
    EMAIL_HOST = 'smtp.gmail.com'  # Replace with your SMTP server
    EMAIL_PORT = 587  # Replace with the appropriate port
    EMAIL_USERNAME = 'youremail@gmail.com'  # Replace with your email address
    EMAIL_PASSWORD = 'yourpassword'  # Replace with your email password
    ```

    > **Note:** Ensure your email account is configured to allow less secure apps, or use an app-specific password if two-factor authentication is enabled.

5. **Run the Application**

    ```bash
    python app.py
    ```

6. **Access the Web Interface**

    Open your web browser and go to `http://127.0.0.1:5000/`. You can now add novel URLs and your email to start tracking.

## Usage

1. **Add a Novel URL**: Input the URL of the light novel and your email address to start tracking.
2. **Receive Notifications**: The app checks for updates every 30 minutes. You'll receive an email whenever a new chapter is released.
3. **Manage Tracked Novels**: View and remove tracked novels from the web interface.

## Troubleshooting

- **Email Issues**: If the app fails to send emails, ensure that the email credentials are correct and that your email provider allows SMTP access.
- **Web Scraping Errors**: Ensure that the selector used in Selenium (`'p.latest.text1row'`) correctly targets the latest chapter element on the light novel website. You may need to adjust this selector based on the website's structure.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Acknowledgments

- Flask for providing an easy-to-use web framework.
- Selenium for powerful web scraping capabilities.
- SQLAlchemy for simple database management.

