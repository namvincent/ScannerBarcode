import asyncio
import cv2, zxingcpp
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import RPi.GPIO as GPIO
from SpecifyCheckingArea import select
from capture_image import capture_frame
import numpy as np
import Adafruit_SSD1306
import requests
import base64
import matplotlib.pyplot as plt
import time
from time import gmtime, strftime
import json
import paho.mqtt.client as mqtt
from dbr import *
import re
from urllib.parse import quote
import os

READY = 16

# Set GPIO mode to BCM
# GPIO.setmode(GPIO.BCM)

# # Set the pin number you want to monitor
# # Setup the pin as input
# # Note the following are only used with SPI:
# GPIO.setup(READY, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Raspberry Pi pin configuration:
RST = None  # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST =import json
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)


# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image_display = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image_display)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()

global areas
areas = []

re_pattern = r"^\d{7}([-])\d{7}([-])\d{6}([-])\d{3}$"
re2_pattern = r"^\d{8}([-])\d{7}([-])\d{7}([-])\d{3}$"
smdReg_pattern = r"^\d{7}([-])\d{5}([-])\S{1}$"

re_options = re.IGNORECASE
re_obj = re.compile(re_pattern, re_options)
re2_obj = re.compile(re2_pattern, re_options)
smdReg_obj = re.compile(smdReg_pattern, re_options)

def show_message_OLED(text):
    try:
        disp.clear()
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load

        # Write two lines of text.

        draw.text((x, top), text, font=font, fill=255)
        # Display image.
        disp.image(image_display)
        disp.display()
    except Exception as e:
        try:
            draw.text((x, top), e, font=font, fill=255)
            # Display image.
            disp.image(image_display)
            disp.display()
        except Exception as ex:
            print(ex)

def read_out_locations_need_to_be_checked(coordinate_file_path):
    try:
        with open(coordinate_file_path, "r") as file:
            for line in file:
                # top_left_x: int = int(line.strip().split(",")[0])
                # top_left_y: int = int(line.strip().split(",")[1])
                # bottom_right_x: int = int(line.strip().split(",")[2])
                # bottom_right_y: int = int(line.strip().split(",")[3])
                # top_left = (top_left_x, top_left_y)
                # bottom_right = (bottom_right_x, bottom_right_y)
                areas.append(line)
        return areas
    except Exception as e:
        print(e)
        return []


import json
import time
import paho.mqtt.client as mqtt
from zbarscanner import decode

global array_code
array_code = []

areas = read_out_locations_need_to_be_checked("coordinate.txt")

# error = BarcodeReader.init_license("DLS2eyJvcmdhbml6YXRpb25JRCI6IjIwMDAwMSJ9")
# if error[0] != EnumErrorCode.DBR_OK:
#     print("License error: " + error[1])

# # 2.Create an instance of Barcode Reader.
# reader = BarcodeReader.get_instance()
# if reader == None:
#     raise BarcodeReaderError("Get instance failed")

def delete_files_in_directory(directory):
     # Traverse the directory recursively
    for root, dirs, files in os.walk(directory):
        # Iterate through all files in the current directory
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Attempt to remove the file
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                # Print an error message if deletion fails
                print(f"Error deleting file: {file_path}, {e}")

