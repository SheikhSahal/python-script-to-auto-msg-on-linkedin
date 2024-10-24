import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Replace with the path to your ChromeDriver
CHROMEDRIVER_PATH = 'path/to/chromedriver'  # Update this path
LINKEDIN_USERNAME = 's.m.sahal786@outlook.com'  # Replace with your LinkedIn username
LINKEDIN_PASSWORD = '8662272425'  # Replace with your LinkedIn password
MESSAGE_TEMPLATE = "Hello {name}, thank you for applying to our job posting!"

# Initialize WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

def login_to_linkedin():
    driver.get('https://www.linkedin.com/login')
    time.sleep(2)

    username_field = driver.find_element(By.ID, 'username')
    password_field = driver.find_element(By.ID, 'password')

    username_field.send_keys(LINKEDIN_USERNAME)
    password_field.send_keys(LINKEDIN_PASSWORD)
    password_field.send_keys(Keys.RETURN)

    time.sleep(5)  # Wait for login to complete

def navigate_to_jobs():
    driver.get('https://www.linkedin.com/jobs/')
    time.sleep(5)  # Wait for the page to load

def send_messages_to_applicants():
    # Assuming you have a way to access the list of applicants (you may need to adapt this part)
    # This is a placeholder URL; replace with the actual URL for your job postings
    driver.get('https://www.linkedin.com/jobs/view/your_job_posting_id/')  # Update with your job posting ID
    time.sleep(5)

    applicants = driver.find_elements(By.CLASS_NAME, 'applicant-list-item')  # Adjust the class name as needed

    for applicant in applicants:
        name = applicant.find_element(By.CLASS_NAME, 'applicant-name').text  # Adjust class name
        send_message(name)

def send_message(name):
    message = MESSAGE_TEMPLATE.format(name=name)
    # Navigate to messaging interface and send the message (this is a simplified version)
    # You may need to implement the actual steps to send a message through LinkedIn's interface
    print(f"Sending message to {name}: {message}")
    time.sleep(2)  # Simulate time delay for sending a message

if __name__ == "__main__":
    login_to_linkedin()
    navigate_to_jobs()
    send_messages_to_applicants()
    driver.quit()
