#!/usr/bin/python
from tkinter import *
import mysql
import mysql.connector
from datetime import datetime
import time
import Reader_2 as reader
import servo_C_angle as servo
import RPi.GPIO as GPIO
import shutil
import tkinter as tk
from tkinter import ttk,messagebox #Messagebox, küçük bilgilendirme penceresi göstermek için. Üstündeki OK tuşu ile kapatılıyor.
from tkinter import *
import sys
#import customtkinter #Bunun içinde daha hoş görünen button'lar vb var.
import RPi.GPIO as gpio
import servo_for_door_and_buzzer

import os

import cv2
from imutils.video import VideoStream
from imutils.video import FPS
import imutils
from PIL import ImageTk, Image

import netifaces as ni
ni.ifaddresses('wlan0')
ip = ni.ifaddresses('wlan0')[2][0]['addr']

##BUTTON CLICK FUNCTIONS##
def introduce_resident():
	root.geometry('800x480') #The resolution of the screen is 800x400
	#root.iconbitmap(r"\home\pi\Desktop\tkinter\look_icon.ico")
	root.configure(background='#5F9EA0')
	root.title('Introducing Resident Screen')

	resident_info = [] #will hold name e-mail and RFID card code


	def get_text():

		if not resident_info:
			resident_info.append(my_text.get())
			newpath = ("/home/pi/Desktop/FINAL_DEMO/tkinter/temp_test")
			if not os.path.exists(newpath):
				os.makedirs(newpath)
			
			resident_info_file = open("/home/pi/Desktop/FINAL_DEMO/tkinter/resident_info.txt","w+")
			resident_info_file.write(resident_info[0]+"\n")
			resident_info_file.close()
			my_text.delete(0, 'end')
			print(resident_info)
			screen_text_instruction.config(text="Please enter the e-mail address belongs to " + resident_info[0]+".")

		elif len(resident_info)==1:
			resident_info.append(my_text.get())
			#Writing to file
			resident_info_file = open("/home/pi/Desktop/FINAL_DEMO/tkinter/resident_info.txt","a+")
			resident_info_file.write(resident_info[1]+"\n")
			resident_info_file.close()
			#End of writing to
			my_text.delete(0, 'end')
			print(resident_info)

			#Klavye vb. ne varsa, tüm widget'ları temizliyoruz. İsim ve mail alımından sonra gerek kalmıyor çünkü.
			for widget in root.winfo_children():
				widget.destroy()
            
			get_text()
		elif len(resident_info)==2:
			global re_rfid
			re_rfid = 0

			def rfid_insert():
				global re_rfid
				if re_rfid == 0:
					screen_text_instruction_next = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),
                                                         text="Please hold the RFID card you want to assign for guests and hit the button below while holding it.")
					screen_text_instruction_next.place(relx=0.5, anchor='center', y=80)

                    # RFID logo placement#
					img_canvas = Canvas(root, height=200, width=200, bg="#5F9EA0",
                                        highlightthickness="0")
                    # Then, we actually create the image file to use (it has to be a *.gif)
					rfid_img = PhotoImage(
                        file=r"/home/pi/Desktop/tkinter/rfid_png_200x200.png")  # <-- you will have to copy-paste the filepath here, for example 'C:\Desktop\pic.gif'
                    # Finally, we create the image on the canvas and then place it onto the main window
					img_canvas.image = rfid_img
					img_canvas.create_image(200, 0, anchor=NE, image=rfid_img)
					img_canvas.place(relx=0.5, anchor='center', y=200)
                    # End of RFID logo placement#
					re_rfid = 1
					print(re_rfid)
					Button(root, text='I am holding the RFID card.', bg='#6495ED', font=('arial', 10, 'normal'),
                           command=rfid_insert).place(x=100, y=300, height=50, width=400)

                # rfid_insert()
				elif re_rfid == 1:
					# Reading from RFID
					reader.card_read()
					re_rfid = reader.id
					rfid_insert()
				elif re_rfid == None:
					for widget in root.winfo_children():
						widget.destroy()
					screen_text_instruction_next = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),
                                                         text="You didn't hold a RFID card in time!")
					screen_text_instruction_next.place(relx=0.5, anchor='center', y=80)
					Button(root, text='Press here to return home screen.', bg='#6495ED', font=('arial', 10, 'normal'),
                           command=lambda: [clear_frame(), return_home_screen()]).place(x=100, y=300, height=50, width=400)


				else:
					for widget in root.winfo_children():
						widget.destroy()

					db = mysql.connector.connect(host="localhost", user="admin", passwd="1234", database="security")
					cursor_re = db.cursor(dictionary=True)
					cursor_re.execute("SELECT * FROM residents WHERE RFID= '%s'" % (re_rfid))
					cursor_re.fetchall()
					re_num = cursor_re.rowcount  # rowcount eşleşen row sayısını veriyor. Yani 1'den az ise eşleşen yok demek.

					cursor_guest = db.cursor(dictionary=True)
					cursor_guest.execute("SELECT * FROM guests WHERE RFID= '%s'" % (re_rfid))
					cursor_guest.fetchall()
					guest_num = cursor_guest.rowcount

					if re_num < 1 and guest_num < 1:
						resident_info.append(re_rfid)
						screen_text_instruction = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),
                                                        text="Do you want to assign this RFID card for "+ resident_info[0]+ ".")
						screen_text_instruction.place(x=170, y=100)

						rfid_screen_text = Label(root, bg='#5F9EA0', font=('arial', 12, 'bold'), text="RFID code: ")
						rfid_screen_text.place(x=170, y=200)
						Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'), text=re_rfid).place(x=258, y=200)

                        ##MYSQL PART##
						def insert_re():
							db = mysql.connector.connect(host="localhost", user="admin", passwd="1234", database="security")
							mycursor = db.cursor()
							mycursor.execute("INSERT INTO residents (name, mail, RFID) VALUES (%s, %s, %s)", (resident_info[0], resident_info[1], resident_info[2]))
							db.commit()
                        ##END OF MYSQL PART##
                        
						introduce_re_yes_button = Button(root, text='Yes', bg='#6495ED', font=('arial', 10, 'normal'),
                                                            command=lambda: [insert_re(), clear_frame(),
                                                                             get_text()])
						introduce_re_yes_button.place(x=500, y=270, height=50, width=150)

						introduce_re_no_button = Button(root, text='No', bg='#6495ED', font=('arial', 10, 'normal'),
                                                           command=lambda: [clear_frame(), return_home_screen()])
						introduce_re_no_button.place(x=150, y=270, height=50, width=150)

					else:
						screen_text_instruction_fail = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),
                                                             text="The RFID card that you held has been already introduced!\n\nPlease try with a different RFID card or return to home screen.")
						screen_text_instruction_fail.place(relx=0.5, anchor='center', y=150)

						re_rfid = 0
						different_rfid = Button(root, text='Try Different RFID', bg='#6495ED', font=('arial', 10, 'normal'),
                                                command=lambda: [clear_frame(), rfid_insert()])
						different_rfid.place(x=500, y=270, height=50, width=150)

						exit_to_home_screen = Button(root, text='Exit', bg='#6495ED', font=('arial', 10, 'normal'),
                                                     command=lambda: [clear_frame(), return_home_screen()])
						exit_to_home_screen.place(x=150, y=270, height=50, width=150)

			rfid_insert()
		elif len(resident_info)==3:
			screen_text_instruction_next = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),
                                                         text="Press the button below and get in front of the camera to introduce your face to system.")
			screen_text_instruction_next.place(relx=0.5, anchor='center', y=80)
			resident_info.append("HOLDER")
			resident_info_file = open("/home/pi/Desktop/FINAL_DEMO/tkinter/resident_info.txt","a+")
			resident_info_file.write("additional line"+"\nA")
			resident_info_file.close()
			Button(root, text='Face Introduction', bg='#6495ED', font=('arial', 10, 'normal'),
                           command=lambda: [clear_frame(), get_text()]).place(x=100, y=300, height=50, width=400)
		elif len(resident_info)==4:
			clear_frame()
			resident_info.append("HOLDER")
			
			success_text = Label(root, bg='#5F9EA0', font=('arial', 12, 'bold'),text="After 10 seconds, face introduction will begin! Please get in front of the camera.")
			success_text.pack(pady=30)

			##Successful logo##
			img_canvas = Canvas(root, height=220, width=220, bg="#5F9EA0",highlightthickness="0")
			face_logo = PhotoImage(
				file=r"/home/pi/Desktop/tkinter/face_recognition_200x200.png")
			img_canvas.image = face_logo
			img_canvas.create_image(220, 0, anchor=NE, image=face_logo)
			img_canvas.pack(pady=20)
			##End of  logo##
			def buzzer():
				Buzz = gpio.PWM(11, 700)
				Buzz.start(40)
				time.sleep(1.5)
				Buzz.stop()
			root.after(10000,lambda: [clear_frame(),buzzer() ,get_text()])
            
 
		elif len(resident_info)==5:
			time_start=time.time()
			cam_label = Label(root, width=740, height=400)
			cam_label.pack(pady=20)
			resident_info_file = open("/home/pi/Desktop/FINAL_DEMO/tkinter/resident_info.txt","a+")
			resident_info_file.write("additional line"+"\nA")
			resident_info_file.close()
            #cap = cv2.VideoCapture(0)
			#cap = VideoStream("http://IP:8000/stream.mjpg").start()
			cap = VideoStream("http://"+ ip+ ":8000/stream.mjpg").start()
            #cap.set(3, 640)
            #cap.set(4, 480)

			def show_cam():
                # Get the latest frame and convert into Image
				frame_cam = cap.read()
				frame_cam = cv2.flip(frame_cam, 1)
				frame_cam = imutils.resize(frame_cam, width = 760, height=400)
				cv2image = cv2.cvtColor(frame_cam, cv2.COLOR_BGR2RGB)
				img = Image.fromarray(cv2image)
                # Convert image to PhotoImage
				imgtk = ImageTk.PhotoImage(image=img)
				cam_label.imgtk = imgtk
				cam_label.configure(image=imgtk)
                # Repeat after an interval to capture continiously
				if time.time() > time_start +20:
					clear_frame()
					return_home_screen()
                
				cam_label.after(20, show_cam)

			show_cam()

	screen_text_instruction = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'), text="Please enter the name and surname of the resident that you want to introduce.")#width height girebiliyorsun bunun için de alttaki text box'a girdiğimiz gibi. Mantığı aynı, pixel değeri değil buradakiler.
	screen_text_instruction.place(relx=0.5, anchor='center', y=30)
	my_text = Entry(root, font=('arial', 10, 'normal'), width=40)
	my_text.pack(pady=50)


	get_name_text_button = Button(root, text='Enter', bg='#6495ED', font=('arial', 10, 'normal'),command= get_text)
	get_name_text_button.place(x=410, y=80, height=50, width=150)

	introduce_resident_exit_button = Button(root, text='Exit', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), return_home_screen()])
	introduce_resident_exit_button.place(x=240, y=80, height=50, width=150)






	####Keyboard Part####
		Keyboard_Buttons = ["1","2","3","4","5","6","7","8","9","0","q", "w", "e", "r", "t", "y", "u", "i", "o", "p","a","s","d","f","g","h","j","k","l","@","z","x","c","v","b","n","m","."]
	Keyboard_Buttons_Caps = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Q", "W", "E", "R", "T", "Y", "U", "I", "O","P", "A", "S", "D", "F", "G", "H", "J", "K", "L", "@", "Z", "X", "C", "V", "B", "N", "M", "."]




	def select(value):
		global isUpperCase
		if (value=="<---"):
			written_text=my_text.get()
			last_char_index=len(written_text)-1
			my_text.delete(last_char_index, "end")
		if (value == "SPACE"):
			my_text.insert("insert", " ")

		if (value == "CapsLock"):

			newkeys=[]
			if (isUpperCase==False):
				newkeys=Keyboard_Buttons_Caps
				isUpperCase=True

			elif (isUpperCase==True):
				newkeys = Keyboard_Buttons
				isUpperCase=False

			for buttonwidget in FourRowsButtonWidgets:
				buttonwidget.destroy()

			FourRowsButtonWidgets.clear()
			# Numbers Row
			key_x = 100
			key_y = 155
			for button in newkeys[0:10]:  # To draw number keys
				command = lambda x=button: select(x)
				a=Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
					   command=command)
				a.place(x=key_x, y=key_y)
				FourRowsButtonWidgets.append(a)
				key_x = key_x + 60

			# First row
			key_x = 100
			key_y = key_y + 55
			for button in newkeys[10:20]:
				command = lambda x=button: select(x)
				a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
						   command=command)
				a.place(x=key_x, y=key_y)
				FourRowsButtonWidgets.append(a)
				key_x = key_x + 60

			# Second row
			key_x = 100
			key_y = key_y + 55
			for button in newkeys[20:30]:
				command = lambda x=button: select(x)
				a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
						   command=command)
				a.place(x=key_x, y=key_y)
				FourRowsButtonWidgets.append(a)
				key_x = key_x + 60

			# Last row
			key_x = 100
			key_y = key_y + 55
			for button in newkeys[30:]:
				command = lambda x=button: select(x)
				a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
						   command=command)
				a.place(x=key_x, y=key_y)
				FourRowsButtonWidgets.append(a)
				if (button == "V" or button == "v"):  # Space'e arada yer bırakmak için v'den önce iki tuşluk boşluk bırakıyorum
					key_x = key_x + 180
				else:
					key_x = key_x + 60

		elif (value !="<---" and value != "SPACE"):
			my_text.insert("insert", value)


	#CapsLock
	key_x = 100
	key_y = 100
	Button(root, text="CapsLock", width=3, bg='black', fg='white', relief="raised", padx=39, pady=9, bd=9,
		   command=lambda: select("CapsLock")).place(x=key_x,y=key_y)

	global isUpperCase
	isUpperCase = False

	#Backspace
	key_x = 580
	key_y = 100
	Button(root, text="<---", width=3, bg='black', fg='white', relief="raised", padx=39, pady=9, bd=9,
			   command=lambda: select("<---")).place(x=key_x, y=key_y)


	FourRowsButtonWidgets = []
	#Numbers Row
	key_x=100
	key_y= key_y+55
	for button in Keyboard_Buttons[0:10]: # To draw number keys
		command = lambda x=button: select(x)
		a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
				   command=command)
		a.place(x=key_x, y=key_y)
		FourRowsButtonWidgets.append(a)
		key_x = key_x + 60

	#First row
	key_x = 100
	key_y = key_y+55
	for button in Keyboard_Buttons[10:20]:
		command = lambda x=button: select(x)
		a=Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
			   command=command)
		a.place(x=key_x, y=key_y)
		FourRowsButtonWidgets.append(a)
		key_x = key_x + 60

	#Second row
	key_x = 100
	key_y = key_y+55
	for button in Keyboard_Buttons[20:30]:
		command = lambda x=button: select(x)
		a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
				   command=command)
		a.place(x=key_x, y=key_y)
		FourRowsButtonWidgets.append(a)
		key_x = key_x + 60

	# Last row
	key_x = 100
	key_y = key_y+55
	for button in Keyboard_Buttons[30:]:
		command = lambda x=button: select(x)
		a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
				   command=command)
		a.place(x=key_x, y=key_y)
		FourRowsButtonWidgets.append(a)
		if (button =="v"):
			key_x = key_x+180
		else:
			key_x = key_x + 60

	#Space button#
	key_x = 340
	Button(root, text="SPACE", width=3, bg='black', fg='white', relief="raised", padx=39, pady=9, bd=9, command=lambda: select("SPACE")).place(x=key_x, y=key_y)

	####End of Keyboard Part####


