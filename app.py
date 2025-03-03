from passporteye import read_mrz
import streamlit as st
import streamlit as st
from PIL import Image
import os
from datetime import datetime,date
import streamlit as st
from PIL import Image
import os
import fitz  # PyMuPDF (fitz) for PDF handling. Install with: pip install pymupdf
import shutil
import glob
import random
import string
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

def get_temp_dir():
    """Returns a temporary directory that works across platforms."""
    if os.name == 'nt':  # Windows
        return os.environ.get('TEMP', os.environ.get('TMP', 'C:\\temp'))
    else:  # macOS or Linux
        return "/tmp"

directory = get_temp_dir()
# Ensure the directory exists
os.makedirs(directory, exist_ok=True)
st.title("📁 Upload passport Image")
uploaded_file = st.file_uploader("Uploader",type=["jpg", "jpeg", "png", "pdf"])


if uploaded_file is not None:
    # Define the file path
    file_path = os.path.join(directory, uploaded_file.name)

    # Save the uploaded file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File saved to: {file_path}")
    

def upload_passport():
    uploaded_passport_path = None
    directory = "/tmp"
    file_names = os.listdir(directory) # list filenames in directory
    print("Directory:",directory)
    passports = [] # To hold multiple jpg files

    for uploaded_passport in file_names:
        if uploaded_passport.endswith((".jpg",".pdf")):
            print('uploaded_passport:',uploaded_passport)
            uploaded_passport_path = os.path.join(directory,uploaded_passport) # Needs to construct path for the file
            print(uploaded_passport_path)
    return uploaded_passport_path
 

def read_passport():
    passport = upload_passport()  # Get file path
    
    if passport is None:
        st.error("No passport image uploaded! Please upload a valid passport image.")
        return None  # Stop execution if no file

    mrz = read_mrz(passport)
    
    if mrz is not None:
        mrz_data = mrz.to_dict()
        #st.write("MRZ Data:", mrz_data)  # Display extracted data
        return mrz_data  # Return extracted MRZ data
    
    else:
        st.error("MRZ extraction failed. Please upload a clearer image.")
        return None   



def passport_details(file_path):
    # Process image
    mrz = read_mrz(file_path)

    # Obtain image
    mrz_data = mrz.to_dict()
    print('mrz_data:',mrz_data)
    #st.write('Nationality :'+ mrz_data['nationality'])
    surname = mrz_data['surname'].replace("X","") # Remove character X
    #st.write('Surname :',surname)
    #st.write('Given Names :'+ mrz_data['names'])
    passport_number = mrz_data['number'].replace("<","")
    #st.write('Passport Number :'+ passport_number)
    date_of_birth = mrz_data['date_of_birth']
    current_format = "%y%m%d"
    # CAUTION: No error handling!  This will crash if the format is wrong.
    date_object = datetime.strptime(date_of_birth, current_format).date()
    date_of_birth = date_object.strftime("%Y/%m/%d")
    #st.write(f"Date of birth: {date_of_birth}")
    #st.write('Gender :'+mrz_data['sex'])
    expiration_date = mrz_data['expiration_date']
    date_object = datetime.strptime(expiration_date, current_format).date()
    expiration_date = date_object.strftime("%Y/%m/%d")
    #st.write(f"Expiration date: {expiration_date}")
    #print(mrz_data,file=open('passportdata.csv',"a")) # append data to csv
    #return formatted_date,surname
    return surname,passport_number,date_of_birth,expiration_date

def passport_image(file_path):
    st.write("In passport image")
    st.write("uploaded_passport_path:",file_path)
    # Read the image
    image = mpimg.imread(file_path)
    # Convert to grayscale if required
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # Display the image
    # Display grayscale image
    st.image(grayscale_image, caption="Uploaded Passport (Grayscale)", use_container_width=True, channels="GRAY")
    return grayscale_image  # Returning grayscale image if required by OCR
    

    

# days left
def days_left(file_path):  
    _, _, _, expiration_date = passport_details(file_path)
    today = date.today()
    
    # Ensure expiry_date is a datetime.date object
    if isinstance(expiration_date, str):  # If it's a string, convert it to a date
        expiration_date = datetime.strptime(expiration_date, "%Y/%m/%d").date()

    if expiration_date > today:
        days = (expiration_date - today).days
        return f"🗓️ {days} days left until expiry."
    elif expiration_date < today:
        days = (today - expiration_date).days
        return f"⚠️ Passport expired {days} days ago."
    else:
        return "⚠️ Passport is expiring today." 
        

# def website UI using streamlit
def ui():
    st.title("🛂 Passport Expiry Checker")
    name = st.text_input("Enter Name")
    submitted = st.button("Submit")
    # Show buttons only if name is provided
    if name:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Passport Expiry") and file_path:  
                st.write("IN UI calling:")
                surname,passport_number,date_of_birth,expiration_date = passport_details(file_path)  # Function is called only when the button is clicked
                if name == surname:
                    st.write('Surname:',surname)
                    st.write('Passport_Number:',passport_number)
                    st.write('DOB:',date_of_birth)
                    st.write('Passport Expiration Date:',expiration_date)
                    st.success("✅ Passport details fetched.")
                else:
                    st.warning("Names dont match") 
        
        with col2:
            if st.button("Passport Image") and file_path:
                image = passport_image(file_path)
                st.write(image)

        with col3:
            if st.button("Days Left"):
                st.write("IN UI calling days left")
                days = days_left(file_path)
                st.write(days)
                

    return name

upload_passport()
read_passport()
#passport_details()
#passport_image()
ui()
