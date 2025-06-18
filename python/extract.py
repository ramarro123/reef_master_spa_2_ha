import cv2
import easyocr
import requests
import time
import numpy as np
import os
import glob
import sys



# Coordinate corrette (grazie a te!)
zones = {
    "CA": (80, 464, 300, 95),
    "KH": (920, 464, 300, 95),
    "PO4": (640, 650, 300, 95),
    "NO3": (360, 670, 300, 95),
    "NO2": (100, 670, 300, 95),

}

VALID_RANGES = {
    "CA": (200, 500),  # Calcio
    "MG": (1000, 1600),  # Magnesio
    "KH": (3, 15),  # Durezza carbonatica
    "NO2": (0, 1),  # Nitriti
    "NO3": (0, 50),  # Nitrati
    "PO4": (0, 5),  # Fosfati
    "FE": (0, 0.5),  # Ferro
}


def is_valid(key, value):
    try:
        value_float = float(value)
    except ValueError:
        return False

    if key.upper() not in VALID_RANGES:
        return False  # chiave sconosciuta

    min_val, max_val = VALID_RANGES[key.upper()]
    return min_val <= value_float <= max_val


def invia_a_home_assistant(sensor_id, friendly_name, value):
    url = f"https://YOUR_HOME_ASSISTANT_IP/api/states/sensor.reef_spa_{sensor_id}"
    headers = {
        "Authorization": "Bearer YOUR_HOME_ASSISTANT_KEY",
        "Content-Type": "application/json"
    }
    payload = {
        "state": str(value),
        "attributes": {
            "unit_of_measurement": "",
            "friendly_name": friendly_name
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"Sent {sensor_id}: {value} → {response.status_code}")
    if not response.ok:
        print("Response:", response.text)


def scan():
    files = glob.glob('data/*')
    for f in files:
        os.remove(f)

    # URL dell'immagine (sostituisci con la tua URL)
    image_url = "http://192.168.1.90/capture"

    # Scarica e salva su disco
    response = requests.get(image_url)
    with open("immagine.png", "wb") as f:
        f.write(response.content)

    image = cv2.imread("immagine.png")

    results = {}

    for key, (x, y, w, h) in zones.items():
        roi = image[y:y + h, x:x + w]
        # Salva per debug
        cv2.imwrite(f"data/debug_{key}.png", roi)

        # Converti in scala di grigi
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Migliora contrasto con CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        cv2.imwrite(f"data/debug_{key}_enhanced.png", gray)


      #  gray = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
      #  cv2.imwrite(f"data/debug_{key}_bilateral.png", gray)

     #  gray = cv2.fastNlMeansDenoising(gray, h=30)
      #  cv2.imwrite(f"data/debug_{key}_denoise.png", gray)

       # gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, blockSize=15, C=10)
        #cv2.imwrite(f"data/debug_{key}_thresh.png", gray)


        kernel = np.ones((2, 2), np.uint8)
        gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        cv2.imwrite(f"data/debug_{key}_processed.png", gray)




        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(f"data/debug_{key}_zoomed.png", gray)



        # OCR con dettaglio completo
        result = reader.readtext(gray, detail=1)

        # Estrai prima stringa con cifre
        best = "N/A"
        for box, text, conf in result:
            if any(c.isdigit() for c in text):
                best = text.strip()
                break

        results[key] = best

    # Stampa finale
    print("Valori estratti:")
    for key in results:
        if is_valid(key, results[key]):
            invia_a_home_assistant(sensor_id=key.lower(), friendly_name=key, value=results[key])
        else:
            print(f"❌ Ignorato {key}: '{results[key]}' (fuori range o non valido)")


# Inizializza EasyOCR
reader = easyocr.Reader(['en'])
while True:
    try:
        scan()
        time.sleep(60 * 5)
    except KeyboardInterrupt:
        print("Bye")
        sys.exit()
    except:
        print("qualcosa è andato storto, riproviamo")