def introduce_guest():
	root.geometry('800x480')
	##root.iconbitmap(r"/home/pi/Desktop/tkinter/look_icon.ico")
	root.configure(background='#5F9EA0')
	root.title('Introducing Guest Screen')

	global guest_rfid
	guest_rfid = 0  # Sadece read değil alt fonksiyonda write da yaptığından global olması gerekiyor.

	def rfid_insert():
		global guest_rfid
		if guest_rfid == 0:
			screen_text_instruction_next = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),
												 text="Please hold the RFID card you want to assign for guests and hit the button below while holding it.")
			screen_text_instruction_next.place(relx=0.5, anchor='center', y=80)

			# RFID logo placement#
			img_canvas = Canvas(root, height=200, width=200, bg="#5F9EA0",
								highlightthickness="0")  # bg: ayrılan kutucuğun rengi, highlighthick frame kalınlığı, highlightbackground frame rengi.
			# Then, we actually create the image file to use (it has to be a *.gif)
			rfid_img = PhotoImage(
				file=r"/home/pi/Desktop/tkinter/rfid_png_200x200.png")  # <-- you will have to copy-paste the filepath here, for example 'C:\Desktop\pic.gif'
			# Finally, we create the image on the canvas and then place it onto the main window
			img_canvas.image = rfid_img  # Fonksiyon içlerinde photo eklediğin zaman bu line'ı yazman gerekiyor. Referance tutuyor bu photo'ya. Image object'inde böyle bir durum var TKinter'da. Garbagecollector siliyormuş.
			img_canvas.create_image(200, 0, anchor=NE, image=rfid_img)
			img_canvas.place(relx=0.5, anchor='center', y=200)
			# End of RFID logo placement#
			guest_rfid = 1
			print(guest_rfid)
			Button(root, text='I am holding the RFID card.', bg='#6495ED', font=('arial', 10, 'normal'),
				   command=rfid_insert).place(x=100, y=300, height=50, width=400)

		# rfid_insert()
		elif guest_rfid == 1:
			# Reading from RFID
			reader.card_read()
			guest_rfid = reader.id
			rfid_insert()
		elif guest_rfid == None:
			for widget in root.winfo_children():
				widget.destroy()
			screen_text_instruction_next = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),
												 text="You didn't hold a RFID card in time!")
			screen_text_instruction_next.place(relx=0.5, anchor='center', y=80)
			Button(root, text='Press here to return home screen.', bg='#6495ED', font=('arial', 10, 'normal'),
				   command=lambda: [clear_frame(), return_home_screen()]).place(x=100, y=300, height=50, width=400)


		else:
			for widget in root.winfo_children():
				widget.destroy()

			db = mysql.connector.connect(host="localhost", user="admin", passwd="1234", database="security")
			cursor_re = db.cursor(dictionary=True)
			cursor_re.execute("SELECT * FROM residents WHERE RFID= '%s'" % (guest_rfid))
			cursor_re.fetchall()
			re_num = cursor_re.rowcount

			cursor_guest = db.cursor(dictionary=True)
			cursor_guest.execute("SELECT * FROM guests WHERE RFID= '%s'" % (guest_rfid))
			cursor_guest.fetchall()
			guest_num = cursor_guest.rowcount

			if re_num < 1 and guest_num < 1:
				screen_text_instruction = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),
												text="Do you want to assign this RFID card for the guests?")
				screen_text_instruction.place(x=170, y=100)

				rfid_screen_text = Label(root, bg='#5F9EA0', font=('arial', 12, 'bold'), text="RFID code: ")
				rfid_screen_text.place(x=170, y=200)
				Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'), text=guest_rfid).place(x=258, y=200)

				##MYSQL PART##
				def insert_guest():
					db = mysql.connector.connect(host="localhost", user="admin", passwd="1234", database="security")
					mycursor = db.cursor()
					mycursor.execute("INSERT INTO guests (RFID) VALUES (%s)", (guest_rfid,))
					db.commit()

				##END OF MYSQL PART##

				introduce_guest_yes_button = Button(root, text='Yes', bg='#6495ED', font=('arial', 10, 'normal'),
													command=lambda: [insert_guest(), clear_frame(),
																	 return_home_screen()])
				introduce_guest_yes_button.place(x=500, y=270, height=50, width=150)

				introduce_guest_no_button = Button(root, text='No', bg='#6495ED', font=('arial', 10, 'normal'),
												   command=lambda: [clear_frame(), return_home_screen()])
				introduce_guest_no_button.place(x=150, y=270, height=50, width=150)

			else:
				screen_text_instruction_fail = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),
													 text="The RFID card that you held has been already introduced!\n\nPlease try with a different RFID card or return to home screen.")
				screen_text_instruction_fail.place(relx=0.5, anchor='center', y=150)

				guest_rfid = 0
				different_rfid = Button(root, text='Try Different RFID', bg='#6495ED', font=('arial', 10, 'normal'),
										command=lambda: [clear_frame(), rfid_insert()])
				different_rfid.place(x=500, y=270, height=50, width=150)

				exit_to_home_screen = Button(root, text='Exit', bg='#6495ED', font=('arial', 10, 'normal'),
											 command=lambda: [clear_frame(), return_home_screen()])
				exit_to_home_screen.place(x=150, y=270, height=50, width=150)

	rfid_insert()


