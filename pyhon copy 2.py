import time
import random
import pickle
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException


# LinkedIn Credentials (replace with yours)
USERNAME = 's.m.sahal786@outlook.com'
PASSWORD = '8662272425'

# Message template
MESSAGE_TEMPLATE = ("Hi {name},\n\n"
                    "I reviewed your application. "
                    "\n\nBest regards,\n[Your Name]")  # Replace [Your Name] with your actual name

HISTORICAL_FILE = "messaged_applicants.pkl"
CSV_FILE = "applicant_history.csv"

def load_history():
    """Load the history of messaged applicants."""
    try:
        with open(HISTORICAL_FILE, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return set()

def save_history(history):
    """Save the history of messaged applicants."""
    with open(HISTORICAL_FILE, 'wb') as file:
        pickle.dump(history, file)

def save_to_csv(applicant_name, date_time):
    """Save applicant message history to CSV."""
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([applicant_name, date_time])

def linkedin_login(driver):
    """Log into LinkedIn."""
    driver.get('https://www.linkedin.com/login')

    try:
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_input = driver.find_element(By.ID, "password")

        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "global-nav-search"))
        )
        print("Logged in successfully.")

    except Exception as e:
        print(f"Error during login: {e}")

def safe_interact_with_element(driver, locator, retries=3):
    """Attempt to interact with an element, retrying if necessary."""
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
            print(f"Clicked element: {locator}")
            return True
        except StaleElementReferenceException:
            print(f"Stale element reference encountered. Retrying... {attempt + 1}/{retries}")
            time.sleep(2)
        except TimeoutException:
            print(f"Timeout while waiting for element: {locator}")
            return False
        except Exception as e:
            print(f"Error clicking element {locator}: {e}")
            return False
    print("Failed to interact with the element after retries.")
    return False

def check_application_status(driver):
    """Check if an applicant has applied for the job."""
    try:
        applied_indicator = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'applied')]"))
        )
        if applied_indicator:
            print("Applicant has applied for the job.")
            return True
    except TimeoutException:
        print("Applicant has not applied for the job.")
        return False
    except Exception as e:
        print(f"Error checking application status: {e}")
        return False

def send_message(driver, name):
    """Send a message to an applicant."""
    try:
        print(f"Attempting to send a message to {name}...")

        # Locate and click the 'Message' button
        message_button_locator = (By.XPATH, "//button[contains(@aria-label, 'Message')]")
        if safe_interact_with_element(driver, message_button_locator):
            message_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'msg-form__contenteditable'))
            )
            message = MESSAGE_TEMPLATE.format(name=name)
            message_box.send_keys(message)
            message_box.send_keys(Keys.RETURN)
            print(f"Message sent to {name}.")

            # Log the message sent
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            save_to_csv(name, current_time)

            # Close the message overlay
            close_button_locator = (By.CLASS_NAME, 'msg-overlay-bubble-header__control')
            safe_interact_with_element(driver, close_button_locator)

            # Pause between messages to prevent rate limiting
            time.sleep(random.uniform(3, 6))  # Randomized delay

    except NoSuchElementException:
        print(f"Error: Message button not found for {name}.")
    except TimeoutException:
        print(f"Error: Timed out waiting for the 'Message' button for {name}.")
    except Exception as e:
        print(f"Error while messaging {name}: {e}")

def process_applicants(driver):
    """Process applicants, clear message box, send a message, and close the dialog before moving to the next applicant."""
    try:
        # Locate the list of applicant containers
        applicants = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'hiring-people-card__title')]"))
        )
        print(f"Found {len(applicants)} applicants.")

        # Iterate through each applicant and send a message
        for index, applicant in enumerate(applicants):
            try:
                applicant_name = applicant.text.strip()
                print(f"Applicant Name: {applicant_name}")

                # Click the applicant's name to open the profile/modal
                applicant.click()
                print(f"Clicked on {applicant_name} to open the profile.")

                # Wait for the 'Message' button to appear and click it
                message_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Message']]"))
                )
                message_button.click()
                print(f"Clicked 'Message' button for {applicant_name}.")

                # Wait for the message input box to appear
                message_box = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'msg-form__contenteditable'))
                )

                # Clear the message input box
                message_box.click()
                message_box.send_keys(Keys.CONTROL + "a")  # Select all existing text
                message_box.send_keys(Keys.BACKSPACE)  # Delete selected text
                print(f"Cleared the message box for {applicant_name}.")

                # Enter the message text
                message = MESSAGE_TEMPLATE.format(name=applicant_name)
                message_box.send_keys(message)
                print(f"Entered message for {applicant_name}.")

                # Locate and click the 'Send' button
                send_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(@class, 'msg-form__send-button')]"))
                )
                send_button.click()
                print(f"Message sent to {applicant_name}.")

                # Wait briefly to ensure the message is sent
                time.sleep(2)

                # Locate and click the specific 'Close' button to close the message dialog
                close_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']"))
                )
                driver.execute_script("arguments[0].click();", close_button)
                print(f"Closed the dialog box for {applicant_name}.")

                # Pause before moving to the next applicant to avoid rate limiting
                time.sleep(random.uniform(2, 4))

            except TimeoutException:
                print(f"Timeout while interacting with {applicant_name}.")
            except NoSuchElementException:
                print(f"Required element not found for {applicant_name}.")
            except Exception as e:
                print(f"Error while processing {applicant_name}: {e}")

    except Exception as e:
        print(f"Error while processing applicants: {e}")




def automate_applicant_messaging(driver):
    """Automate messaging to applicants."""
    driver.get('https://www.linkedin.com/talent/job-management-redirect')

    try:
        jobs = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/hiring/jobs/')]"))
        )
        print(f"Found {len(jobs)} jobs.")

        for job in jobs:
            try:
                job.click()
                print("Clicked on job.")
                time.sleep(random.uniform(3, 5))  # Randomized sleep

                # Find and click the 'View Applicants' button
                view_applicants_button_locator = (By.XPATH, "//button[contains(., 'View applicants')]")
                if safe_interact_with_element(driver, view_applicants_button_locator):
                    process_applicants(driver)

                time.sleep(random.uniform(3, 5))  # Randomized sleep

            except Exception as e:
                print(f"Error processing job: {e}")
                driver.refresh()  # Refresh to get fresh elements
                time.sleep(3)

    except Exception as e:
        print(f"Error while navigating jobs or applicants: {e}")
        

def main():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-webrtc")  # Disable WebRTC to avoid stun errors

    driver = webdriver.Chrome(service=Service(), options=options)

    try:
        linkedin_login(driver)
        automate_applicant_messaging(driver)

    except Exception as e:
        print(f"Script encountered an error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

