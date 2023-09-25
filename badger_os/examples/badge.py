import badger2040
import pngdec
import jpegdec
import json

# Global Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

IMAGE_WIDTH = 104

COMPANY_HEIGHT = 30
DETAILS_HEIGHT = 20
NAME_HEIGHT = HEIGHT - COMPANY_HEIGHT - (DETAILS_HEIGHT * 2) - 2
TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 1

COMPANY_TEXT_SIZE = 0.6
DETAILS_TEXT_SIZE = 0.5

LEFT_PADDING = 5
NAME_PADDING = 20
DETAIL_SPACING = 10

BADGE_DB_PATH = "/badges/badge_data.json"


class Badge:
    def __init__(self, badge_data_path):
        with open(badge_data_path, "r") as f:
            self.badge_data = json.load(f)

        self.company_index = 0
        self.detail1_index = 0
        self.detail2_index = 0
        self.company_text_size = COMPANY_TEXT_SIZE

        # Create a new Badger and set it to update NORMAL
        self.display = badger2040.Badger2040()
        self.display.led(128)
        self.display.set_update_speed(badger2040.UPDATE_NORMAL)
        self.display.set_thickness(2)

    def prepare(self):
        company = self.badge_data["company"][self.company_index]
        self.company_text = company["text"]
        self.company_text_size = company["size"]
        self.name = self.badge_data["name"]
        detail1 = self.badge_data["detail1"][self.detail1_index]
        detail2 = self.badge_data["detail2"][self.detail2_index]
        self.detail1_title = detail1["title"]
        self.detail1_text = detail1["text"]
        self.detail2_title = detail2["title"]
        self.detail2_text = detail2["text"]
        self.image_path = self.badge_data["image_path"]

        # Truncate all of the text (except for the name as that is scaled)
        self.company_text = self.truncatestring(
            self.company_text, self.company_text_size, TEXT_WIDTH
        )

        self.detail1_title = self.truncatestring(
            self.detail1_title, DETAILS_TEXT_SIZE, TEXT_WIDTH
        )
        self.detail1_text = self.truncatestring(
            self.detail1_text,
            DETAILS_TEXT_SIZE,
            TEXT_WIDTH
            - DETAIL_SPACING
            - self.display.measure_text(self.detail1_title, DETAILS_TEXT_SIZE),
        )

        self.detail2_title = self.truncatestring(
            self.detail2_title, DETAILS_TEXT_SIZE, TEXT_WIDTH
        )
        self.detail2_text = self.truncatestring(
            self.detail2_text,
            DETAILS_TEXT_SIZE,
            TEXT_WIDTH
            - DETAIL_SPACING
            - self.display.measure_text(self.detail2_title, DETAILS_TEXT_SIZE),
        )

    def truncatestring(self, text, text_size, width):
        """Reduce the size of a string until it fits within a given width"""
        while True:
            length = self.display.measure_text(text, text_size)
            if length > 0 and length > width:
                text = text[:-1]
            else:
                text += ""
                return text

    def draw(self):
        """Draw the badge, including user text"""
        self.display.set_pen(0)
        self.display.clear()

        # Draw badge image
        if self.image_path.lower().endswith(".png"):
            png = pngdec.PNG(self.display.display)
            png.open_file(self.image_path)
            png.decode(WIDTH - IMAGE_WIDTH, 0)
        else:
            jpeg = jpegdec.JPEG(self.display.display)
            jpeg.open_file(self.image_path)
            jpeg.decode(WIDTH - IMAGE_WIDTH, 0)

        # Draw a border around the image
        self.display.set_pen(0)
        self.display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - 1, 0)
        self.display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - IMAGE_WIDTH, HEIGHT - 1)
        self.display.line(WIDTH - IMAGE_WIDTH, HEIGHT - 1, WIDTH - 1, HEIGHT - 1)
        self.display.line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1)

        # Uncomment this if a white background is wanted behind the company
        # display.set_pen(15)
        # display.rectangle(1, 1, TEXT_WIDTH, COMPANY_HEIGHT - 1)

        # Draw the company
        self.display.set_pen(15)  # Change this to 0 if a white background is used
        self.display.set_font("serif")
        self.display.text(
            self.company_text,
            LEFT_PADDING,
            (COMPANY_HEIGHT // 2) + 1,
            WIDTH,
            self.company_text_size,
        )

        # Draw a white background behind the name
        self.display.set_pen(15)
        self.display.rectangle(1, COMPANY_HEIGHT + 1, TEXT_WIDTH, NAME_HEIGHT)

        # Draw the name, scaling it based on the available width
        self.display.set_pen(0)
        self.display.set_font("sans")
        name_size = 2.0  # A sensible starting scale
        while True:
            name_length = self.display.measure_text(self.name, name_size)
            if name_length >= (TEXT_WIDTH - NAME_PADDING) and name_size >= 0.1:
                name_size -= 0.01
            else:
                self.display.text(
                    self.name,
                    (TEXT_WIDTH - name_length) // 2,
                    (NAME_HEIGHT // 2) + COMPANY_HEIGHT + 1,
                    WIDTH,
                    name_size,
                )
                break

        # Draw a white backgrounds behind the details
        self.display.set_pen(15)
        self.display.rectangle(
            1, HEIGHT - DETAILS_HEIGHT * 2, TEXT_WIDTH, DETAILS_HEIGHT - 1
        )
        self.display.rectangle(
            1, HEIGHT - DETAILS_HEIGHT, TEXT_WIDTH, DETAILS_HEIGHT - 1
        )

        # Draw the first detail's title and text
        self.display.set_pen(0)
        self.display.set_font("sans")
        name_length = self.display.measure_text(self.detail1_title, DETAILS_TEXT_SIZE)
        self.display.text(
            self.detail1_title,
            LEFT_PADDING,
            HEIGHT - ((DETAILS_HEIGHT * 3) // 2),
            WIDTH,
            DETAILS_TEXT_SIZE,
        )
        self.display.text(
            self.detail1_text,
            5 + name_length + DETAIL_SPACING // 2,
            HEIGHT - ((DETAILS_HEIGHT * 3) // 2),
            WIDTH,
            DETAILS_TEXT_SIZE,
        )

        # Draw the second detail's title and text
        name_length = self.display.measure_text(self.detail2_title, DETAILS_TEXT_SIZE)
        self.display.text(
            self.detail2_title,
            LEFT_PADDING,
            HEIGHT - (DETAILS_HEIGHT // 2),
            WIDTH,
            DETAILS_TEXT_SIZE,
        )
        self.display.text(
            self.detail2_text,
            LEFT_PADDING + name_length + DETAIL_SPACING,
            HEIGHT - (DETAILS_HEIGHT // 2),
            WIDTH,
            DETAILS_TEXT_SIZE,
        )

        self.display.update()

    def run(self):
        # Sometimes a button press or hold will keep the system
        # powered *through* HALT, so latch the power back on.
        self.display.keepalive()

        if self.display.pressed(badger2040.BUTTON_A):
            self.company_index += 1
            if self.company_index >= len(self.badge_data["company"]):
                self.company_index = 0
            self.prepare()
            self.draw()
        elif self.display.pressed(badger2040.BUTTON_B):
            self.detail1_index += 1
            if self.detail1_index >= len(self.badge_data["detail1"]):
                self.detail1_index = 0
            self.prepare()
            self.draw()
        elif self.display.pressed(badger2040.BUTTON_C):
            self.detail2_index += 1
            if self.detail2_index >= len(self.badge_data["detail2"]):
                self.detail2_index = 0
            self.prepare()
            self.draw()

        # If on battery, halt the Badger to save power, it will wake up if any of the front buttons are pressed
        self.display.halt()


badge = Badge(BADGE_DB_PATH)
badge.prepare()
badge.draw()

while True:
    badge.run()