def scan():
    # x = [0, 1000, 2000, 3000]
    # y = [0, 600, 1200, 1800]
    # mixed = list(zip(zip(x, y), zip(x, y)))
    
    # areas = select('captured_image.jpg')
    # if len(areas) > 0:
    #     with open("coordinate.txt", 'w') as file:o7777777777777ii7oo7o5
    #                 for item in areas:
    #                         topLeft = item[0]
    #                         bottomRight = item[1]
    #                         file.write(f'{topLeft[0]},{topLeft[1]}, {bottomRight[0]},{bottomRight[1]}\n')
    show_message_OLED("Scanning")
    for area in areas:
        capture_frame(False, area)
        # coodinate = select('captured_image.jpg')
        # if len(coodinate) > 0:
        #     with open(f"coordinate-{area}.txt", 'w') as file:
        #                 for item in coodinate:
        #                         topLeft = item[0]
        #                         bottomRight = item[1]
        #                         file.write(f'{topLeft[0]},{topLeft[1]}, {bottomRight[0]},{bottomRight[1]}\n')
        img = cv2.imread("captured_image.jpg")
        # cv2.imwrite(
        #     f'images/{strftime("%Y-%m-%d %H:%M:%S", gmtime())}.jpg',
        #     img,
        # )
        gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        cv2.imwrite(f'images/gray.jpg',gray_image)
        image = img.copy()
        try:
            with open(f"coordinate-{area}.txt", "r") as file:
                for line in file:
                    top_left_x: int = int(line.strip().split(",")[0])
                    top_left_y: int = int(line.strip().split(",")[1])
                    bottom_right_x: int = int(line.strip().split(",")[2])
                    bottom_right_y: int = int(line.strip().split(",")[3])
                    topLeft = (top_left_x, top_left_y)
                    bottomRight = (bottom_right_x, bottom_right_y)

                    partial = image[
                        topLeft[1] : bottomRight[1], topLeft[0] : bottomRight[0]
                    ]
                    # gray = cv2.cvtColor(partial, cv2.COLOR_RGB2GRAY)
                    # ret, thresh = cv2.threshold(
                    #             partial, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
                    #         )
                    # resized = cv2.resize(
                    #     partial,
                    #     (partial.shape[1] *4, partial.shape[0]*4),
                    #     interpolation=cv2.INTER_LINEAR_EXACT,
                    # )

                    # cv2.imwrite(f"thresh_{area}.jpg", thresh)

                    
                    ## Take cordiante - Vincent
                    # coodinate = select(f"{line}.jpg")
                    # if len(coodinate) > 0:
                    #     with open(f"coordinate-{line}.txt", 'w') as file:
                    #                 for item in coodinate:
                    #                         topLeft = item[0]
                    #                         bottomRight = item[1]
                    #                         file.write(f'{topLeft[0]},{topLeft[1]}, {bottomRight[0]},{bottomRight[1]}\n')
                    with open(f"coordinate-{line}.txt", "r") as file_part:
                        for line_part in file_part:
                            top_left_x: int = int(line_part.strip().split(",")[0])
                            top_left_y: int = int(line_part.strip().split(",")[1])
                            bottom_right_x: int = int(line_part.strip().split(",")[2])
                            bottom_right_y: int = int(line_part.strip().split(",")[3])
                            topLeft = (top_left_x, top_left_y)
                            bottomRight = (bottom_right_x, bottom_right_y)
                    # cv2.imwrite(f"partial-{line}.jpg", line)
                    partial = cv2.cvtColor(partial, cv2.COLOR_RGB2GRAY)
                    partial_line = partial[
                        topLeft[1] : bottomRight[1], topLeft[0] : bottomRight[0]
                    ]

                    cv2.imwrite(f"partial-{line}.jpg", partial_line)
                    # cv2.imwrite(
                    #     f'images/{strftime("%Y-%m-%d %H:%M:%S", gmtime())}.jpg',
                    #     partial_line,
                    # )
                    pil_image = Image.open(f"partial-{line}.jpg")
                    # from detect_dmc import detect

                    # detected = detect(f"{area}.jpg")

                    # # command for read barcode API
                    # tr = zxingcpp.read_barcodes(
                    #     pil_image, formats=zxingcpp.BarcodeFormat.DataMatrix
                    # )

                    # if len(tr) == 0:
                    #     tr = zxingcpp.read_barcodes(
                    #         pil_image, formats=zxingcpp.BarcodeFormat.DataMatrix
                    #     )
                    #     if len(tr) == 0:
                    #         tr = zxingcpp.read_barcodes(
                    #             pil_image, formats=zxingcpp.BarcodeFormat.QRCode
                    #         )

                    # if len(tr) == 0:
                    #     tr = zxingcpp.read_barcodes(
                    #         pil_image, formats=zxingcpp.BarcodeFormat.DataMatrix
                    #     )
                    #     if len(tr) == 0:
                    #         tr = zxingcpp.read_barcodes(
                    #             pil_image, formats=zxingcpp.BarcodeFormat.QRCode
                    #         )
                    # if len(tr) > 0:
                    #     for result in tr:
                    #         array_code.append(tr)
                    #         client.publish("mqtt/mes/scanner", f"{result.text}")
                    #         print(
                    #             f"Found {len(tr)} barcodes:"
                    #             f'\n Text:    "{result.text}"'
                    #             f"\n Format:   {result.format}"
                    #             f"\n Position: {result.position}"
                    #         )
                    #         print(40 * "#")
                    # if len(tr) == 0:
                    #     print("Could not find any barcode.")
                    # if len(tr) == 0:
                    #     try:
                    #         print("Try harder!!!")

                    #         # 3. Decode barcodes from an image file
                    #         text_results = reader.decode_file(f"partial-{line}.jpg")
                    #         tr = text_results
                    #         # 4.Output the barcode text.
                    #         if text_results != None and len(text_results) > 0:
                    #             for text_result in text_results:
                    #                 print(
                    #                     "Barcode Format : ",
                    #                     text_result.barcode_format_string,
                    #                 )
                    #                 print(
                    #                     "Barcode Text : ", text_result.barcode_text
                    #                 )
                    #                 print(
                    #                     "Localization Points : ",
                    #                     text_result.localization_result.localization_points,
                    #                 )
                    #                 print("Exception : ", text_result.exception)
                    #                 print("-------------")

                    #         print(40 * "#")
                    #         if len(tr) == 0:
                    #             gray = cv2.cvtColor(partial_line, cv2.COLOR_RGB2GRAY)
                    #             gray = partial_line.copy()
                    #             ret, thresh = cv2.threshold(gray, 180, 225, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                    #             print("Try the best!!!")
                    #             cv2.imwrite('best_try.jpg')
                    #             tr = reader.decode_file('best_try.jpg')
                    #     except Exception as e:
                    #         pass
                    #     except KeyboardInterrupt:
                    #         break
                barcode_data=[]
                panel_data=[]
                pcb_data=[]
                gets = None
                with Image.open("captured_image.jpg") as capture_image:
                    buffered = BytesIO()
                    capture_image.save(buffered, format="JPEG")  # Adjust format as needed
                    # base64.b64encode(buffered.getvalue()).decode()
                    show_message_OLED("Send API")
                    try:
                        api_url = 'http://10.100.27.138:8080/api/detectbarcode'
                        params = {'image':f'{base64.b64encode(buffered.getvalue()).decode()}'}
                        response = requests.post(url=api_url, json=params)
                    except Exception as e:
                        response = None
                    if response is not None:
                        if response.status_code == 200:
                            gets = response.json()
                            if gets:
                                print(gets)
                            else:
                                print("None 1" + gets)
                        else:
                            print(f"{response.status_code}")
                            print(f"{response.reason}")
                    else:
                        print("Response none")
                barcode_data = gets
                # os.remove("captured_image.jpg")
                for item in barcode_data:
                    if re2_obj.match(item):
                        pcb_data.append(item)
                    elif smdReg_obj.match(item):
                        panel_data.append(item)
                print(pcb_data)
                print(panel_data)
                panel_code = ""
                for item in panel_data:
                    panel_code = panel_code + item + ";"
                print(panel_code)
                for item in pcb_data:
                    base_url = "http://fvn-s-ws01.friwo.local:8088/api/ProcessLock/FA/InsertLinkPanel/"
                    endpoint = f"{panel_code}/{item}"
                    # Encode the endpoint to convert URL to URI
                    uri = endpoint.replace(";",quote(";"))
                    url = f"{base_url}{uri}"
                    response = requests.post(url)

                    if response.status_code == 200:
                        print("Request successful")
                        # print("Response:", response.json())
                    else:
                        print("Request failed with status code:", response.status_code)
                        print("Request failed with reason:", response.reason)
                    # if len(tr) == 0:

                    #     gray = cv2.cvtColor(partial, cv2.COLOR_RGB2GRAY)
                    #     ret, thresh = cv2.threshold(
                    #             partial, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
                    #         )
                    #     print("New packages:")
                    #     ret, thresh = cv2.threshold(
                    #         partial, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
                    #     )

                    #     msg = decoder.decode(thresh)
                    #     print(msg)
            show_message_OLED("Done")
        except Exception as e:
            # topLeft, bottomRight = area
            show_message_OLED(f"EXcep: {e}")
            print(e)
            topLeft = (0, 0)
            bottomRight = (1920, 1080)
        
    return array_code


