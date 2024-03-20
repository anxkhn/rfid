import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep
import sengo
from cs50 import SQL
import subprocess

# Initialize SQLite database
db = SQL("sqlite:///attendance.db")

# Create table if it doesn't exist
db.execute("CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, professor_id TEXT NOT NULL, student_id TEXT NOT NULL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

# Function to mark attendance
def mark_attendance(professor_id, student_id):
    db.execute("INSERT INTO attendance (professor_id, student_id) VALUES (?, ?)", professor_id, student_id)

try:
    while True:
        # Initialize RFID reader
        reader = SimpleMFRC522()
        
        # Fetch professor's RFID information
        print("Please scan your RFID professor card to start the lecture:")
        professor_id, _ = reader.read()
        print(f"Professor ID: {professor_id}")

        # Start the lecture
        print("Lecture has started. Students can now scan their QR codes.")
        sleep(5)  # Let professor move away from the RFID reader

        # Capture QR codes during the lecture using libcamera-still
        for _ in range(5):  # Assuming 5 students
            # Capture image using libcamera-still
            subprocess.run(["libcamera-still", "-o", "qr_code.jpg"])

            # Decode QR code
            qr_code_data = sengo.read('qr_code.jpg')
            if qr_code_data:
                mark_attendance(professor_id, qr_code_data)
                print("Attendance marked for student ID:", qr_code_data)
            else:
                print("No QR code detected.")
            sleep(1)  # Wait between scans

        # End of lecture
        print("Lecture has ended. Please scan your RFID professor card again.")
        professor_id_end, _ = reader.read()
        if professor_id_end == professor_id:
            print("End of session. Attendance has been recorded.")
        else:
            print("Error: RFID scan does not match the professor's ID.")

except KeyboardInterrupt:
    GPIO.cleanup()
