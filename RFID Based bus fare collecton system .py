
# Required libraries
import firebase_admin
from firebase_admin import credentials, db
import time
import socket
from mfrc522 import SimpleMFRC522
import serial
from math import radians, sin, cos, sqrt, atan2

# Firebase credentials and database URL
cred = credentials.Certificate("start-rfid-firebase-adminsdk-htwny-5ac4737aef.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://start-rfid-default-rtdb.firebaseio.com'})

# Reference to the RFID path in the database
rfid_ref = db.reference('/rfid_data')

#------------------------------------------------------------------Initialization---------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------

# Initialize RFID reader
rfid_reader = SimpleMFRC522()

#Predefined list of admin RFID cards
admin_ids = ['27010276260']   #replace with multiple ids separated by commas to get multiple admins


# GPS Serial Setup
# gpgga_info = "$GPGGA,"
# ser = serial.Serial("/dev/ttyUSB0")  # Open port with baud rate
# NMEA_buff = 0
# lat_in_degrees = 0
# long_in_degrees = 0

# Fare chart: defining fare as per the distance ranges
# 0-5 km = Rs 20     # 6-10 km = Rs 30       # 11-15 km = Rs 40       # 16-20 km = Rs 50

def calculate_fare(distance):
    if 0 < distance <= 5:
        return 20
    elif 5 < distance <= 10:
        return 30
    elif 10 < distance <= 15:
        return 40
    elif 15 < distance <= 20:
        return 50
    else:
        return 5

#-----------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------FUNCTIONS-----------------------------------------------------------------------

# Function to print the local IP address of the Raspberry Pi
def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unable to get IP"

# Function to read RFID card
def read_rfid():
    try:
        print("Place your RFID card...")
        rfid_id, _ = rfid_reader.read()
        print(f"RFID ID: {rfid_id}")
        return rfid_id
    except Exception as e:
        print(f"Error reading RFID: {e}")
        return None

# Function to get RFID data from Firebase
def get_rfid_data(rfid_id):
    rfid_data = rfid_ref.child(str(rfid_id)).get()
    if rfid_data:
        print(f"Retrieved RFID data from Firebase: {rfid_data}")
        return rfid_data
    else:
        print(f"No data found for RFID ID: {rfid_id}")
        return None

# Function to update the balance on Firebase
def update_balance(rfid_id, new_balance):
    rfid_ref.child(str(rfid_id)).update({'BALANCE': new_balance})
    print(f"Updated balance for RFID ID {rfid_id}. New balance: {new_balance}")

# Function to get GPS info
def get_gps_info():
    global NMEA_buff, lat_in_degrees, long_in_degrees
    max_retries = 10
    attempts = 0
    
    while attempts < max_retries:
        received_data = (str)(ser.readline())
        GPGGA_data_available = received_data.find(gpgga_info)
        if GPGGA_data_available > 0:
            GPGGA_buffer = received_data.split("$GPGGA,", 1)[1]
            NMEA_buff = (GPGGA_buffer.split(','))
            nmea_latitude = float(NMEA_buff[1])
            nmea_longitude = float(NMEA_buff[3])
        
            lat_in_degrees = convert_to_degrees(nmea_latitude)
            long_in_degrees = convert_to_degrees(nmea_longitude)
            return lat_in_degrees, long_in_degrees
        attempts += 1
        print(f"GPS retrieval failed , attempt {attempts}, Retrying in a second...")
        time.sleep(2)
        
    print("Failed to retrieve GPS location after 6 attempts.")
    return None  # Return None if no valid GPS data is received

# Convert raw NMEA string into degree decimal format
def convert_to_degrees(raw_value):
    decimal_value = raw_value / 100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value)) / 0.6
    position = degrees + mm_mmmm
    return position