def check_logs():

	root.geometry('800x480')
	#root.iconbitmap(r"/home/pi/Desktop/tkinter/look_icon.ico")
	root.configure(background='#5F9EA0')
	root.title('Show Logs Screen')
	columns = ('order', 'name', 'activity', 'date','log_id') #Order dediğimiz normal sıralamadaki solundaki sayı olacak. Log id ise mysql database'deki entry'nin unique sayısı olacak ve bunu arayüzde göstermeyeceğiz. Bunu da alıyorum çünkü entry delete etmek için gerecek log id değeri. Onunla specific entry'i seçip delete edeceğiz.

	tree = ttk.Treeview(root, columns=columns, show='headings')
	tree.column('order', width=50, minwidth=50)
	tree.column('name', width=350,minwidth=350)
	tree.column('activity', width=150,minwidth=150)
	tree.column('date', width=240,minwidth=240)
	tree.column('log_id')

	tree.bind('<Motion>', 'break')

	#Create Headings
	tree.heading('order', text='Order')
	tree.heading('name', text='Name')
	tree.heading('activity', text='Activity', anchor="center")
	tree.heading('date', text='Date')

	tree_style_config=ttk.Style()
	tree_style_config.configure('Treeview', rowheight=20)
	tree_style_config.configure('Treeview',  font=('Arial', 9))

	#Gettin All Logs From Database and Inserting Treeview
	db = mysql.connector.connect(host="localhost", user="admin", passwd="1234", database="security")
	mycursor = db.cursor(dictionary=True)
	flag = 1
	mycursor.execute("SELECT * FROM log")
	mycursor.fetchall()

	if mycursor.rowcount >= 1:
		mycursor.execute("SELECT * FROM log")
		list = mycursor.fetchall()
		for x in list:
			tree.insert(parent='', index=flag,values=(flag,x["name"], x["activity"], x["date"].strftime("%d/%m/%y, %H:%M:%S"), x['log_id'])) #Parent'a root yazınca olmuyor parent='' yazmak gerekiyor.
			flag += 1

	#Scroolbar
	scrool = ttk.Scrollbar(root, orient="vertical",command=tree.yview)
	tree.configure(yscrollcommand=scrool.set)
	scrool.pack(side='right', fill='y')

	tree.pack(ipady=40)
	check_log_exit_button = Button(root, text='Exit', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), return_home_screen()])
	check_log_exit_button.place(x=60, y=320, height = 50, width = 150)

	##Are you sure window##
	def are_you_sure():
		try:
			selected_item = tree.selection()[0]
			selected_item_info = tree.item(selected_item)
			window = tk.Toplevel(root)
			window.attributes("-topmost", True)
			window.geometry('800x480')
			window.maxsize(height=480, width=800)
			window.minsize(height=480, width=800)
			window.configure(background='#5F9EA0')
			window.title('Are you sure?')

			text_message_on_window = Label(window, bg='#5F9EA0', font=('arial', 18, 'normal'),text='Are you really sure you want to delete the entry below?')
			text_message_on_window.pack(pady=15)

			entry_row_string = ''
			for column_values in selected_item_info['values']:
				entry_row_string += str(column_values)

				if (selected_item_info['values'][-2] == column_values):
					break
				entry_row_string += ', '

			entry_text_on_window = Label(window, bg='#5F9EA0', font=('arial', 16, 'bold'), text=entry_row_string)
			entry_text_on_window.pack(pady=5)

			yes_button=Button(window, text='Yes', bg='#6495ED', font=('arial', 11, 'normal'),command=lambda: [window.destroy(), delete_selected_log()])
			yes_button.place(x=60, y=330,height=50, width=150)

			no_button=Button(window, text='No', bg='#6495ED', font=('arial', 11, 'normal'),command=window.destroy)
			no_button.place(x=570, y=330,height=50, width=150)

		except:
			return


	def delete_selected_log():
		selected_item = tree.selection()[0]
		selected_item_info = tree.item(selected_item)
		tree.delete(selected_item)
		selected_item_log_id= selected_item_info['values'][4]

		db = mysql.connector.connect(host="localhost", user="admin", passwd="1234", database="security")
		mycursor = db.cursor(dictionary=True)
		mycursor.execute("DELETE FROM log WHERE log_id= '%s'" % (selected_item_log_id))
		db.commit()



	check_log_delete_selected_button = Button(root, text='Delete Selected', bg='#6495ED', font=('arial', 10, 'normal'), command=are_you_sure)
	check_log_delete_selected_button.place(x=570, y=320, height=50, width=150)

