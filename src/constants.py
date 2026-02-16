from aiogram.types import FSInputFile
import os

logo_photo_path = os.path.join("src", "photos", "logo.png")
virus_total_scan_path = os.path.join("src", "photos", "virus_total_scan.png")

logo_photo = FSInputFile(logo_photo_path)
virus_total_photo = FSInputFile(virus_total_scan_path)

win_link = "https://github.com"
mac_link =  "https://github.com"
linux_link =  "https://github.com"
vt_report = "https://www.virustotal.com/gui/file/ccd7bf5bd7176e5b3f97e6175814acd1eac46abd9b09cd65cecf28225aee1c1b"