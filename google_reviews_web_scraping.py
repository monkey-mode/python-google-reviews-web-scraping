# %%
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# %%
# Initialize Chrome browser using WebDriver Manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Place URL (Google Maps with your specific place ID)
url = "https://www.google.com/maps/place/?q=place_id:ChIJ66xUOlyf4jARvMLE_hDQAX0&hl=en"

# Load the page
driver.get(url)

# Allow the page to load
time.sleep(5)

# %%
# Click on the "Reviews" tab
try:
    reviews_tab = driver.find_element(
        By.XPATH, "//button[contains(@aria-label, 'Reviews')]"
    )
    reviews_tab.click()
    time.sleep(3)  # Wait for the reviews tab to load
except Exception as e:
    print(f"Error clicking Reviews tab: {e}")
    driver.quit()
    exit()

# %%
# Click on the "Sort" button to sort by "Highest rating"
try:
    # Locate the "Sort" button using its class name
    sort_button = driver.find_element(
        By.XPATH, "//button[contains(@aria-label, 'Sort reviews')]"
    )
    sort_button.click()
    time.sleep(2)  # Wait for the sort options to appear

    # Select the entire "Highest rating" menu item
    highest_rating_option = driver.find_element(
        By.CSS_SELECTOR, "#action-menu > div:nth-child(3)"
    )
    highest_rating_option.click()
    time.sleep(3)  # Wait for the reviews to reload after sorting
except Exception as e:
    print(f"Error sorting reviews: {e}")
    # driver.quit()
    # exit()

# %%
scroll_pause_time = 2

# CSS selector for the scrollable element

# Wait for the scrollable element to be present
scrollable_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located(
        (By.XPATH, ".//div[contains(@class, 'm6QErb DxyBCb kA9KIf dS8AEf XiKgde')]")
    )
)
# Get initial scroll height
last_height = driver.execute_script(
    "return arguments[0].scrollHeight", scrollable_element
)


def is_scrollbar_at_bottom(element):
    # Check if scrollbar is at the bottom
    return driver.execute_script(
        """
        var element = arguments[0];
        return Math.abs(element.scrollHeight - element.scrollTop - element.clientHeight);
    """,
        element,
    )


attempts = 0
while True:
    # Scroll to the bottom of the element
    driver.execute_script(
        "arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_element
    )
    time.sleep(scroll_pause_time)

    try:
        more_buttons = scrollable_element.find_elements(
            By.XPATH, ".//button[contains(@aria-label, 'See more')]"
        )
        for button in more_buttons:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", button
            )
            button.click()
            time.sleep(0.5)

        translate_buttons = scrollable_element.find_elements(
            By.XPATH,
            ".//button[contains(@class, 'kyuRq') and contains(@jsaction, 'review.showReviewInTranslation')]",
        )
        for button in translate_buttons:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", button
            )
            button.click()
            time.sleep(0.5)  # Short pause after each click
    except:
        pass  # Continue if no translation buttons are found

    time.sleep(2)
    # Check if we've reached the end of the reviews
    # Check if we've reached the bottom
    if is_scrollbar_at_bottom(scrollable_element) != 0:
        print("New content loaded, continuing to scroll.")
        attempts += 1
    else:
        print(f"Reached the bottom. Attempt {attempts}")
        break

    # Small pause to allow for any animations to complete


# %%
# Get page source and parse it with BeautifulSoup
page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")

# Extract reviews and their star ratings
reviews_data = []
reviews = soup.find_all("div", class_="jftiEf")

for review in reviews:
    # Extract review text
    review_text_element = review.find("span", class_="wiI7pd")
    review_text = review_text_element.text if review_text_element else ""

    star_element = review.find("span", class_="kvMYJc")
    star_rating = int(star_element["aria-label"][0]) if star_element else 0

    # Get the reviewer's name
    name_element = review.find("div", class_="d4r55")
    reviewer_name = name_element.text if name_element else "Anonymous"

    # Get the reviewer's profile image
    image_element = review.find("img", class_="NBa7we")
    reviewer_image = image_element["src"] if image_element else None

    # Store review, name, rating, and image
    reviews_data.append(
        {
            "name": reviewer_name,
            "image": reviewer_image,
            "text": review_text,
            "rating": star_rating,
        }
    )

# Sort reviews by star rating (descending order: highest rating first)
# sorted_reviews = sorted(reviews_data, key=lambda x: x['rating'], reverse=True)
sorted_reviews = reviews_data[:20]


# %%
# Print the sorted reviews
for i, review in enumerate(sorted_reviews[:10]):
    print(f"Review {i}:")
    print(f"Name: {review['name']}")
    print(f"Image: {review['image']}")
    print(f"Rating: {review['rating']}")
    print(f"Text: {review['text']}\n")

# Close the browser
# driver.quit()

# %%
with open("reviews_output.txt", "w", encoding="utf-8") as file:
    for i, review in enumerate(sorted_reviews):
        file.write(f"Review {i}:\n")
        file.write(f"Name: {review['name']}\n")
        file.write(f"Image: {review['image']}\n")
        file.write(f"Rating: {review['rating']}\n")
        file.write(f"Text: {review['text']}\n\n")

print("Data has been exported to 'reviews_output.txt'")