# Function to calculate distance using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of the Earth in kilometers
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# Function to upload RFID Data to Firebase in JSON format
def upload_rfid_data(rfid_id, rfid_name, rfid_ph, balance=0):
    # Creating the JSON structure for the RFID data
    rfid_data = {
        'info': {
            'ID': rfid_id,
            'NAME': rfid_name,
            'PH': rfid_ph,
            'BALANCE': balance,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    # Uploading the JSON data to Firebase under the 'rfid_data' key
    rfid_ref.child(str(rfid_id)).set(rfid_data)
    
    print(f"RFID data uploaded to Firebase in JSON format: {rfid_data}")



# Function to update the balance on Firebase and write it back to the RFID card
def recharge_rfid(rfid_id, current_balance, amount):
    new_balance = current_balance + amount
    
    # Update the balance in Firebase
    rfid_ref.child(str(rfid_id)).child('info').update({'BALANCE': new_balance})
    print(f"Recharged RFID ID: {rfid_id}. New balance: {new_balance}")
    print(f"Updated RFID card with new balance: {new_balance}")

# Function to verify admin
def verify_admin(rfid_id):
    if rfid_id in admin_ids:
        return True
    else:
        return False
    
# Print connection information
print("Connected to Wi-Fi with IP:", get_local_ip())

# Define the minimum balance required
min_charge = 5  # Minimum charge: Rs 5
journey_started = False  # To track whether a journey is in progress
previous_location = None  # To store the starting GPS location

#-----------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------MAIN LOOP------------------------------------------------------------------------------
while True:
    action = input("1. for Passenger , 2. for Admin officer: ")
    if action not in ['1', '2']:
        print("Invalid input. Please choose '1' if Passenger or '2' Administrator")
        continue

#     if action == '1':  # Passenger case
#         rfid_id = read_rfid()
#         if rfid_id is not None:  # (1) if a card is read
#             rfid_data = get_rfid_data(rfid_id)
#             
#             if rfid_data:  # (2) checks if data exists for this ID
#                 balance = rfid_data.get('BALANCE', 0)
#                 user_name = rfid_data.get('NAME', "user")  # Retrieve the user's name from Firebase
#                 
#                 print(f"Balance is Rs. {balance}")
#                 
#                 if balance < min_charge:  # (3) check if balance is sufficient
#                     print(f"Insufficient balance to start journey.")
#                     continue
#                 else:  # (3) if balance is sufficient
#                     if not journey_started:  # Only allow starting if no journey is in progress
#                         # Start journey
#                         print(f"Starting your journey, {user_name}! Tap again at your destination.")
#                         previous_location = get_gps_info()
# 
#                         if previous_location is None:  # (4 no else case)
#                             print("Error retrieving GPS location. (start)")
#                             continue  # skip if GPS location is not available
# 
#                         print(f"Location saved: {previous_location}")
#                         journey_started = True  # set flag to indicate the journey has started
# 
#                     else:
#                         print("A journey is already in progress. Tap to end the journey.")
#                     
#                     # Wait for user to end journey
#                     if journey_started:  # (5)
#                         print("Tap to end the journey.")
#                         rfid_id = read_rfid()  # Read the RFID again
#                         if rfid_id is not None:  # (6)
#                             print("Ending journey... Please wait for GPS data.")
#                             
#                             current_location = get_gps_info()  # Get current GPS coordinates
#                             if current_location is None:  # (7 no else case)
#                                 print("Error retrieving GPS location. (end)")
#                                 continue  # skip if GPS location is not available
# 
#                             # Calculate distance and fare
#                             distance = haversine(previous_location[0], previous_location[1], current_location[0], current_location[1])
#                             fare = calculate_fare(distance)
#                             
#                             print(f"Distance traveled: {distance:.2f} km, Fare: Rs. {fare}")
# 
#                             # Update balance
#                             new_balance = balance - fare
#                             if new_balance < 0:
#                                 print("Insufficient balance to complete the journey.")
#                             else:
#                                 update_balance(rfid_id, new_balance)
#                                 print("Journey completed. Thank you for traveling!")
#                                 print(f"New balance: Rs. {new_balance}")
# 
#                                 # Reset journey status
#                                 journey_started = False
#                                 previous_location = None
#                             
#             else:
#                 print("User data not found. Please register your card.")
# 
    if action == '1':
        continue
    elif action == '2':  # Admin case
        rfid_id = str(read_rfid())
        if rfid_id is not None:
            if verify_admin(rfid_id):
                print("Welcome \n Admin Verified!")
                
                admin_action = input("1. Recharge card, 2. Update user details, 3. Register new user: ")
                if admin_action == '1':
                    rfid_id_to_recharge = read_rfid()  # Get the RFID ID
                    if rfid_id_to_recharge is not None:
                        user_data = get_rfid_data(rfid_id_to_recharge)  # Retrieve user data from Firebase
                        if user_data and 'info' in user_data:
                            current_balance = user_data['info']['BALANCE']  # Access balance from the 'info' key
                            print(f"Current Balance: Rs. {current_balance}")
        
                            recharge_amount = float(input("Enter amount to recharge: Rs. "))
                            recharge_rfid(rfid_id_to_recharge, current_balance, recharge_amount)  # Updated call
                        break
                    else:
                        print("No user found with that RFID ID.")
                        break

                            
                elif admin_action == '2':
                    rfid_id_to_update = read_rfid() #Get the RFID ID
                    if rfid_id_to_update is not None:
                        user_data = get_rfid_data(rfid_id_to_update)  #Retrieve User data from Firebase
                        if user_data and 'info' in user_data:
                            new_name = input(f"Enter New Name(current: {user_data['info']['NAME']}):]")
                            new_phone = input(f"Enter New Phone(current: {user_data['info']['PH']}):)")
                            rfid_ref.child(str(rfid_id_to_update)).child('info').update({'NAME': new_name, 'PH': new_phone})
                            print(f"User details updated for RFID ID {rfid_id_to_update}.")
                        else:
                            print("No user found with that RFID ID.")

                elif admin_action == '3':
                    new_rfid_id = read_rfid()
#                     #if new_rfid_id is not None:
#                         #Check if already registered user
#                         #existing_user_data = get_rfid_id(new_rfid_id)
#                         
#                         #if existing_user_data:
#                            # print(f"RFID ID {new_rfid_id} is already registered to {existing_user_data['NAME']}.")
                           
#                         #else:
#                             new_name = input("Enter user name: ")
#                             new_phone = input("Enter user phone number: ")
#                             upload_rfid_data(new_rfid_id, new_name, new_phone, balance=0)
                    if new_rfid_id is not None:
                       new_name = input("Enter user name: ")
                       new_phone = input("Enter user phone number: ")
                       upload_rfid_data(new_rfid_id, new_name, new_phone, balance=0)
                    else:
                         print("Invalid action. Please try again.")
            