# Initialize library.


# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.


# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
# padding = 2
# shape_width = 120
# Draw a triangle.
# draw.polygon([(x, bottom), (x+shape_width/2, top), (x+shape_width, bottom)], outline=255, fill=0)
# x += shape_width+padding
# # Draw an X. time.sleep(10)
# draw.line((x, bottom, x+shape_width, top), fill=255)
# draw.line((x, top, x+shape_width, bottom), fill=255)
# x += shape_width+padding

# Load default font.
# font = ImageFont.load_default()

# Alternatively load a TTF font.
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

global tr
tr = []
global busy
busy = False


# Callback running on connection
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    client.subscribe("mqtt/mes/wavesoldering")

    client.publish("mqtt/mes/wavesoldering", "Done")

    client.subscribe("mqtt/mes/scanner")

    client.publish("mqtt/mes/scanner", "Test")


# Callback running on new message
def on_message(client, userdata, msg):
    global busy
    if not busy:
        # We print each message received
        # print(json.dump(mqtt.MQTTMessage,msg))
        # print(msg.payload)
        

        if str(msg.payload) == "b'Ready to scan'":
            busy = True
            # time.sleep(3)
            client.publish("mqtt/mes/wavesoldering", "Scanning")
            delete_files_in_directory("images")
            scan()
            client.publish("mqtt/mes/wavesoldering", "Done")
            busy = False
        if str(msg.payload) == "b'Finish'":
            client.publish("mqtt/mes/wavesoldering", "Done")


# Initiate the MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Replace `<USER>`, `<PASSWORD>` and `<XXXXXX>.stackhero-network.com` with your server credentials.
client.username_pw_set("mesclient", "1")

client.connect("10.100.27.67", 1883, 60)


# def pin_event(channel):
#     global busy
#     if GPIO.input(READY) == 1:
#         busy = True
#         tr = scan()
#         busy = False
#         # If pin is high


# GPIO.add_event_detect(
#     READY,
#     GPIO.FALLING,
#     callback=pin_event,

# )

try:
    # Add event detection to the pin

    # print("Monitoring pin", READY, "...")
    # Keep the program running
    client.loop_forever()

except KeyboardInterrupt:
    GPIO.cleanup()
    print("GPIO cleanup completed.")
    busy = False