def check_residents():
	root.geometry('800x480')
	#root.iconbitmap(r"/home/pi/Desktop/tkinter/look_icon.ico")
	root.configure(background='#5F9EA0')
	root.title('Show Residents Screen')
	columns = ('order', 'name', 'mail', 'RFID', 'resident_id')

	tree = ttk.Treeview(root, columns=columns, show='headings')
	tree.column('order', width=50)
	tree.column('name', width=250)
	tree.column('mail', width=250)
	tree.column('RFID', width=240)
	tree.column('resident_id')

	tree.bind('<Motion>', 'break')

	# Create Headings
	tree.heading('order', text='Order')
	tree.heading('name', text='Name')
	tree.heading('mail', text='Mail Address', anchor="center")
	tree.heading('RFID', text='RFID')

	tree_style_config = ttk.Style()
	tree_style_config.configure('Treeview', rowheight=20)
	tree_style_config.configure('Treeview', font=('Arial', 9))

	#Getting All Entries From Database and Inserting Treeview Kısmı
	db = mysql.connector.connect(host="localhost", user="admin", passwd="1234", database="security")
	mycursor = db.cursor(dictionary=True)
	flag = 1
	mycursor.execute("SELECT * FROM residents")
	mycursor.fetchall()

	if mycursor.rowcount >= 1:
		mycursor.execute("SELECT * FROM residents")
		list = mycursor.fetchall()
		for x in list:
			hidden_rfid = str(x['RFID'])[0:len(str(x['RFID'])) - 4] + "****"
			tree.insert(parent='', index=flag, values=(flag, x["name"], x["mail"], hidden_rfid,x['resident_id']))
			flag += 1


	#Scroolbar
	scrool = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
	tree.configure(yscrollcommand=scrool.set)
	scrool.pack(side='right', fill='y')
	tree.pack(ipady=40)

	check_residents_exit_button = Button(root, text='Exit', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), return_home_screen()])
	check_residents_exit_button.place(x=60, y=320, height=50, width=150)


	def are_you_sure():
		try:
			selected_item = tree.selection()[0]
			selected_item_info = tree.item(selected_item)
			window = tk.Toplevel(root)
			window.attributes("-topmost", True)
			window.geometry('800x480')
			window.maxsize(height=480, width=800)
			window.minsize(height=480, width=800)
			window.configure(background='#5F9EA0')
			window.title('Are you sure?')

			text_message_on_window = Label(window, bg='#5F9EA0', font=('arial', 18, 'normal'),text='Are you really sure you want to delete the entry below?')
			text_message_on_window.pack(pady=15)

			entry_row_string = ''
			for column_values in selected_item_info['values']:
				entry_row_string += str(column_values)

				if (selected_item_info['values'][-2] == column_values):
					break
				entry_row_string += ', '

			entry_text_on_window = Label(window, bg='#5F9EA0', font=('arial', 16, 'bold'), text=entry_row_string)
			entry_text_on_window.pack(pady=5)

			yes_button=Button(window, text='Yes', bg='#6495ED', font=('arial', 11, 'normal'),command=lambda: [window.destroy(), delete_selected_resident()])
			yes_button.place(x=60, y=330,height=50, width=150)

			no_button=Button(window, text='No', bg='#6495ED', font=('arial', 11, 'normal'),command=window.destroy)
			no_button.place(x=570, y=330,height=50, width=150)

		except:
			return

	def delete_selected_resident():

		selected_item = tree.selection()[0]
		selected_item_info = tree.item(selected_item)
		tree.delete(selected_item)

		selected_item_resident_id = selected_item_info['values'][4]
		db = mysql.connector.connect(host="localhost", user="admin", passwd="1234", database="security")
		mycursor = db.cursor(dictionary=True)
		mycursor.execute("DELETE FROM residents WHERE resident_id= '%s'" % (selected_item_resident_id))
		db.commit()
		
		selected_item_resident_name = selected_item_info ['values'][1]
		folder_path = "/home/pi/Desktop/FINAL_DEMO/Face_Recognition/dataset/" 
		shutil.rmtree(folder_path + selected_item_resident_name)
        
		delete_file = open("/home/pi/Desktop/FINAL_DEMO/tkinter/delete_interrupt.txt","w+")
		delete_file.write("delete\ndelete")
		delete_file.close()

		
    

	# messagebox.showinfo("Resident Delete", "Resident deleted successfully.")

	check_residents_delete_selected_button = Button(root, text='Delete Selected', bg='#6495ED', font=('arial', 10, 'normal'),command=are_you_sure)
	check_residents_delete_selected_button.place(x=570, y=320, height=50, width=150)


