from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///novels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Novel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    latest_chapter = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

logging.basicConfig(level=logging.INFO)

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'  # Change this if you are using a different SMTP server
EMAIL_PORT = 587  # Port number for SMTP
EMAIL_USERNAME = 'shadowmonarchnightcore@gmail.com'  # Replace with your email address
EMAIL_PASSWORD = 'WebScraper112'  # Replace with your email password

def create_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Uncomment the following line for headless mode (no GUI)
    # options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)  # Increase the page load timeout
    return driver

def send_email(to_email, novel_url, latest_chapter):
    subject = 'Novel Chapter Update'
    body = f'Master, the novel at {novel_url} has a new chapter: {latest_chapter}'

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME  # Sender's email address
    msg['To'] = to_email  # Recipient's email address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)  # Log in to the SMTP server
            server.sendmail(EMAIL_USERNAME, to_email, msg.as_string())  # Send the email
        logging.info(f'Email sent to {to_email}')
    except Exception as e:
        logging.error(f'Failed to send email: {e}')

def check_for_updates():
    while True:
        novels = Novel.query.all()
        for novel in novels:
            try:
                driver = create_driver()
                driver.get(novel.url)
                wait = WebDriverWait(driver, 30)
                
                latest_chapter_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'p.latest.text1row'))
                )
                latest_chapter = latest_chapter_element.text.strip()
                
                if latest_chapter != novel.latest_chapter:
                    novel.latest_chapter = latest_chapter
                    db.session.commit()
                
                # Send email notification regardless of whether a new chapter was detected
                send_email(novel.email, novel.url, latest_chapter)
                
            except Exception as e:
                logging.error(f"Error checking updates for {novel.url}: {e}")
            finally:
                driver.quit()

        time.sleep(1800)  # Check for updates every 30 minutes

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        email = request.form.get('email')

        if not url or not email:
            return 'Invalid input', 400

        try:
            driver = create_driver()
            driver.get(url)
            wait = WebDriverWait(driver, 30)
            
            latest_chapter_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p.latest.text1row'))
            )
            latest_chapter = latest_chapter_element.text.strip()
            driver.quit()

            novel = Novel.query.filter_by(url=url).first()
            if novel:
                novel.latest_chapter = latest_chapter
            else:
                novel = Novel(url=url, email=email, latest_chapter=latest_chapter)
                db.session.add(novel)
            db.session.commit()

        except Exception as e:
            logging.error(f"Error adding novel: {e}")
            return f"Error adding novel: {e}", 500
        finally:
            driver.quit()

        return redirect(url_for('index'))

    novels = Novel.query.all()
    return render_template('index.html', novels=novels)

@app.route('/remove', methods=['POST'])
def remove():
    url = request.form.get('url')
    novel = Novel.query.filter_by(url=url).first()
    if novel:
        db.session.delete(novel)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/novels')
def get_novels():
    novels = Novel.query.all()
    return jsonify([{
        'url': novel.url,
        'email': novel.email,
        'latest_chapter': novel.latest_chapter
    } for novel in novels])

if __name__ == '__main__':
    threading.Thread(target=check_for_updates, daemon=True).start()
    app.run(debug=True)
