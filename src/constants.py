from aiogram.types import FSInputFile
import os

logo_photo_path = os.path.join("src", "photos", "logo.jpg")
virus_total_scan_path = os.path.join("src", "photos", "virus_total_scan.png")

logo_photo = FSInputFile(logo_photo_path)
virus_total_photo = FSInputFile(virus_total_scan_path)

MAX_LOADING_SCORE = 999999