# E-KYC Project
Welcome to the E-KYC project! This application utilizes modern techniques in computer vision and OCR (Optical Character Recognition) to automate and streamline Know Your Customer (KYC) verification, specifically for Aadhar, PAN, and College ID cards.

## Overview

The E-KYC web app provides an intuitive interface where users can upload their ID card and a face photograph. The system extracts the face from the ID card and compares it with the provided image to validate identity, followed by secure storage of verified data.

### Features

1. **Face Verification**: Uses Haarcascade to detect and crop faces from ID cards and compares them with a user-uploaded face image. If the verification passes, the process continues; otherwise, the user is notified.
   
2. **Optical Character Recognition (OCR)**: On successful face match, the app extracts text from the ID card using EasyOCR.

3. **Database Handling**:
   - Extracted data and face embeddings are checked for duplicacy.
   - If already registered, no duplicate entry is created.
   - Data is securely inserted into a MySQL database.

4. **Face Embeddings**: Utilizes DeepFace and FaceNet to extract face embeddings for enhanced matching accuracy.

## Face Verification Demo



This demonstration shows how mismatched face images trigger verification failure, while matching images allow successful data entry and duplicate detection.

## Full Workflow of Web App



Example: Uploading Aadhar with another person’s face fails face verification. Re-uploading with the correct face allows successful database insertion. Reuploading again confirms the system detects duplicates effectively.

## Technologies Used

- **Streamlit**: For building interactive frontend
- **Computer Vision**: For face detection and matching
- **EasyOCR**: For extracting text from ID cards
- **DeepFace + FaceNet**: For facial embeddings
- **Haarcascade**: For real-time face detection
- **MySQL**: For database storage and retrieval

## Upcoming Improvements

- ✅ **College ID Card Support** (Completed)
- 🔄 **Live Face Capture** via webcam
- 🔐 **Hashed Data Storage** for sensitive user information (completed)

## Prerequisites

- Python 3.x
- MySQL Server (running locally or remotely)

## Setup Instructions

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/YashK13200/E-KYC-OCR-Card-System.git
    cd E-KYC-OCR
    ```

2. **Create a Virtual Environment**:
    ```bash
    python -m venv .venv 
    ```

3. **Activate the Virtual Environment**:
    - On Windows:
      ```bash
      .\.venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```

4. **Install Required Packages**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Add a `config.toml` File**:
    In your project root, create a `config.toml` file with:
    ```toml
    [database]
    user = "your_mysql_user"
    password = "your_mysql_password"
    host = "localhost"
    database = "ekyc"
    ```

6. **Run the App**:
    ```bash
    streamlit run app.py
    ```

## Security Best Practices

- Your `.gitignore` must include:
    ```plaintext
    .venv/
    config.toml
    logs/
    ```
- Never push `config.toml` or `.venv` to GitHub.

## Logging

- The app logs errors and activities in the `logs/` directory.
- This directory is ignored in the repository to protect sensitive information.

## Troubleshooting

- **MySQL errors**: Check if your database and credentials in `config.toml` are correct.
- **Missing packages**: Ensure all dependencies are installed.
- **Table Errors**: Ensure the `aadhar`, `pan`, and other required tables are created beforehand.

---

## Author

**Yash Kumar Kashyap**  
Final Year B.Tech CSE Undergraduate  
CSJM University, Kanpur  
📧   
🔗 [LinkedIn]

## Contributing

Feel free to contribute by opening issues or submitting pull requests! I'm open to feature suggestions, bug fixes, and improvements.

Happy Building! 🚀