def check_guests():
	root.geometry('800x480')
	#root.iconbitmap(r"/home/pi/Desktop/tkinter/look_icon.ico")
	root.configure(background='#5F9EA0')
	root.title('Show Guests Screen')
	columns = ('order', 'RFID', 'guest_id')

	tree = ttk.Treeview(root, columns=columns, show='headings')
	#Formatting columns.
	tree.column('order', width=50)
	tree.column('RFID', width=740)
	tree.column('guest_id')

	tree.bind('<Motion>', 'break')

	tree.heading('order', text='Order')
	tree.heading('RFID', text='RFID')

	tree_style_config = ttk.Style()
	tree_style_config.configure('Treeview', rowheight=20)
	tree_style_config.configure('Treeview', font=('Arial', 9))

	db = mysql.connector.connect(host="localhost", user="admin", passwd="1234", database="security")
	mycursor = db.cursor(dictionary=True)
	flag = 1
	mycursor.execute("SELECT * FROM guests")
	mycursor.fetchall()

	if mycursor.rowcount >= 1:
		mycursor.execute("SELECT * FROM guests")
		list = mycursor.fetchall()
		for x in list:
			hidden_rfid = str(x['RFID'])[
						  0:len(str(x['RFID'])) - 4] + "****"
			tree.insert(parent='', index=flag, values=(flag, hidden_rfid, x['guest_id']))
			flag += 1



	#Scroolbar
	scrool = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
	tree.configure(yscrollcommand=scrool.set)
	scrool.pack(side='right', fill='y')

	tree.pack(ipady=40)

	check_guests_exit_button = Button(root, text='Exit', bg='#6495ED', font=('arial', 10, 'normal'),command=lambda: [clear_frame(), return_home_screen()])
	check_guests_exit_button.place(x=60, y=320, height=50, width=150)

	def are_you_sure():
		try:
			selected_item = tree.selection()[0]
			selected_item_info = tree.item(selected_item)
			window = tk.Toplevel(root)
			window.attributes("-topmost", True)
			window.geometry('800x480')
			window.maxsize(height=480, width=800)
			window.minsize(height=480, width=800)
			window.configure(background='#5F9EA0')
			window.title('Are you sure?')

			text_message_on_window = Label(window, bg='#5F9EA0', font=('arial', 18, 'normal'),text='Are you really sure you want to delete the entry below?')
			text_message_on_window.pack(pady=15)

			entry_row_string = ''
			for column_values in selected_item_info['values']:
				entry_row_string += str(column_values)

				if (selected_item_info['values'][-2] == column_values):
					break
				entry_row_string += ', '

			entry_text_on_window = Label(window, bg='#5F9EA0', font=('arial', 16, 'bold'), text=entry_row_string)
			entry_text_on_window.pack(pady=5)

			yes_button=Button(window, text='Yes', bg='#6495ED', font=('arial', 11, 'normal'),command=lambda: [window.destroy(), delete_selected_guest()])
			yes_button.place(x=60, y=330,height=50, width=150)

			no_button=Button(window, text='No', bg='#6495ED', font=('arial', 11, 'normal'),command=window.destroy)
			no_button.place(x=570, y=330,height=50, width=150)

		except:
			return

	def delete_selected_guest():
		selected_item = tree.selection()[0]
		selected_item_info = tree.item(selected_item)
		tree.delete(selected_item)

		selected_item_guest_id = selected_item_info['values'][2]
		db = mysql.connector.connect(host="localhost", user="admin", passwd="1234", database="security")
		mycursor = db.cursor(dictionary=True)
		mycursor.execute("DELETE FROM guests WHERE guest_id= '%s'" % (selected_item_guest_id))
		db.commit()


	check_guests_delete_selected_button = Button(root, text='Delete Selected', bg='#6495ED',font=('arial', 10, 'normal'), command=are_you_sure)
	check_guests_delete_selected_button.place(x=570, y=320, height=50, width=150)


