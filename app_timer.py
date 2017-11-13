##
# app_timer.py
#
# Creates application that monitors face and locks the computer if something 
# the user is not recognized
##
import sys
import os
import dlib
import glob
import math
import time
import ctypes
from cv2 import *
from tkinter import *
from skimage import io

# Paths for accessing resources
predictor_path = "./res/shape_predictor_68_face_landmarks.dat"
face_rec_model_path = "./res/dlib_face_recognition_resnet_model_v1.dat"
setup_folder_path = "./users"

# Load the models we need a detector to find the faces, a shape predictor
# to find face landmarks so we can recognize the face, and the
# face recognition model.
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

#set the number of photos we require for user setup and how many are currently held
num_reference = 5
saved_photos = 0

# Get the webcam for taking photos of the user
cam = VideoCapture(0)   # 0: index of camera

#list of current users
user_list = []

##
# create_new_user
#
# creates window with an input box for username and a box that checks the 
# username and then begins taking reference photos
##
def create_new_user(root):
    # Create new window
    win = Toplevel()
    win.wm_title("User Creation")
    win.resizable(width=False, height=False)
    win.geometry('{}x{}'.format(400, 300))

    # Create input box for username
    Label(win, text="Enter User Name").pack()
    user_name = Entry(win)
    user_name.pack()

    # Create button to check that the username is valid and proceed with setup
    Button(win, text="Create User", command=lambda:checkUsername(user_name.get(), win)).pack()

    root.wait_window(win)

##
# add_user_to_file
#
# Adds the new user to the list of user names in user_file
##
def add_user_to_file(name):
    new_file = open(setup_folder_path + "/users_file.txt", 'a')
    new_file.write(name + "\n")
    new_file.close()

##
# chackUsername
#
# Checks to see if there is already a user with the given name
# continues setup if there is not otherwise it tells the user to pick a new name
##
def checkUsername(name, win):
    # if a path with that username already exists it is invalid and should 
    # update the window telling the user this information
    if os.path.isfile(setup_folder_path + "/{}/{}4".format(name,name)):
        Label(win, text="There is already a user with this name").pack()
    else:
        # Add user to the user list
        add_user_to_file(name)
        user_list.append(name)
        print(user_list)
        # Create the reference faces
        create_reference_faces(win, name)

##
# reference_img
#
# Takes a photo that will be used as reference for monitoring a user
##
def reference_img(name, index):
    s, img = cam.read()
    if s:
        imshow("Face-Reference-{}".format(index),img)
        waitKey(0)
        destroyWindow("Face-Reference-{}".format(index))
        imwrite(setup_folder_path + "/{}/pics/{}.jpg".format(name, index),img) #save image

##
# create_reference_faces
#
# Creates directories for a given user's name and then takes the references photos
##
def create_reference_faces(win, name):
    # Build the directory for the user
    os.makedirs(setup_folder_path + "/{}".format(name))
    os.makedirs(setup_folder_path + "/{}/pics".format(name))
    # Create the reference faces
    saved_photos = 0
    while saved_photos < 5:
        print("here : " + str(saved_photos))
        conf = Toplevel()
        # Create window
        conf.wm_title("Use photo as a reference {}?".format(saved_photos))
        conf.resizable(width=False, height=False)
        conf.geometry('{}x{}'.format(400, 300))

        # Ask if user wants to use that photo as a reference and create buttons as options
        Label(conf, text="Would you like to use that picture as a reference for your face?").pack()
        # Create buttons for the user to confirm or deny the current photo
        Button(conf, text="Confirm", command=lambda:create_map_file(conf, name, saved_photos)).pack()
        Button(conf, text="Use different picture", command=lambda:new_img_prompt(conf, name, saved_photos)).pack()
        
        use_img_prompt(name, saved_photos)

        win.wait_window(conf)

        if os.path.isfile(setup_folder_path + "/{}/{}{}".format(name,name,saved_photos)):
            saved_photos += 1
        print("out")
    win.destroy()

##
# use_img_prompt
#
# Asks user if they would like to use that image as a reference photo
##
def use_img_prompt(name, index):
    reference_img(name, index)


##
# new_img_prompt
#
# Destroys the last window
##
def new_img_prompt(conf, name, index):
    conf.destroy()

##
# create_map_file
#
# Saves a file containing the landmark points of a reference photo
##
def create_map_file(conf, name, index):
    new_file = open(setup_folder_path + "/{}/{}{}".format(name, name, index), 'w')
    print(setup_folder_path + "/{}/pics/{}.jpg".format(name, index))
    img = io.imread(setup_folder_path + "/{}/pics/{}.jpg".format(name, index))
    dets = detector(img, 1)
    for k, d in enumerate(dets):
        print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
            k, d.left(), d.top(), d.right(), d.bottom()))
        # Get the landmarks/parts for the face in box d.
        shape = sp(img, d)
        # Get face descriptor and save points to the file
        face_descriptor = facerec.compute_face_descriptor(img, shape)
    
        # save each point to the file on a separate line
        for point in face_descriptor:
            new_file.write(str(point) + "\n")
    conf.destroy()
    new_file.close()

##
# load_user_list
#
# loads the usernames
##
def load_user_list():
    file = open("./users/users_file.txt", 'r')
    points = file.readlines()
    for str in points:
        user_list.append(str.rstrip("\n"))
    file.close()

