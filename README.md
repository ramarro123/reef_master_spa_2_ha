# Reef Master Spa → Home Assistant Importer

**Automatically capture and send data from a Reef Master spa screen to Home Assistant using an ESP32-CAM.**

This project provides step-by-step instructions to:

1. Flash an ESP32-CAM to capture images of your spa control screen.
2. Perform OCR on those images.
3. Send the extracted data to Home Assistant.

---

## 📌 Prerequisites

You should already be familiar with the following:

- Programming and flashing ESP32 using Arduino IDE or PlatformIO.
- Running Python or using Docker.
- Using Home Assistant and its APIs.

---

## Setup Overview

### 1. Clone the Repository

```bash
git clone https://github.com/ramarro123/reef_master_spa_2_ha.git
cd reef_master_spa_2_ha
```



---

### 2. Prepare the ESP32-CAM

- Use an ESP32-CAM board with an OV5640 sensor, e.g.:
  - Amazon: [ESP32 CAM Camera Module OV5640 Amazon it](https://www.amazon.it/dp/B0DXFF1GKV)
  - AliExpress: [ESP32 CAM Camera Module OV5640 aliexpress](https://www.aliexpress.com/item/1005007234963618.html) (look similar but not verified)
- In [arduino/main.cpp](https://github.com/ramarro123/reef_master_spa_2_ha/blob/b7876e6f92e96fe249d5a62a347671c6a5dcf474/arduino/main.cpp#L53), update your Wi‑Fi credentials:

```cpp
wifiMulti.addAP("yourSSID1", "yourPassword1");
wifiMulti.addAP("yourSSID2", "yourPassword2");
```

- **Important**: If you're using a different board or camera module, you'll need to adjust board settings and pin definitions.
- Most of the code is based on the example that comes with the ESP32-CAM, so refer to that documentation as needed.

---


### 3. 3D-Print a Mount

- The `stl/` folder contains two STL files for a mounting bracket.
- Print them and assemble your ESP32-CAM using the printed mount.

the final result should look like <add img>

---


### 4. Test the Camera

1. Power on your ESP32-CAM. 
2. Access the device’s web interface using its IP address. the browser should look lik ![](img/screenshot/esp32%20control.png)
3. Adjust capture settings and click **Get Still**.
4. Settings are temporary—note them down or embed defaults in firmware:

```cpp
// EXTRA CONFIG
Serial.println("Apply my personal preference");
// Adjusted values here...
```

---

### 5. OCR + Data Extraction

You have two options to run the Python extraction script:

#### A) Docker (recommended)

- Suitable for production setups.
- Navigate to `python/` and build the Docker image (Dockerfile included).
- Runs indefinitely alongside Home Assistant.

#### B) Python Virtual Environment

- Install dependencies:

```bash
pip install opencv-python easyocr requests numpy
```

---

### 6. Run & Validate Extraction

- Execute the extraction script.
- It saves debug PNGs in the `data/` folder to verify processing steps:

  1. Initial frame capture
  2. Preprocessed/enhanced image
  3. Final segmented image passed to OCR
  4. Zoomed-in version for clarity

Check alignment and OCR performance—adjust offsets in `extract.py` if necessary.

this is how the data got extracted
![](img/screenshot/immagine.png)
and then analized in various step

![](img/data/debug_CA.png)
![](img/data/debug_CA_enhanced.png)
![](img/data/debug_CA_processed.png)

this is the final step, the one used by OCR, if this is good, normally OCR result will be good :)

![](img/data/debug_CA_zoomed.png)

---

## 🛠 Troubleshooting

- Post debug images (e.g., `data/debug_*.png`) on the Reef2Reef thread for help:

> https://www.reef2reef.com/threads/kamoer-reef-master-spa-ha-integration.1116295/

- Make sure your camera view matches the expected alignment—offsets must be tweaked in `extract.py` if necessary.

---

## Summary

| Step        | Description                                      |
|-------------|--------------------------------------------------|
| 1. Clone    | Download the project                            |
| 2. Flash    | Install firmware on ESP32-CAM                   |
| 3. Print    | 3D-print and mount your hardware                |
| 4. Capture  | Test camera settings in the web interface       |
| 5. Run OCR  | Use Docker or Python to extract spa screen data |
| 6. Integrate| Send extracted values to Home Assistant         |