def change_camera_direction():
    def left():
        (servo.servo1).start(0)

        GPIO.output(40,True)          
        (servo.servo1).ChangeDutyCycle(2+(135/18))        
        time.sleep(0.5)
        (servo.servo1).ChangeDutyCycle(0)
        GPIO.output(40,False) 

    def right():
        (servo.servo1).start(0)

        GPIO.output(40,True)          
        (servo.servo1).ChangeDutyCycle(2+(45/18))        
        time.sleep(0.5)
        (servo.servo1).ChangeDutyCycle(0)
        GPIO.output(40,False)        
    def mid_x():
        (servo.servo1).start(0)
        GPIO.output(40,True)          
        (servo.servo1).ChangeDutyCycle(2+(90/18))        
        time.sleep(0.5)
        (servo.servo1).ChangeDutyCycle(0)
        GPIO.output(40,False)
    def down():
        (servo.servo2).start(0)
        
        GPIO.output(38,True)          
        (servo.servo2).ChangeDutyCycle(2+(115/18))        
        time.sleep(0.5)
        (servo.servo2).ChangeDutyCycle(0)
        GPIO.output(38,False) 
    def up():
        (servo.servo2).start(0)
        
        GPIO.output(38,True)          
        (servo.servo2).ChangeDutyCycle(2+(45/18))        
        time.sleep(0.5)
        (servo.servo2).ChangeDutyCycle(0)
        GPIO.output(38,False)
    
    def mid_y():
        (servo.servo2).start(0)
        
        GPIO.output(38,True)          
        (servo.servo2).ChangeDutyCycle(2+(90/18))        
        time.sleep(0.5)
        (servo.servo2).ChangeDutyCycle(0)
        GPIO.output(38,False)
        
    def open_door():

        ##KAPI
        (servo_for_door_and_buzzer.servo_door)
        (servo_for_door_and_buzzer.servo_door).ChangeDutyCycle(2+(90/18))
        time.sleep(0.5) 
        (servo_for_door_and_buzzer.servo_door).ChangeDutyCycle(0)
        (servo_for_door_and_buzzer.servo_door).start(0)
        time.sleep(1)    
        (servo_for_door_and_buzzer.servo_door).ChangeDutyCycle(2+(0/18))
        time.sleep(0.5)
        (servo_for_door_and_buzzer.servo_door).ChangeDutyCycle(0)

        
    root.geometry('800x480')
    #root.iconbitmap(r"/home/pi/Desktop/tkinter/look_icon.ico")
    root.configure(background='#5F9EA0')
    root.title('Change Camera Direction Screen')

    
    change_camera_direction_exit_button = Button(root, text='Exit', bg='#6495ED', font=('arial', 10, 'normal'),command=lambda: [clear_frame(), return_home_screen()])
    change_camera_direction_exit_button.place(x=30, y=330, height=50, width=100)

    Button(root, text='LEFT, ←', bg='#6495ED', font=('arial', 10, 'normal'),command=left).place(x=520, y=100, height=50,width=73)
    Button(root, text='X-MID', bg='#6495ED', font=('arial', 10, 'normal'), command=mid_x).place(x=520, y=270, height=50,width=73)
    Button(root, text='RIGHT, →', bg='#6495ED', font=('arial', 10, 'normal'), command=right).place(x=695, y=100, height=50, width=73)
    Button(root, text='UP, ↑', bg='#6495ED', font=('arial', 10, 'normal'), command=up).place(x=609, y=30, height=50,width=73)
    Button(root, text='Y-MID', bg='#6495ED', font=('arial', 10, 'normal'), command=mid_y).place(x=609, y=270, height=50,width=73)
    Button(root, text='DOWN, ↓', bg='#6495ED', font=('arial', 10, 'normal'), command=down).place(x=609, y=170, height=50,width=73)

    Button(root, text='Open Door', bg='#6495ED', font=('arial', 10, 'normal'),command=open_door).place(x=400, y=330, height=50,width=100)

    cam_label = Label(root, width=480, height=300)
    cam_label.place(x=20, y=10)
    #cap = cv2.VideoCapture(0)
    #cap = VideoStream("http://IP:8000/stream.mjpg").start()
    cap = VideoStream("http://"+ ip+ ":8000/stream.mjpg").start()
    #cap.set(3, 640)
    #cap.set(4, 480)

    def show_cam():
        # Get the latest frame and convert into Image
        frame_cam = cap.read()
        frame_cam = cv2.flip(frame_cam, 1)
        frame_cam = imutils.resize(frame_cam, width = 635, height=200)
        cv2image = cv2.cvtColor(frame_cam, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        # Convert image to PhotoImage
        imgtk = ImageTk.PhotoImage(image=img)
        cam_label.imgtk = imgtk
        cam_label.configure(image=imgtk)
        # Repeat after an interval to capture continiously
        cam_label.after(20, show_cam)

    show_cam()


def change_system_state():
	root.geometry('800x480')
	#root.iconbitmap(r"/home/pi/Desktop/tkinter/look_icon.ico")
	root.configure(background='#5F9EA0')
	root.title('Change System State Screen')
	#Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),text="The state of the motion sensors are: ON").pack(pady=20)





##Destroy Every Widget in the Frame##
# It is needed to draw a new frame after button click
def clear_frame():
	for widget in root.winfo_children():
		widget.destroy()

def greeting_screen():
	root.geometry('800x480')
	#root.iconbitmap(r"\home\pi\Desktop\tkinter\look_icon.ico")
	root.title('HESTIA - Home Security System Products')
	##Successful logo##
	img_canvas = Canvas(root, height=480, width=800, bg="#5F9EA0",highlightthickness="0")
	greeting_wallpaper = PhotoImage(
		file=r"/home/pi/Desktop/tkinter/greeting_screen_800x480.png")
	img_canvas.image = greeting_wallpaper
	img_canvas.create_image(800, 0, anchor=NE, image=greeting_wallpaper)
	img_canvas.place(x=0,y=0)

	img_canvas.bind("<Button-1>", lambda event: [clear_frame(), user_pass_screen()])

##End of successful logo##

def user_pass_screen():
	root.geometry('800x480')
	#root.iconbitmap(r"/home/pi/Desktop/tkinter/look_icon.ico")
	root.configure(background='#5F9EA0')
	root.title('HESTIA - Home Security System Log In')

	screen_text = Label(root, bg='#5F9EA0', font=('arial', 12, 'normal'),text="Please log in with the interface Username-Password dedicated to your HESTIA Home Security product.")
	screen_text.pack(pady=10)


	id_text = Label(root, bg='#5F9EA0', font=('arial', 10, 'bold'),text="Username:")
	id_text.place(x=255, y=40)

	id_box = Entry(root, font=('arial', 10, 'normal'),width=30)
	id_box.place(x=325, y=40)

	pass_text = Label(root, bg='#5F9EA0', font=('arial', 10, 'bold'),text="Password:")
	pass_text.place(x=255, y=70)

	pass_box = Entry(root, font=('arial', 10, 'normal'),width=30, show="*")
	pass_box.place(x=325, y=70)



	def get_id_pass():
		if id_box.get() == "hestia" and pass_box.get() == "ee494":
			clear_frame()
			success_text = Label(root, bg='#5F9EA0', font=('arial', 12, 'bold'),text="Login is successful!")
			success_text.pack(pady=30)

			##Successful logo##
			img_canvas = Canvas(root, height=170, width=170, bg="#5F9EA0",highlightthickness="0")
			success_logo = PhotoImage(
				file=r"/home/pi/Desktop/tkinter/success_logo_150x150.png")
			img_canvas.image = success_logo
			img_canvas.create_image(170, 0, anchor=NE, image=success_logo)
			img_canvas.pack(pady=20)
			##End of successful logo##

			#Successful ekranda 3000 ms bekleyip home screen'e dönüyor
			root.after(3000,lambda: [clear_frame(), return_home_screen()])

		else:
			screen_text.config(text="The username or password is incorrect! Please try again.", font=('bold', 11, 'bold'))

	#Enter tuşu bu.
	check_id_pass_button = Button(root, text='Enter', bg='#6495ED', font=('arial', 10, 'normal'), command=get_id_pass)
	check_id_pass_button.place(x=325, y=100, height=50, width=150)


	####Keyboard Part####
	global selected_entry
	selected_entry=0

	def id_pressed(id_entry):
		global selected_entry
		selected_entry = id_box
	def pass_pressed(pass_entry):
		global selected_entry
		selected_entry = pass_box

	id_box.bind("<Button-1>",lambda event: id_pressed(id_box))
	pass_box.bind("<Button-1>",lambda event: pass_pressed(pass_box))

	####Keyboard Part####
	Keyboard_Buttons = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "q", "w", "e", "r", "t", "y", "u", "i", "o",
						"p", "a", "s", "d", "f", "g", "h", "j", "k", "l", "@", "z", "x", "c", "v", "b", "n", "m", "."]
	Keyboard_Buttons_Caps = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Q", "W", "E", "R", "T", "Y", "U", "I",
							 "O", "P", "A", "S", "D", "F", "G", "H", "J", "K", "L", "@", "Z", "X", "C", "V", "B", "N",
							 "M", "."]


	def select(value):
		global isUpperCase
		if (value == "<---"):
			written_text = selected_entry.get()
			last_char_index = len(written_text) - 1
			selected_entry.delete(last_char_index, "end")
		if (value == "SPACE"):
			selected_entry.insert("insert",
						   " ")

		if (value == "CapsLock"):

			newkeys = []
			if (
					isUpperCase == False):
				newkeys = Keyboard_Buttons_Caps
				isUpperCase = True

			elif (isUpperCase == True):
				newkeys = Keyboard_Buttons
				isUpperCase = False

			for buttonwidget in FourRowsButtonWidgets:
				buttonwidget.destroy()

			FourRowsButtonWidgets.clear()
			# Numbers Row
			key_x = 100
			key_y = 155
			for button in newkeys[0:10]:  # To draw number keys
				command = lambda x=button: select(x)
				a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
						   command=command)
				a.place(x=key_x, y=key_y)
				FourRowsButtonWidgets.append(a)
				key_x = key_x + 60

			# First row
			key_x = 100
			key_y = key_y + 55
			for button in newkeys[10:20]:
				command = lambda x=button: select(x)
				a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
						   command=command)
				a.place(x=key_x, y=key_y)
				FourRowsButtonWidgets.append(a)
				key_x = key_x + 60

			# Second row
			key_x = 100
			key_y = key_y + 55
			for button in newkeys[20:30]:
				command = lambda x=button: select(x)
				a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
						   command=command)
				a.place(x=key_x, y=key_y)
				FourRowsButtonWidgets.append(a)
				key_x = key_x + 60

			# Last row
			key_x = 100
			key_y = key_y + 55
			for button in newkeys[30:]:
				command = lambda x=button: select(x)
				a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
						   command=command)
				a.place(x=key_x, y=key_y)
				FourRowsButtonWidgets.append(a)
				if (
						button == "V" or button == "v"):
					key_x = key_x + 180
				else:
					key_x = key_x + 60

		elif (value != "<---" and value != "SPACE"):  # Normal char key'ler
			selected_entry.insert("insert",
						   value)

	# CapsLock Tuşu
	key_x = 100
	key_y = 100
	Button(root, text="CapsLock", width=3, bg='black', fg='white', relief="raised", padx=39, pady=9, bd=9,
		   command=lambda: select("CapsLock")).place(x=key_x, y=key_y)

	global isUpperCase
	isUpperCase = False

	# Backspace
	key_x = 580
	key_y = 100
	Button(root, text="<---", width=3, bg='black', fg='white', relief="raised", padx=39, pady=9, bd=9, command=lambda: select("<---")).place(x=key_x, y=key_y)

	FourRowsButtonWidgets = []
	# Numbers Row
	key_x = 100
	key_y = key_y + 55
	for button in Keyboard_Buttons[0:10]:  # To draw number keys
		command = lambda x=button: select(x)
		a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,command=command)
		a.place(x=key_x, y=key_y)
		FourRowsButtonWidgets.append(a)
		key_x = key_x + 60

	# First row
	key_x = 100
	key_y = key_y + 55
	for button in Keyboard_Buttons[10:20]:
		command = lambda x=button: select(x)
		a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
				   command=command)
		a.place(x=key_x, y=key_y)
		FourRowsButtonWidgets.append(a)
		key_x = key_x + 60

	# Second row
	key_x = 100
	key_y = key_y + 55
	for button in Keyboard_Buttons[20:30]:
		command = lambda x=button: select(x)
		a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
				   command=command)
		a.place(x=key_x, y=key_y)
		FourRowsButtonWidgets.append(a)
		key_x = key_x + 60

	# Last row
	key_x = 100
	key_y = key_y + 55
	for button in Keyboard_Buttons[30:]:
		command = lambda x=button: select(x)
		a = Button(root, text=button, width=3, bg='black', fg='white', relief="raised", padx=9, pady=9, bd=9,
				   command=command)
		a.place(x=key_x, y=key_y)
		FourRowsButtonWidgets.append(a)
		if (button == "v"):
			key_x = key_x + 180
		else:
			key_x = key_x + 60

	# Space button#
	key_x = 340
	Button(root, text="SPACE", width=3, bg='black', fg='white', relief="raised", padx=39, pady=9, bd=9, command=lambda: select("SPACE")).place(x=key_x, y=key_y)


	####End of Keyboard Part####




