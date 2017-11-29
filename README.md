# ID UR Face

This submission contains all the file that we did all our code in.
All the code in the file is all our code that we wrote which uses a
couple of libraries:

Dlib: Library that can identifyfaces  in photos which helped us do landmarking
	Found here: http://dlib.net/

OpenCV: Gave us access to computer webcam and allowed us to take photos
	Found here: https://github.com/opencv/opencv

TkInter: Built-in python library that helped build the GUI

Most of the other libraries that we had to import were dependencies of OpenCV or Dlib

Files:
app_timer.py
	This is our entire application that creates user profiles, gui, facial recognition.
		TkInter had a lot of problems when we tried to split our source code up into 
		separate files. We wanted to split up source code into many files however the
		libraries we were using did not like when we tried to split them up.

user_setting.py
	Was meant to have serializable users and settings using a native python library, pickle.
	Unfortunately TkInter didn't like when we tried to have this implemented with out gui and
	had to abandon the idea to focus on other goals we thought were more important.
	(Not sure if you wanted this but we spent time on writing it for the project so thought
	might as well include it)

Developent of the app was a lot of troubleshooting combined with reading about deep learning
and facial recognition methods. Also problems with the libraries really slowed down the rate
at which we could complete goals that we wanted for this project. 