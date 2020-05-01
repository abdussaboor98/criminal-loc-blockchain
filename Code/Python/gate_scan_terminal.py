from tkinter import *
import face_recognition
import cv2
import json
import numpy as np
import io
from web3 import Web3
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


location = ""

with open("./PassportData.abi.json") as f:
    pdABI = json.load(f)

with open("./LookOuts.abi.json") as f:
    locABI = json.load(f)

def print_msg():
    print("Button is pressed")

def close_window():
    root.destroy()
    
def isAadharNumber(text):
    if len(text) != 12:
        print("length less than 12 -- Length is: "+str(len(text)))
        return False
    for i in range(0, 11):
        if not text[i].isdecimal():
            print(str(i)+" element is not a decimal")
            return False
    return True

my_provider = Web3.HTTPProvider('https://ropsten.infura.io/v3/42c787749004489ebef7d01077d3a76f')
web3 = Web3(my_provider)
privateKey = "F316A41637A866B201D03B686A1B4D26ADB90D277ED273CA65FD5A7B485B12F2"
pdAddress = web3.toChecksumAddress("0x244d3ce74d2704166fa038fd14b9e57ea4dc6a0d")
pdContract = web3.eth.contract(address=pdAddress, abi=pdABI)
locAddress = web3.toChecksumAddress("0x960e552ba5dcccd56ae18c616b17ea4441bc67e5")
locContract = web3.eth.contract(address=locAddress, abi=locABI)

acct = web3.eth.account.privateKeyToAccount(privateKey)

def setLocation():
    location = locationEntry.get()
    locLabel.configure(text="Location:  "+location,fg='black')
    locationEntry.configure(state=DISABLED)
    locSetBut.configure(state=DISABLED)

def writeDetails(_name, _aadharNo, _passportNo):
    nameEntry.configure(state=NORMAL)
    passportEntry.configure(state=NORMAL)
    aadharEntry.configure(state=NORMAL)
    nameEntry.insert(END, _name)
    passportEntry.insert(END, _passportNo)
    aadharEntry.insert(END, _aadharNo)
    nameEntry.configure(state=DISABLED)
    passportEntry.configure(state=DISABLED)
    aadharEntry.configure(state=DISABLED)

def eraseDetails():
    nameEntry.configure(state=NORMAL)
    passportEntry.configure(state=NORMAL)
    aadharEntry.configure(state=NORMAL)
    nameEntry.delete('0', END)
    passportEntry.delete('0', END)
    aadharEntry.delete('0', END)
    nameEntry.configure(state=DISABLED)
    passportEntry.configure(state=DISABLED)
    aadharEntry.configure(state=DISABLED)

def scanRFID():
    reader = SimpleMFRC522()
    try:
        id,text = reader.read()
        return text
    finally:
        GPIO.cleanup()

def faceVerify(x, y):
    known_face_encoding = [x]
    video_capture = cv2.VideoCapture(0)
    personname = y
    found = False
    timeout = time.time() + 60 * 2
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]
        # Find all the faces and face enqcodings in the frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        # Loop through each face in this frame of video
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encoding, face_encoding, tolerance=0.5)
            name = "Unknown"
            for m in matches:
                print("match value: " + str(m))
            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                name = personname
                found = True
            else:
                found = False
            #print("found: " + str(found))
            # Draw a box around the face
            #cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # Draw a label with a name below the face
            #cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            #font = cv2.FONT_HERSHEY_DUPLEX
            #cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        # Display the resulting image
        #cv2.imshow('Video', frame)
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q') or found == True or time.time() > timeout:
            break
    video_capture.release()
    #cv2.destroyAllWindows()
    return found