##HOME SCREEN##
def return_home_screen():
# This is the section of code which creates the main window
	root.geometry('800x480') #The resolution of the Rasp Pi LCD screen
	#root.iconbitmap(r"/home/pi/Desktop/tkinter/look_icon.ico")
	root.configure(background='#5F9EA0')
	root.title('HESTIA - Home Security Control Panel')


	#background= ImageTk.PhotoImage(Image.open(r"C:\Users\Mert\PycharmProjects\tkinter\background_480x320.png"))
	#img_panel = Label(root, image = background)
	#img_panel.image = background
	#img_panel.pack(side = "bottom", fill = "both", expand = "yes")

	#LOGO PLACEMENT
	img_canvas= Canvas(root, height=320, width=320, bg="#5F9EA0",highlightthickness="0")
	# Then, we actually create the image file to use (it has to be a *.gif)
	HESTIA_logo= PhotoImage(file = r"/home/pi/Desktop/tkinter/hestia_logo_320x320.png")  # <-- you will have to copy-paste the filepath here, for example 'C:\Desktop\pic.gif'
	# Finally, we create the image on the canvas and then place it onto the main window
	img_canvas.image = HESTIA_logo
	img_canvas.create_image(320, 0, anchor=NE, image=HESTIA_logo)
	img_canvas.place(x=420, y=40)


	#HOME SCREEN BUTTONS#
	Introduce_Resident_button = Button(root, text='Introduce Resident', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), introduce_resident()])
	Introduce_Resident_button.place(x=70, y=40, height = 40, width = 200)

	Introduce_Guest_button = Button(root, text='Introduce Guest', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), introduce_guest()])
	Introduce_Guest_button.place(x=70, y=90, height = 40, width = 200)

	Check_Logs_button = Button(root, text='Check Logs', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), check_logs()])
	Check_Logs_button.place(x=70, y=140, height = 40, width = 200)

	Check_Residents_button = Button(root, text='Check Residents', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), check_residents()])
	Check_Residents_button.place(x=70, y=190, height=40, width = 200)

	Check_Guests_button = Button(root, text='Check Guests', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), check_guests()])
	Check_Guests_button.place(x=70, y=240, height=40, width = 200)

	Change_Camera_Direction_button = Button(root, text='Camera Control', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), change_camera_direction()])
	Change_Camera_Direction_button.place(x=70, y=290, height=40, width = 200)

	#Change_System_State_button = Button(root, text='Change System State', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), change_system_state()])
	#Change_System_State_button.place(x=60, y=280, height=30, width = 200)

	Log_Out_button = Button(root, text='Log Out', bg='#6495ED', font=('arial', 10, 'normal'), command=lambda: [clear_frame(), greeting_screen()])
	Log_Out_button.place(x=70, y=340, height=40, width = 200)





root = Tk()

root.maxsize(height=480,width=800)
root.minsize(height=480,width=800)
root.attributes("-topmost", True)
greeting_screen()


root.mainloop()
