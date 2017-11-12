import sys
import os
import dlib
import glob
import math
import time
from tkinter import *
from skimage import io

#paths for accessing resources
predictor_path = "./res/shape_predictor_5_face_landmarks.dat"
face_rec_model_path = "./res/dlib_face_recognition_resnet_model_v1.dat"
setup_folder_path = "./users"

# Load all the models we need: a detector to find the faces, a shape predictor
# to find face landmarks so we can precisely localize the face, and finally the
# face recognition model.
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

current_loaded_user = "";
faces = [];

run = False

##
# TODO: Sets up new user profile
##
def setup_user():
    file_num = 0
    print(user_option.get().lower())
    # Now process all the images
    for f in glob.glob(os.path.join(setup_folder_path + "/{}/pics".format(user_option.get().lower()), "*.jpg")):
        print("Processing file: {}".format(f))
        img = io.imread(f)

        # Ask the detector to find the bounding boxes of each face. The 1 in the
        # second argument indicates that we should upsample the image 1 time. This
        # will make everything bigger and allow us to detect more faces.
        dets = detector(img, 1)
        print("Number of faces detected: {}".format(len(dets)))
        
        if len(dets) == 1:
            # Now process each face we found.
            for k, d in enumerate(dets):
                print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                    k, d.left(), d.top(), d.right(), d.bottom()))
                # Get the landmarks/parts for the face in box d.
                shape = sp(img, d)
                #get face descriptor and save points to the file
                face_descriptor = facerec.compute_face_descriptor(img, shape)
                print(file_num)
                save_image_landmarks(setup_folder_path + "/{}/{}{}".format(user_option.get().lower(), user_option.get().lower(), file_num), face_descriptor)
                file_num+=1

##
# Saves face descriptor points to a file
##
def save_image_landmarks(path, points):
    print("landmarks path: " + path)
    new_file = open(path, 'w')
    for point in points:
        new_file.write(str(point) + "\n")
    new_file.close()

##
# Gets face descriptor points from a given file
##
def get_image_landmarks(path):
    file = open(path, 'r')
    points = file.readlines()
    otherpoints = []
    for str in points:
        otherpoints.append(float(str.rstrip("\n")))
    file.close()
    return otherpoints

##
# Calculates the distance between two face descriptors
##
def calc_distance(check, reference):
    sum_of_dif_sq = 0
    i = 0
    for x in face_descriptor:
        sum_of_dif_sq += (x - prev[i])*(x - prev[i])
        i+=1
    return math.sqrt(sum_of_diff_sq)

##
# Does Facial recognition things
##
def recog():
    win = dlib.image_window()

    # Now process all the images
    for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
        print("Processing file: {}".format(f))
        img = io.imread(f)

        win.clear_overlay()
        win.set_image(img)

        # Ask the detector to find the bounding boxes of each face. The 1 in the
        # second argument indicates that we should upsample the image 1 time. This
        # will make everything bigger and allow us to detect more faces.
        dets = detector(img, 1)
        print("Number of faces detected: {}".format(len(dets)))
        
       	if len(dets) < 1:
       		print("There are no faces in this")
       	elif len(dets) == 1:
	        for k, d in enumerate(dets):
	            print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
	                k, d.left(), d.top(), d.right(), d.bottom()))
	            # Get the landmarks/parts for the face in box d.
	            shape = sp(img, d)
	            # Draw the face landmarks on the screen so we can see what face is currently being processed.
	            win.clear_overlay()
	            win.add_overlay(d)
	            win.add_overlay(shape)

	            face_descriptor = facerec.compute_face_descriptor(img, shape)

	            calc_distance();
	            
	            print(total)
        else:
            lock()
##
# Locks the Operating System
##
def lock():
    os.popen('gnome-screensaver-command --lock')

def start_timer():
	run = True
	while run:
		time.sleep(10)
		print("hey")
	print("timer ended")

def stop_timer():
	run = false;

root = Tk()

toolbar = Frame(root)

a = Button(toolbar, text="lock", width = 40, command=lock)
a.pack(padx = 3, pady = 10)

b = Button(toolbar, text="popup window", width = 40, command=recog)
b.pack(padx = 3, pady = 10)

c = Button(toolbar, text="setup", width = 40, command=setup_user)
c.pack(padx = 3, pady = 10)

d = Button(toolbar, text="start", width = 40, command=start_timer)
d.pack(padx = 3, pady = 10)

e = Button(toolbar, text="stop", width = 40, command=stop_timer)
e.pack(padx = 3, pady = 10)

user_list = ["Doug", "Patrick"]

user_option = StringVar(toolbar)
user_option.set(user_list[0]) # default value
w = OptionMenu(toolbar, user_option , *user_list)
w.pack()

toolbar.pack(side=TOP, fill=X)

mainloop()