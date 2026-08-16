from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import json
import os
import requests


# =========================================================
# CONFIGURATION
# =========================================================

WEBSITE_URL = "https://pminternship.mca.gov.in/"

# ---------------------------------------------------------
# ntfy notification
# ---------------------------------------------------------
# Subscribe to this same topic in the ntfy app.
# Keep this topic difficult to guess.
NTFY_TOPIC = os.environ["NTFY_TOPIC"]

# ---------------------------------------------------------
# Data file
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "internships.json"
)


# =========================================================
# SEND NTFY NOTIFICATION
# =========================================================

def send_notification(message):

    url = f"https://ntfy.sh/{NTFY_TOPIC}"

    try:

        response = requests.post(
            url,
            data=message.encode("utf-8"),
            headers={
                "Title": "New PM Internship",
                "Priority": "high",
                "Tags": "rotating_light,briefcase"
            },
            timeout=15
        )

        response.raise_for_status()

        print("✓ Notification sent successfully")

    except requests.RequestException as e:

        print("❌ Notification failed:")
        print(e)


# =========================================================
# LOAD PREVIOUS INTERNSHIPS
# =========================================================

def load_previous_internships():

    if not os.path.exists(DATA_FILE):

        print("No previous internship data found.")
        print("This is the first run.")

        return None

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError) as e:

        print("⚠ Could not read previous internship data:")
        print(e)

        return None


# =========================================================
# SAVE CURRENT INTERNSHIPS
# =========================================================

def save_internships(internships):

    try:

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                internships,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("✓ Internship data saved")

    except OSError as e:

        print("❌ Could not save internship data:")
        print(e)


# =========================================================
# FIND NEW INTERNSHIPS
# =========================================================

def find_new_internships(
    old_internships,
    current_internships
):

    # First run:
    # We don't want notifications for every existing
    # internship. We only create the baseline.

    if old_internships is None:

        return []

    new_internships = []

    for internship in current_internships:

        if internship not in old_internships:

            new_internships.append(
                internship
            )

    return new_internships


# =========================================================
# CREATE NOTIFICATION MESSAGE
# =========================================================

def create_notification_message(
    new_internships
):

    count = len(new_internships)

    if count == 1:

        message = (
            "🚨 NEW PM INTERNSHIP\n\n"
        )

    else:

        message = (
            f"🚨 {count} NEW PM INTERNSHIPS\n\n"
        )

    for number, internship in enumerate(
        new_internships,
        start=1
    ):

        message += (
            "━━━━━━━━━━━━━━━━━━\n"
            f"INTERNSHIP {number}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"{internship}\n\n"
        )

    message += (
        "📍 Delhi → New Delhi\n\n"
        "🔗 https://pminternship.mca.gov.in/"
    )

    return message


# =========================================================
# GET ALL INTERNSHIPS FROM WEBSITE
# =========================================================

