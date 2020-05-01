from tkinter import *
from tkinter import filedialog
import json
import face_recognition as fc
import io
import numpy as np
from web3 import Web3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

with open("./PassportData.abi.json") as f:
	abi = json.load(f)

def isAadharNumber(text):
    if len(text) != 12:
        return False
    for i in range(0, 11):
        if not text[i].isdecimal():
            return False
    return True

def isPassportNumber(text):
    if len(text) != 8:
        return False
    if not text[0].isupper():
        return False
    if text[0].isdecimal():
        return False
    for i in range(1, 7):
        if not text[i].isdecimal():
            return False
    return True

def print_msg():
    print("Button is pressed")

def close_window():
    root.destroy()

def encodeImage(URL):
    image = fc.load_image_file(URL)
    face_encoding = fc.face_encodings(image)[0]
    output = io.BytesIO()
    np.savez(output, x=face_encoding)
    bytes_encoding = output.getvalue()
    return bytes_encoding

my_provider = Web3.HTTPProvider('https://ropsten.infura.io/v3/42c787749004489ebef7d01077d3a76f')
web3 = Web3(my_provider)
address = web3.toChecksumAddress("0x244d3ce74d2704166fa038fd14b9e57ea4dc6a0d")
privateKey = "F316A41637A866B201D03B686A1B4D26ADB90D277ED273CA65FD5A7B485B12F2"
myContract = web3.eth.contract(address=address,abi=abi)

acct = web3.eth.account.privateKeyToAccount(privateKey)

root = Tk()
root.title("Passport Details Entry Terminal")
root.resizable(0, 0)
root.attributes('-fullscreen', True)
padding = 3
dimensions = "{0}x{1}+0+0"
width = root.winfo_screenwidth()-padding
height = root.winfo_screenheight()-padding
root.geometry(dimensions.format(width, height))
main_frame = Frame(root)
main_frame.place(relx=0.5, rely=0.3, anchor=CENTER)
Label(main_frame, text="Enter the person's details:").grid(row=0, column=0, columnspan=5, pady=10)

bottom_frame = Frame(root)
bottom_frame.pack(fill=X, expand='false', side=BOTTOM)

text_frame = Frame(bottom_frame)
text_frame.pack(fill=X, side=TOP)

#Labels
Label(main_frame, text="Name:").grid(row=2, column=2, columnspan=3, sticky=W)
Label(main_frame, text="Passport No:").grid(row=4, column=2, columnspan=3, sticky=W)
Label(main_frame, text="Aadhar No:").grid(row=6, column=2, columnspan=3, sticky=W)
Label(main_frame, text="Image:").grid(row=8, column=2, columnspan=3, sticky=W)

err_name = Label(main_frame, text="", fg='red', pady=0)
err_name.grid(row=3,  column=5, columnspan=6,  sticky=E, pady=0)
#error Message for passport
err_passport = Label(main_frame, text="", fg='red', pady=0)
err_passport.grid(row=5, column=5, columnspan=6, sticky=E, pady=0)
#error Message for passport
err_aadhar = Label(main_frame, text="", fg='red', pady=0)
err_aadhar.grid(row=7, column=5, columnspan=6, sticky=E, pady=0)

err_image = Label(main_frame, text="", fg='red', pady=0)
err_image.grid(row=9, column=5, columnspan=6, sticky=E, pady=0)

#Entry boxes
nameEntry = Entry(main_frame, width=35)
passportEntry = Entry(main_frame , width=35)
aadharEntry = Entry(main_frame, width=35)
imageEntry = Entry(main_frame, width=25, state=DISABLED)
hiddenLabel = Label(main_frame)

nameEntry.grid(row=2, column=5, columnspan=6)
passportEntry.grid(row=4, column=5, columnspan=6)
aadharEntry.grid(row=6, column=5, columnspan=6)
imageEntry.grid(row=8, column=5, columnspan=3)

def openfile():
	imageEntry.delete(0, END)
	filename = filedialog.askopenfilename(parent = root,filetypes = [('jpeg files','*.jpg')], title="Select Image")
	print(filename)
	imageEntry.configure(state=NORMAL)
	imageEntry.insert(0, filename)
	hiddenLabel.configure(text=filename)
	print(hiddenLabel.cget("text"))
	imageEntry.configure(state=DISABLED)

imgButton = Button(main_frame, width=6, text="Browse", command=openfile)
imgButton.grid(row=8, column=9)

