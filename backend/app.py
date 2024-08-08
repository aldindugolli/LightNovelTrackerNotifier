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

def create_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Uncomment the following line for debugging
    # options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(10)  # Increase the page load timeout
    return driver

def check_for_updates():
    while True:
        novels = Novel.query.all()
        for novel in novels:
            try:
                driver = create_driver()
                driver.get(novel.url)
                wait = WebDriverWait(driver, 10)
                
                latest_chapter_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'p.latest.text1row'))
                )
                latest_chapter = latest_chapter_element.text.strip()
                
                if latest_chapter != novel.latest_chapter:
                    novel.latest_chapter = latest_chapter
                    db.session.commit()
                    # send_email(novel.email, latest_chapter)
            except Exception as e:
                logging.error(f"Error checking updates for {novel.url}: {e}")
            finally:
                driver.quit()

        time.sleep(3600)

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
            wait = WebDriverWait(driver, 10)
            
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
    threading.Thread(target=check_for_updates).start()
    app.run(debug=True)
