import os
import logging
import streamlit as st
from datetime import datetime
from preprocess import read_image, extract_id_card, save_image
from ocr_engine import extract_text
from postprocess import extract_information, extract_information1, extract_college_info
from face_verification import detect_and_extract_face, deepface_face_comparison, get_face_embeddings
from sql_connection import (
    insert_records, 
    fetch_records, 
    check_duplicacy,
    insert_records_aadhar,
    fetch_records_aadhar,
    check_duplicacy_aadhar,
    insert_college_id,
    fetch_college_records,
    check_college_duplicacy
)
import toml
import hashlib

# Logging configuration
logging_str = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "ekyc_logs.log"),
    level=logging.INFO,
    format=logging_str,
    filemode="a"
)

# Load configuration
config = toml.load("config.toml")
db_config = config.get("database", {})
db_user = db_config.get("user")
db_password = db_config.get("password")

def hash_id(id_value):
    """Generate SHA-256 hash of the ID value"""
    hash_object = hashlib.sha256(id_value.encode())
    return hash_object.hexdigest()

def wider_page():
    """Set wider page layout"""
    max_width_str = "max-width: 1200px;"
    st.markdown(
        f"""
        <style>
            .reportview-container .main .block-container{{ {max_width_str} }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    logging.info("Page layout set to wider configuration.")

def set_custom_theme():
    """Apply custom Streamlit theme"""
    st.markdown(
        """
        <style>
            body {
                background-color: #A9D0D5;
                color: #333333;
            }
            .sidebar .sidebar-content {
                background-color: #ffffff;
            }
        </style>                            
        """,
        unsafe_allow_html=True,
    )
    logging.info("Custom theme applied to Streamlit app.")

def sidebar_section():
    """Create sidebar with ID type selection"""
    st.sidebar.title("Select ID Card Type")
    option = st.sidebar.selectbox("", ("PAN", "AADHAR", "COLLEGE ID"))
    logging.info(f"ID card type selected: {option}")
    return option

def header_section(option):
    """Display appropriate header based on ID type"""
    if option == "AADHAR":
        st.title("Extract Data from Aadhar Card")
        logging.info("Header set for Aadhar Card registration.")
    elif option == "PAN":
        st.title("Extract Data from PAN Card")
        logging.info("Header set for PAN Card registration.")
    elif option == "COLLEGE ID":
        st.title("Extract Data from College ID Card")
        logging.info("Header set for College ID Card registration.")

def process_pan_aadhar(image_roi, face_image_path1, option, extracted_text):
    """Process PAN or Aadhar card data"""
    text_info = extract_information(extracted_text) if option == "PAN" else extract_information1(extracted_text)
    text_info['ID'] = hash_id(text_info['ID'])
    
    records = fetch_records(text_info) if option == "PAN" else fetch_records_aadhar(text_info)
    if records.shape[0] > 0:
        st.write(records.shape)
        st.write(records)
    
    is_duplicate = check_duplicacy(text_info) if option == "PAN" else check_duplicacy_aadhar(text_info)
    if is_duplicate:
        st.write(f"User already present with ID {text_info['ID']}")
        return
    
    # Process and store new record
    if isinstance(text_info["DOB"], str):
        text_info["DOB"] = datetime.strptime(text_info["DOB"], "%Y-%m-%d")
    
    text_info["DOB"] = text_info["DOB"].strftime('%Y-%m-%d')
    text_info["Embedding"] = get_face_embeddings(face_image_path1)
    
    if option == "PAN":
        insert_records(text_info)
    else:
        insert_records_aadhar(text_info)
    
    logging.info(f"New user record inserted: {text_info['ID']}")
    st.write(text_info)

def process_college_id(image_roi, face_image_path1, extracted_text):
    """Process College ID card data"""
    text_info = extract_college_info(extracted_text)
    text_info["ID"] = hash_id(text_info.get("contact_no", "") + hash_id(text_info.get("name", "")))
    
    records = fetch_college_records(text_info)
    if records.shape[0] > 0:
        st.write(records.shape)
        st.write(records)
    
    is_duplicate = check_college_duplicacy(text_info)
    if is_duplicate:
        st.write(f"User already present with contact number {text_info.get('contact_no', '')}")
        return
    
    # Process validity date if exists
    if "validity" in text_info and text_info["validity"]:
        try:
            text_info["validity"] = datetime.strptime(text_info["validity"], "%m/%d/%Y").strftime('%Y-%m-%d')
        except ValueError:
            text_info["validity"] = None
    
    text_info["Embedding"] = get_face_embeddings(face_image_path1)
    insert_college_id(text_info)
    
    logging.info(f"New college ID record inserted: {text_info.get('name', '')}")
    st.write(text_info)

def main_content(image_file, face_image_file, option):
    """Main content processing function"""
    if image_file is None:
        st.warning("Please upload an ID card image.")
        logging.warning("No ID card image uploaded.")
        return
    
    face_image = read_image(face_image_file, is_uploaded=True)
    if face_image is None:
        st.error("Face image not uploaded. Please upload a face image.")
        logging.error("No face image uploaded.")
        return
    
    # Process the ID card image
    image = read_image(image_file, is_uploaded=True)
    logging.info("ID card image loaded.")
    image_roi, _ = extract_id_card(image)
    logging.info("ID card ROI extracted.")
    
    # Process face images
    face_image_path2 = detect_and_extract_face(img=image_roi)
    face_image_path1 = save_image(face_image, "face_image.jpg", path=os.path.join("data", "02_intermediate_data"))
    logging.info("Faces extracted and saved.")
    
    # Verify face match
    is_face_verified = deepface_face_comparison(image1_path=face_image_path1, image2_path=face_image_path2)
    logging.info(f"Face verification status: {'successful' if is_face_verified else 'failed'}.")
    
    if not is_face_verified:
        st.error("Face verification failed. Please try again.")
        return
    
    # Process the ID card based on type
    extracted_text = extract_text(image_roi)
    logging.info("Text extracted from ID card.")
    
    if option == "COLLEGE ID":
        process_college_id(image_roi, face_image_path1, extracted_text)
    else:
        process_pan_aadhar(image_roi, face_image_path1, option, extracted_text)

def main():
    """Main application function"""
    # Initialize database connection
    conn = st.connection(
        "local_db",
        type="sql",
        url=f"mysql://{db_user}:{db_password}@localhost:3306/kyc"
    )
    
    # Setup UI
    wider_page()
    set_custom_theme()
    option = sidebar_section()
    header_section(option)
    
    # File uploaders
    image_file = st.file_uploader("Upload ID Card")
    if image_file is not None:
        face_image_file = st.file_uploader("Upload Face Image")
        if face_image_file is not None:
            main_content(image_file, face_image_file, option)

if __name__ == "__main__":
    main()