def get_all_internships():

    # =====================================================
    # SETUP CHROME
    # =====================================================

    options = webdriver.ChromeOptions()

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        options=options
    )

    wait = WebDriverWait(
        driver,
        20
    )

    try:

        # =================================================
        # OPEN WEBSITE
        # =================================================

        print()
        print("Opening website...")

        driver.get(
            WEBSITE_URL
        )

        time.sleep(5)


        # =================================================
        # SELECT DELHI
        # =================================================

        state_input = wait.until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "react-select-2-input"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            state_input
        )

        driver.execute_script(
            "arguments[0].focus();",
            state_input
        )

        state_input.send_keys(
            "DELHI"
        )

        time.sleep(2)

        delhi_option = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[@role='option' "
                    "and normalize-space()='DELHI']"
                )
            )
        )

        print("✓ Delhi option found")

        driver.execute_script(
            "arguments[0].click();",
            delhi_option
        )

        print("✓ Delhi selected")

        time.sleep(3)


        # =================================================
        # SELECT NEW DELHI
        # =================================================

        district_input = wait.until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "react-select-3-input"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            district_input
        )

        driver.execute_script(
            "arguments[0].focus();",
            district_input
        )

        district_input.send_keys(
            "NEW DELHI"
        )

        time.sleep(2)

        new_delhi_option = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[@role='option' "
                    "and normalize-space()='NEW DELHI']"
                )
            )
        )

        print("✓ New Delhi option found")

        driver.execute_script(
            "arguments[0].click();",
            new_delhi_option
        )

        print("✓ New Delhi selected")


        # =================================================
        # WAIT FOR RESULTS
        # =================================================

        print()
        print("Waiting for internship results...")

        time.sleep(10)


        # =================================================
        # GET VISIBLE INTERNSHIPS
        # =================================================

        def get_visible_internships():

            cards = driver.find_elements(
                By.CSS_SELECTOR,
                ".swiper-slide.p-2"
            )

            results = []

            for card in cards:

                text = card.text.strip()

                if (
                    text
                    and text not in results
                ):

                    results.append(
                        text
                    )

            return results


        # =================================================
        # GET INITIAL CARDS
        # =================================================

        all_internships = (
            get_visible_internships()
        )

        print()
        print("=" * 60)
        print("INITIAL CARDS")
        print("=" * 60)

        print(
            f"Currently found: "
            f"{len(all_internships)}"
        )


        # =================================================
        # FIND NEXT BUTTON
        # =================================================

        next_button_xpath = (
            "//button[@title='Next' "
            "and contains("
            "@class, "
            "'featuredInternship_explore_arrow'"
            ")]"
        )

        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    next_button_xpath
                )
            )
        )

        print(
            "✓ Internship Next button found"
        )


        # =================================================
        # MOVE THROUGH CAROUSEL
        # =================================================

        duplicate_count = 0
        click_count = 0

        while True:

            # ---------------------------------------------
            # Find Next button
            # ---------------------------------------------

            next_button = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        next_button_xpath
                    )
                )
            )


            # ---------------------------------------------
            # Click Next
            # ---------------------------------------------

            driver.execute_script(
                "arguments[0].click();",
                next_button
            )

            click_count += 1

            print()
            print(
                f"Next clicked: "
                f"{click_count}"
            )


            # ---------------------------------------------
            # Wait for website to update
            # ---------------------------------------------

            time.sleep(5)


            # ---------------------------------------------
            # Get cards after movement
            # ---------------------------------------------

            current_visible = (
                get_visible_internships()
            )


            # ---------------------------------------------
            # Find genuinely new cards
            # ---------------------------------------------

            new_cards = []

            for card in current_visible:

                if card not in all_internships:

                    new_cards.append(
                        card
                    )


            # ---------------------------------------------
            # New card found
            # ---------------------------------------------

            if new_cards:

                duplicate_count = 0

                for card in new_cards:

                    all_internships.append(
                        card
                    )

                    print()
                    print(
                        "✓ New internship found"
                    )

                    print(
                        card
                    )

                print()
                print(
                    f"Total unique internships: "
                    f"{len(all_internships)}"
                )


            # ---------------------------------------------
            # No new card
            # ---------------------------------------------

            else:

                duplicate_count += 1

                print(
                    f"No new internship "
                    f"({duplicate_count}/2)"
                )


            # ---------------------------------------------
            # Stop after 2 duplicate positions
            # ---------------------------------------------

            if duplicate_count >= 2:

                print()
                print(
                    "✓ Reached end of carousel"
                )

                break


            # ---------------------------------------------
            # Safety limit
            # ---------------------------------------------

            if click_count >= 50:

                print()
                print(
                    "⚠ Safety limit reached"
                )

                break


        # =================================================
        # FINAL RESULT
        # =================================================

        print()
        print("=" * 60)
        print("FINAL RESULT")
        print("=" * 60)

        print(
            f"Total internships found: "
            f"{len(all_internships)}"
        )


        return all_internships


    finally:

        # =================================================
        # CLOSE CHROME
        # =================================================

        print()
        print("Closing Chrome...")

        driver.quit()


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("PM INTERNSHIP MONITOR")
    print("=" * 60)


    # =====================================================
    # GET CURRENT INTERNSHIPS
    # =====================================================

    try:

        current_internships = (
            get_all_internships()
        )

    except Exception as e:

        print()
        print("❌ Website checking failed:")
        print(e)

        raise


    # =====================================================
    # LOAD PREVIOUS DATA
    # =====================================================

    old_internships = (
        load_previous_internships()
    )


    # =====================================================
    # COMPARE
    # =====================================================

    new_internships = (
        find_new_internships(
            old_internships,
            current_internships
        )
    )


    # =====================================================
    # DISPLAY COMPARISON
    # =====================================================

    print()
    print("=" * 60)
    print("COMPARISON")
    print("=" * 60)

    if old_internships is None:

        print(
            "This is the first run."
        )

        print(
            f"Baseline created with "
            f"{len(current_internships)} internships."
        )

    else:

        print(
            f"Previous internships : "
            f"{len(old_internships)}"
        )

        print(
            f"Current internships  : "
            f"{len(current_internships)}"
        )

        print(
            f"New internships      : "
            f"{len(new_internships)}"
        )


    # =====================================================
    # NOTIFICATION
    # =====================================================

    if new_internships:

        print()
        print("=" * 60)
        print("🚨 NEW INTERNSHIPS FOUND")
        print("=" * 60)

        for internship in new_internships:

            print()
            print(internship)

        message = (
            create_notification_message(
                new_internships
            )
        )

        send_notification(
            message
        )

    else:

        print()
        print(
            "✓ No new internships found."
        )


    # =====================================================
    # SAVE CURRENT DATA
    # =====================================================

    save_internships(
        current_internships
    )


    # =====================================================
    # DONE
    # =====================================================

    print()
    print("=" * 60)
    print("MONITORING CHECK COMPLETE")
    print("=" * 60)