def scanCard():
    try:
        scanButton.configure(state=DISABLED)
        setLocation()
        location = locationEntry.get()
        print(location)
        if(location != ""):
            scanLabel.configure(text="Please scan your card!!",fg='black')
            root.update()
            aadharNo = int(scanRFID())
            if (isAadharNumber(str(aadharNo))):
                scanLabel.configure(text="Card Scanned", fg='green')
                root.update()
                if (bool(pdContract.functions.aadharExists(int(aadharNo)).call())):
                    name = pdContract.functions.getName(int(aadharNo)).call()
                    passport = pdContract.functions.getPassportNo(int(aadharNo)).call()
                    writeDetails(name, aadharNo, passport)
                    root.update()
                    byte_encoding = pdContract.functions.getFaceCode(int(aadharNo)).call()
                    data = np.load(io.BytesIO(byte_encoding))
                    facecode = data['x']
                    frMessage.configure(text="Verifying by Facial Recognition")
                    root.update()
                    verified = faceVerify(facecode, name)
                    if verified:
                        frMessage.configure(text="Verified")
                        root.update()
                        status = str(locContract.functions.statusByAadhar(int(aadharNo)).call())
                        print("The scanned passport is: "+status)
                        if(status == "Whitelist"):
                            doorMsg.configure(text="Door Open", fg='green')
                            root.update()
                        else:
                            if status == "Greylist":
                                doorMsg.configure(text="Door Open", fg='green')

                            elif status == "Blacklist":
                                doorMsg.configure(text="Door Close", fg='red')
                            root.update()
                            gas_req = locContract.functions.aadharScan(int(aadharNo), str(location)).estimateGas()
                            print("Gas: " + str(gas_req))
                            construct_txn = locContract.functions.aadharScan(int(aadharNo), str(location)).buildTransaction({
                                'from': acct.address,
                                'nonce': web3.eth.getTransactionCount(acct.address),
                                'gas': gas_req,
                                'gasPrice': web3.toWei('21', 'gwei')})
                            signed = acct.signTransaction(construct_txn)
                            transaction = web3.eth.sendRawTransaction(signed.rawTransaction)
                            result = web3.eth.waitForTransactionReceipt(transaction)
                            if (result.status == 1):
                                print("Scan update sent")
                            else:
                                print("Some error occured while sending scan update")
                                print(result)

                        gas_req = pdContract.functions.addLocation(int(aadharNo), str(location)).estimateGas()
                        print("Gas: "+str(gas_req))
                        construct_txn = pdContract.functions.addLocation(int(aadharNo), str(location)).buildTransaction({
                            'from': acct.address,
                            'nonce': web3.eth.getTransactionCount(acct.address),
                            'gas': gas_req,
                            'gasPrice': web3.toWei('21', 'gwei')})
                        signed = acct.signTransaction(construct_txn)
                        transaction = web3.eth.sendRawTransaction(signed.rawTransaction)
                        result = web3.eth.waitForTransactionReceipt(transaction)
                        if (result.status == 1):
                            print("Location Updated")
                        else:
                            print("Some error occured while updating location")
                            print(result)
                    else:
                        frMessage.configure(text="Failed to recognize.", fg="red")
                        root.update()
                        time.sleep(10)

                else:
                    scanLabel.configure(text="No such Aadhar", fg='red')
                    root.update()
                    time.sleep(10)
                    scanLabel.configure(text="", fg='black')
                    root.update()
            else:
                scanLabel.configure(text="Error while reading card", fg='red')
                root.update()
                time.sleep(10)
                scanLabel.configure(text="", fg='black')
                root.update()
                
        else:
            locLabel.configure(text="Please set the location first", fg='red')
            locSetBut.configure(state=NORMAL)
            locationEntry.configure(state=NORMAL)
    except TypeError:
        scanLabel.configure(text="Some unknown error occured. Please try again.", fg='red')
        root.update()
        time.sleep(5)
    except ValueError:
        scanLabel.configure(text="Invalid RFID card.", fg='red')
        root.update()
        time.sleep(5)
    finally:
        frMessage.configure(text="", fg='black')
        doorMsg.configure(text="")
        scanLabel.configure(text="", fg='black')
        eraseDetails()
        scanButton.configure(state=NORMAL)
        root.update()




root = Tk()
root.title("Passport Scan Terminal")
root.resizable(0, 0)
root.attributes('-fullscreen', True)
padding = 3
dimensions = "{0}x{1}+0+0"
width = root.winfo_screenwidth()-padding
height = root.winfo_screenheight()-padding
root.geometry(dimensions.format(width, height))

top_frame = Frame(root)
top_frame.pack(pady=20)
Label(top_frame, text="Enter location: ").grid(row=0, column=0, columnspan=3, sticky=W)

locationEntry = Entry(top_frame,width=35)
locationEntry.grid(row=0, column=3, sticky=E, columnspan=6)

locSetBut = Button(top_frame, text="Set Location", command=setLocation)
locSetBut.grid(row=0, column=9, sticky=E, padx=5)

#Frames
main_frame = Frame(root)
main_frame.pack()
bottom_frame = Frame(root)
bottom_frame.pack(fill=X, expand='false', side=BOTTOM)
details_frame = Frame(main_frame)

locLabel = Label(main_frame, text="Location")
locLabel.pack()

scanButton = Button(main_frame, text="Scan Next", command=scanCard)
scanButton.pack()

scanLabel = Label(main_frame)
scanLabel.pack()

details_frame.pack(pady=10)

Label(details_frame, text="Person's details:").grid(row=0, column=0, columnspan=5, pady=10)
Label(details_frame, text="Name:").grid(row=2, column=2, columnspan=3, sticky=W)
Label(details_frame, text="").grid(row=3,  column=2, columnspan=3, sticky=W)
Label(details_frame, text="Passport No:").grid(row=4, column=2, columnspan=3, sticky=W)
Label(details_frame, text="").grid(row=5,  column=2, columnspan=3, sticky=W)
Label(details_frame, text="Aadhar No:").grid(row=6, column=2, columnspan=3, sticky=W)

nameEntry = Entry(details_frame, width=35, state=DISABLED)
passportEntry = Entry(details_frame , width=35, state=DISABLED)
aadharEntry = Entry(details_frame, width=35, state=DISABLED)

nameEntry.grid(row=2, column=5, columnspan=6)
passportEntry.grid(row=4, column=5, columnspan=6)
aadharEntry.grid(row=6, column=5, columnspan=6)

frMessage = Label(main_frame)
frMessage.pack(pady=5)

doorMsg = Label(main_frame, font=('', 30, 'bold'))
doorMsg.pack()

#Buttons
quit = Button(bottom_frame, text="Quit", command=close_window,width=20)

quit.pack(padx=5, pady=5)

root.mainloop()