##
# Monitor Face
#
# Class that keeps track of a face monitoring action that is currently running
##
class MonitorFace(Frame):
    
    ##
    # __init__
    #
    # initializer for MonitorFace class
    ##                                                            
    def __init__(self, parent=None, **kw):        
        Frame.__init__(self, parent, kw)
        self._start = 0.0        
        self._elapsedtime = 0.0
        self._running = 0
        self.time_since_last_update = 0.0
        self.current_user = ""
        self.loaded_faces = []
        self.user_option = user_list[0]
        self.makeWidgets()

    ##
    # makeWidgets
    #
    # places the widgets on the MonitorFace window
    ##
    def makeWidgets(self):  

        self.toolbar = Frame(self)                       

        self.user_option = StringVar(self.toolbar)
        self.user_option.set("Select User") # default value
        self.w = OptionMenu(self.toolbar, self.user_option , *user_list)
        self.w.pack()

        self.toolbar.pack(side=TOP, fill=X)
   
    def update_user_options():
    	user_menu = self.user_option["menu"]
    	user_menu.delete(0, "end")
    	for user in user_list:
    		user_menu.add_command(label=string, command=lambda value=user: self.user_option.set(value))


    ##
    # _update
    #
    # Updates the MonitorFace object and keeps track of time between user face checks
    ##
    def _update(self): 
        self._elapsedtime = time.time() - self._start
        self._timer = self.after(1000, self._update)
        self.time_since_last_update += 1
        if self.time_since_last_update >= 10:
            self.recog()
            print(len(self.loaded_faces))
            self.time_since_last_update = 0
        
    ##
    # Start
    #
    # Called when start button is pressed, loads the requested user's data and begins
    # monitoring whether that user is present at each check
    ##
    def Start(self):
        if self.user_option != "Select User"                                   
	        if not self._running:            
                if self.current_user != self.user_option.get():
                    self.load_user()
                self._start = time.time() - self._elapsedtime
                self.time_since_last_update = 0.0
                self._update()
                self._running = 1
    
    ##
    # Stop
    #
    # Stops a face monitoring session and removes and photos that might be saved
    ##
    def Stop(self):                                    
        if self._running:
            self.after_cancel(self._timer)            
            self._elapsedtime = 0
            self._running = 0
            if os.path.isfile('./verify.jpg'):
                os.remove("verify.jpg")

    ##
    # take_photo
    #
    # Uses the webcam to take a photo of the user
    ##
    def take_photo(self):
        s, img = cam.read()
        if s:    # frame captured without any errors
            imwrite("verify.jpg", img) #save image    

    ##
    # get_image_landmarks
    #
    # Gets face descriptor points from a given file
    ##
    def get_image_landmarks(self, path):
        file = open(path, 'r')
        points = file.readlines()
        otherpoints = []
        for str in points:
            otherpoints.append(float(str.rstrip("\n")))
        file.close()
        return otherpoints

    ##
    # load_user
    #
    # Loads the arrays of landmarks from the reference face files for that user
    ##
    def load_user(self):
        file_num = 0
        self.current_user = self.user_option.get()
        self.loaded_faces = []
        for f in glob.glob(os.path.join(setup_folder_path + "/{}/pics".format(self.user_option.get(), "*.jpg"))):
            print("Processing file: {}".format(f))
            self.loaded_faces.append(self.get_image_landmarks(setup_folder_path + "/{}/{}{}".format(self.user_option.get(), self.user_option.get(), file_num)))

    ##
    # lock
    #
    # Locks the Operating System (Windows)
    ##
    def lock(self):
        ctypes.windll.user32.LockWorkStation()

    ##
    # calc_distance
    #
    # Calculates the distance between two face descriptors
    ##
    def calc_distance(self, check, reference):
        sum_of_diff_sq = 0
        i = 0
        for x in check:
            sum_of_diff_sq += (x - reference[i])*(x - reference[i])
            i+=1
        return math.sqrt(sum_of_diff_sq)

    ##
    # recog
    #
    # Takes photo from webcam and creates a face descriptor from that picture.
    # Depending on the numberof faces that are detected in the the photo different
    # actions are takes such as locking the computer if shoulder surfing might be
    # occuring
    ##
    def recog(self):
        self.take_photo()
        distance = 0
        # Now process all the images
        img = io.imread("verify.jpg")

        # Ask the detector to find the bounding boxes of each face. The 1 in the
        # second argument indicates that we should upsample the image 1 time. This
        # will make everything bigger and allow us to detect more faces.
        dets = detector(img, 1)
        print("Number of faces detected: {}".format(len(dets)))
        for k, d in enumerate(dets):
            print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                k, d.left(), d.top(), d.right(), d.bottom()))
            shape = sp(img, d)

            face_descriptor = facerec.compute_face_descriptor(img, shape)

        if len(dets) < 1:
            print("There are no faces in this")
            self.lock()
            self.Stop()
        elif len(dets) == 1:
            for f in self.loaded_faces:
                        distance = distance + self.calc_distance(face_descriptor, f);
        else:
            self.lock()
            self.Stop() 
        avg_distance = distance / num_reference
        print(distance)
        print(avg_distance)

##
# main
#
# Creates the main window of the program and creates the Face Monitor object
##
def main():
    load_user_list()
    root = Tk()
    root.resizable(width=False, height=False)
    root.geometry('{}x{}'.format(400, 300))

    #root.wm_attributes("-topmost", 1)      #always on top - might do a button for it
    sw = MonitorFace(root)
    sw.pack(side=TOP)

    

    Button(root, text='Start', command=sw.Start).pack(side=LEFT)
    Button(root, text='Stop', command=sw.Stop).pack(side=LEFT)
    Button(root, text='create_new_user', command=lambda:create_new_user(root)).pack(side=LEFT)
    
    root.mainloop()

if __name__ == '__main__':
    main()