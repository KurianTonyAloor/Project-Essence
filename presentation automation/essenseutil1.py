import time
from PIL import ImageGrab
import pytesseract
from playwright.sync_api import Playwright, sync_playwright
import pathlib
import cv2
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Global variables
wpm = 0
time1 = 0
user_engaged = False
paused_time = 0
remaining_time = 0
slide_timer_start = None
presentation_url = None
current_slide = 2
log_file = "user_data_log.txt"
slide_links = {}

cascade_path = pathlib.Path(cv2.__file__).parent.absolute() / "data/haarcascade_frontalface_default.xml"
print(cascade_path)

# Function to load log file
def load_log():
    global wpm, slide_links
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            lines = file.readlines()
            wpm = float(lines[0].strip().split(":")[1])
            for line in lines[1:]:
                title, url, slides = line.strip().split("|")
                slide_links[title] = {"url": url, "slides": int(slides)}
    else:
        save_log()

# Function to save log file
def save_log():
    global wpm, slide_links
    with open(log_file, 'w') as file:
        file.write(f"Reading Speed (WPM): {wpm}\n")
        for title, details in slide_links.items():
            file.write(f"{title}|{details['url']}|{details['slides']}\n")

# Function to measure reading speed
def measure_reading_speed():
    global wpm
    if wpm > 0:
        print(f"Reading speed already recorded: {wpm:.2f} words per minute.")
        return

    passage = """Reading speed is an important skill to develop. By increasing your reading speed, 
    you can save time and be more efficient with your study or work. Let's find out your reading speed!"""

    print("Please read the following passage and press Enter when you're done:\n")
    print(passage)
    input("\nPress Enter to start reading...")

    start_time = time.time()

    input("\nPress Enter after you've finished reading...")

    end_time = time.time()

    time_taken = end_time - start_time
    word_count = len(passage.split())
    wpm = (word_count / time_taken) * 60

    print(f"\nYou read {word_count} words in {time_taken:.2f} seconds.")
    print(f"Your reading speed is approximately {wpm:.2f} words per minute.")
    save_log()  # Save reading speed to log

# Function to extract text from the slide
def extract_slide_text():
    region = (400, 270, 1440, 810)
    screenshot = ImageGrab.grab(bbox=region)
    screenshot.save("screenshot.png")
    text = pytesseract.image_to_string(screenshot)
    return text

# Function to calculate the time for a slide
def calculate_slide_time(text):
    global wpm, time1, remaining_time, slide_timer_start
    sec = len(text.split())
    time1 = sec / (wpm / 60)
    remaining_time = time1
    slide_timer_start = time.time()
    print(f"Time for slide: {time1:.2f} seconds")

# Function to run the presentation
def run(playwright: Playwright, url: str):
    global current_slide
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    time.sleep(5)

    # Extract initial text and calculate time
    text = extract_slide_text()
    print("Extracted Text:", text)
    calculate_slide_time(text)

    return page

# Function to move to the next slide
def NextSlide(page):
    global current_slide, remaining_time, slide_timer_start
    try:
        if current_slide <= slid:
            page.locator(".docs-texteventtarget-iframe").press("ArrowRight")
            print(f"Moved to slide {current_slide}")
            current_slide += 1

            # Extract new text and recalculate time for the next slide
            text = extract_slide_text()
            print("Extracted Text for new slide:", text)
            calculate_slide_time(text)
        else:
            print("End of presentation.")
    except Exception as e:
        print(f"Failed to navigate to the next slide: {e}")

# Function to handle face recognition
def FceRec(page):
    global user_engaged, paused_time, remaining_time, slide_timer_start
    clf = cv2.CascadeClassifier(str(cascade_path))
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Failed to open camera")
        return

    while current_slide <= slid:
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = clf.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(faces) > 0:
            if not user_engaged:
                user_engaged = True
                print("User Engaged: Resuming slide timer.")
                if paused_time:
                    slide_timer_start += time.time() - paused_time  # Adjust slide timer start
                    paused_time = None
            else:
                remaining_time -= time.time() - slide_timer_start
                slide_timer_start = time.time()

            for (x, y, width, height) in faces:
                cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 0), 2)
            cv2.putText(frame, "User Engaged", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

            if remaining_time <= 0:
                NextSlide(page)
        else:
            if user_engaged:
                user_engaged = False
                print("User Not Engaged: Pausing slide timer.")
                paused_time = time.time()

            cv2.putText(frame, "No User Detected", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

        cv2.imshow("Faces", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

# Main Program
if __name__ == "__main__":
    while True:
        choice = input("Do you have an existing log file? (y/n): ").lower()
        if choice == 'y':
            load_log()
        else:
            print("Creating a new log file...")
            measure_reading_speed()

        while True:
            chc = input("To analyze reading speed (1), to advance to the presentation (2), or to exit (3): ")
            if chc == '1':
                measure_reading_speed()
            elif chc == '2':
                if not slide_links:
                    title = input("Enter the title of the presentation: ")
                    presentation_url = input("Enter the URL of the presentation: ")
                    slid = int(input("Enter the number of slides: "))
                    slide_links[title] = {"url": presentation_url, "slides": slid}
                    save_log()  # Save presentation URL to log
                else:
                    print("Available presentations:")
                    for idx, title in enumerate(slide_links.keys(), start=1):
                        print(f"{idx}. {title}")
                    selection = input("Choose a presentation by number or type 'new' to add a new one: ")
                    if selection.lower() == 'new':
                        title = input("Enter the title of the presentation: ")
                        presentation_url = input("Enter the URL of the presentation: ")
                        slid = int(input("Enter the number of slides: "))
                        slide_links[title] = {"url": presentation_url, "slides": slid}
                        save_log()  # Save presentation URL to log
                    else:
                        title = list(slide_links.keys())[int(selection) - 1]
                        presentation_url = slide_links[title]["url"]
                        slid = slide_links[title]["slides"]

                with sync_playwright() as playwright:
                    page = run(playwright, presentation_url)
                    FceRec(page)
            elif chc == '3':
                break