scroll_bary = Scrollbar(text_frame)
out_box= Text(text_frame, width=width,height=float(height/100))
scroll_bary.pack(side=RIGHT, fill=Y)
out_box.pack(side=LEFT, fill=BOTH, anchor=CENTER)
scroll_bary.config(command=out_box.yview)
out_box.config(yscrollcommand=scroll_bary.set)

out_box.insert(END, "\tProgress messages:")
out_box.config(state=DISABLED)


def write_text(widget, message):
    widget.config(state=NORMAL)
    widget.insert(END, message)
    widget.config(state=DISABLED)
    widget.see('end')
    widget.update()

def rfid_send():
    reader = SimpleMFRC522()
    submit.configure(state=DISABLED)
    write.configure(state=DISABLED)
    err_aadhar.configure(text="")
    aadharNo = aadharEntry.get()
    if isAadharNumber(aadharNo):
        try:
            text = aadharNo
            write_text(out_box,"\nNow place your RFID tag to write")
            reader.write(text)
            write_text(out_box,"\nWritten to RFID card")
        finally:
            GPIO.cleanup()
            submit.configure(state=NORMAL)
            write.configure(state=NORMAL)
    else:
        err_aadhar.configure(text="Enter a valid 12 digit Aadhar number")
        submit.configure(state=NORMAL)
        write.configure(state=NORMAL)
    
def data_send():
    submit.configure(state=DISABLED)
    write.configure(state=DISABLED)
    err_aadhar.configure(text="")
    err_passport.configure(text="")
    try:
        name = nameEntry.get()
        passportNo = passportEntry.get()
        aadharNo = aadharEntry.get()
        imageURL = hiddenLabel.cget("text")
        if(name != '' and isAadharNumber(aadharNo) and isPassportNumber(passportNo) and imageURL != ''):
            a_exists = bool(myContract.functions.aadharExists(int(aadharNo)).call())
            p_exists = bool(myContract.functions.passportExists(passportNo).call())
            if a_exists:
                err_aadhar.configure(text="Aadhar number already exists")
                write_text(out_box,"\nThe Aadhar Number you entered already has a Name and Passport linked with it.")
            elif p_exists:
                err_passport.configure(text="Passport number already exists")
                write_text(out_box, "\nThe Passport Number you entered already has a Name and Aadhar linked with it.")
            else:
                encoding = encodeImage(imageURL)
                write_text(out_box, "\nSending Details:")
                write_text(out_box, "\t" + name + " with passport no: " + passportNo + " and Aadhar No: " + aadharNo)
                write_text(out_box, "\nCalculating Gas: ")
                gas_req = myContract.functions.addPerson(name, passportNo, int(aadharNo), encoding).estimateGas()
                write_text(out_box, gas_req)
                construct_txn = myContract.functions.addPerson(name, passportNo, int(aadharNo), encoding).buildTransaction({
                    'from': acct.address,
                    'nonce': web3.eth.getTransactionCount(acct.address),
                    'gas': gas_req,
                    'gasPrice': web3.toWei('21', 'gwei')})
                signed = acct.signTransaction(construct_txn)
                transaction = web3.eth.sendRawTransaction(signed.rawTransaction)
                result = web3.eth.waitForTransactionReceipt(transaction)
                if (result.status == 1):
                    write_text(out_box, "\nSent Details:")
                    write_text(out_box,"\t" + name + " with passport no: " + passportNo + " and Aadhar No: " + aadharNo)
                else:
                    write_text(out_box, "Some error occured please try again...")
        else:
            if name == '':
                err_name.configure(text="Enter a name")
            if(not isAadharNumber(aadharNo)):
                err_aadhar.configure(text="Enter a valid 12 digit Aadhar number")
            if(not isPassportNumber(passportNo)):
                err_passport.configure(text="Enter a valid Passport number")
            if imageURL == '':
                err_image.configure(text="Select an image")
    finally:
        submit.configure(state=NORMAL)
        write.configure(state=NORMAL)

#Buttons
submit = Button(main_frame, text="Submit", command=data_send, width=23)
write = Button(main_frame, text="Write to RFID card", command=rfid_send, width=20)
quit = Button(bottom_frame, text="Quit", command=close_window,width=20)

submit.grid(row=10, column=2, columnspan=4, sticky='w')
write.grid(row=10, column=7, columnspan=4, sticky='w')
quit.pack(padx=5, pady=5)

root.mainloop()
