import pandas as pd
from datetime import datetime
import re

def filter_lines(lines):
    start_index = None
    end_index = None

    for i in range(len(lines)):
       line = lines[i]
       if "INCOME TAX DEPARTMENT" in line and start_index is None:
           start_index = i
       if "Signature" in line:
          end_index = i
          break

    filtered_lines = []
    if start_index is not None and end_index is not None:
        for line in lines[start_index:end_index + 1]:
            if len(line.strip()) > 2:
                filtered_lines.append(line.strip())
    
    return filtered_lines

def create_dataframe(texts):
    lines = filter_lines(texts)
    print("="*20)
    print(lines)
    print("="*20)
    data = []
    name = lines[2].strip()
    father_name = lines[3].strip()
    dob = lines[4].strip()
    for i in range(len(lines)):
        if "Permanent Account Number" in lines[i]:
            pan = lines[i+1].strip()
    data.append({"ID": pan, "Name": name, "Father's Name": father_name, "DOB": dob, "ID Type": "PAN"})
    df = pd.DataFrame(data)
    return df

def extract_information(data_string):
    updated_data_string = data_string.replace(".", "")
    words = [word.strip() for word in updated_data_string.split("|") if len(word.strip()) > 2]
    
    extracted_info = {
        "ID": "",
        "Name": "",
        "Father's Name": "",
        "DOB": "",
        "ID Type": "PAN"
    }

    try:
        id_index = next((i for i, word in enumerate(words) if "Permanent Account Number" in word), -1)
        if id_index != -1 and id_index + 1 < len(words):
            extracted_info["ID"] = words[id_index + 1]

        if len(words) > 7:
            extracted_info["Name"] = words[6]
            extracted_info["Father's Name"] = words[7]

        dob_index = None
        for word in words:
            try:
                dob_index = datetime.strptime(word, "%d/%m/%Y")
                extracted_info["DOB"] = dob_index.strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
    except Exception as e:
        print(f"Error processing PAN card: {e}")
    return extracted_info

def extract_information1(data_string):
    updated_data_string = data_string.replace(".", "")
    words = [word.strip() for word in updated_data_string.split("|") if len(word.strip()) > 2]
    
    extracted_info = {
        "ID": "",
        "Name": "",
        "Gender": "",
        "DOB": "",
        "ID Type": "AADHAR"
    }

    try:
        name_index = next((i for i, word in enumerate(words) if "DOB" in word), -1) - 1
        extracted_info["Name"] = words[name_index] if name_index >= 0 else ""

        gender_index = next((i for i, word in enumerate(words) if "male" in word.lower() or "female" in word.lower()), -1)
        if gender_index != -1:
            gender_word = re.search(r"(male|female)", words[gender_index], re.IGNORECASE)
            extracted_info["Gender"] = gender_word.group(0).capitalize() if gender_word else ""

        aadhar_pattern = re.compile(r'\d{4} \d{4} \d{4}')
        id_number = next((word for word in words if aadhar_pattern.match(word)), "")
        extracted_info["ID"] = id_number
        
        dob_match = next((word for word in words if "DOB:" in word or re.match(r'\d{2}/\d{2}/\d{4}', word)), "")
        if "DOB:" in dob_match:
            dob_match = dob_match.split("DOB:")[1].strip()
        try:
            dob_index = datetime.strptime(dob_match, "%d/%m/%Y")
            extracted_info["DOB"] = dob_index.strftime("%Y-%m-%d")
        except ValueError:
            extracted_info["DOB"] = ""

    except Exception as e:
        print(f"Error processing Aadhar card: {e}")
    
    return extracted_info

def extract_college_info(data_string):
    updated_data_string = data_string.replace(".", "")
    words = [word.strip() for word in updated_data_string.split("|") if len(word.strip()) > 2]
    
    extracted_info = {
        "name": "",
        "course": "",
        "department": "",
        "contact_no": "",
        "validity": "",
        "address": "",
        "father_name": "",
        "ID Type": "COLLEGE ID"
    }

    try:
        # Extract name - typically appears after "Name" keyword
        name_index = next((i for i, word in enumerate(words) if "Name" in word), -1)
        if name_index != -1 and name_index + 1 < len(words):
            extracted_info["name"] = words[name_index + 1]
            # Sometimes name might be split across multiple words
            if name_index + 2 < len(words) and not any(keyword in words[name_index + 2].lower() for keyword in ["course", "department", "b.tech"]):
                extracted_info["name"] += " " + words[name_index + 2]

        # Extract course (B.Tech, etc.)
        course_index = next((i for i, word in enumerate(words) if "B.Tech" in word or "Course" in word), -1)
        if course_index != -1:
            if "B.Tech" in words[course_index]:
                extracted_info["course"] = words[course_index]
            elif course_index + 1 < len(words):
                extracted_info["course"] = words[course_index + 1]

        # Extract department
        dept_index = next((i for i, word in enumerate(words) if "Department" in word or "Dept" in word), -1)
        if dept_index != -1 and dept_index + 1 < len(words):
            extracted_info["department"] = words[dept_index + 1]

        # Extract contact number
        contact_index = next((i for i, word in enumerate(words) if "Contact No" in word or "Phone" in word), -1)
        if contact_index != -1 and contact_index + 1 < len(words):
            # Clean the contact number (remove non-digit characters)
            extracted_info["contact_no"] = re.sub(r'\D', '', words[contact_index + 1])

        # Extract validity date
        validity_index = next((i for i, word in enumerate(words) if "Validity" in word), -1)
        if validity_index != -1 and validity_index + 1 < len(words):
            try:
                # Handle different date formats
                date_str = words[validity_index + 1]
                if '/' in date_str:
                    date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                    extracted_info["validity"] = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Extract address - typically appears after "Address" and spans multiple lines
        address_index = next((i for i, word in enumerate(words) if "Address" in word), -1)
        if address_index != -1:
            address_parts = []
            current_index = address_index + 1
            while current_index < len(words) and not any(keyword in words[current_index].lower() for keyword in ["proctor", "signature", "validity"]):
                address_parts.append(words[current_index])
                current_index += 1
            extracted_info["address"] = " ".join(address_parts)

        # Extract father's name (typically in address line for Indian college IDs)
        if "S/o" in extracted_info["address"] or "D/o" in extracted_info["address"]:
            father_match = re.search(r'(S/o|D/o)\s+(.*?),\s*Vill-', extracted_info["address"])
            if father_match:
                extracted_info["father_name"] = father_match.group(2)

    except Exception as e:
        print(f"Error processing College ID card: {e}")
    
    return extracted_info