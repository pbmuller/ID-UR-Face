import sys
import os
import shutil
import dlib
import glob
import math
import time

import ctypes
from cv2 import *
import tkinter as tk
from scipy.misc import imread

#paths for accessing resources
predictor_path = "./res/shape_predictor_68_face_landmarks.dat"
face_rec_model_path = "./res/dlib_face_recognition_resnet_model_v1.dat"
setup_folder_path = "./users"

# Load all the models we need: a detector to find the faces, a shape predictor
# to find face landmarks so we can precisely localize the face, and finally the
# face recognition model.
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

num_reference = 5
saved_photos = 0

cam = VideoCapture(0)   # 0 -> index of camera

interval_options = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

# check for the users directory
directory = os.listdir()
users_flag = False
for entry in directory:
    if entry == 'users':
        users_flag = True
if not users_flag:
    os.makedirs('./users')


def get_users():
    user_list = os.listdir('./users')
    global user_count
    user_count = len(user_list)
    if len(user_list) == 0:
        user_list.append('No Users Found')
    return user_list

user_list = get_users()


def how_to():
    howto = tk.Toplevel()
    howto.wm_title("How To")

    howto.resizable(width=False, height=False)
    howto.geometry('{}x{}'.format(400, 300))

    how_to_file = open("./res/how_to.txt", "r")
    how_to_text = tk.Text(howto, wrap=tk.WORD)
    how_to_text.insert(tk.END, how_to_file.read())
    how_to_text.pack()

def create_new_user(root, sw):
    win = tk.Toplevel()
    win.wm_title("User Creation")

    win.resizable(width=False, height=False)
    win.geometry('{}x{}'.format(400, 300))
    tk.Label(win, text="Enter User Name").pack()
    user_name = tk.Entry(win)
    user_name.pack()
    error_label = tk.Label(win, text="There is already a user with this name")
    error_label_2 = tk.Label(win, text="Username must be only characters in the alphabet")
    tk.Button(win, text="Create User", command=lambda: check_username(user_name.get(), win, sw, error_label, error_label_2)).pack()
    tk.Button(win, text="Cancel", command=win.destroy).pack()

    root.wait_window(win)

def check_username(name, win, sw, error_label, error_label_2):
    user_already_exists = False
    error_label.pack_forget()
    error_label_2.pack_forget()
    users = get_users()
    for user in users:
        if name == user:
            user_already_exists = True
    if user_already_exists:
        error_label.pack()
    elif not name.isalpha():
        error_label_2.pack()
    else:
        error_label.pack_forget()
        create_reference_faces(name, win, sw)

def reference_img(name, index):
    face_found = False
    while not face_found:
        s, img = cam.read()
        if s:
            dets = detector(img, 1)
            print(len(dets))
            if len(dets) == 1:
                face_found = True
                imshow("Face-Reference-{}".format(index),img)
                waitKey(0)
                destroyWindow("Face-Reference-{}".format(index))
                imwrite("./users/{}/pics/{}.jpg".format(name, index),img) #save image


def create_reference_faces(name, win, sw):
    os.makedirs("./users/{}".format(name))
    shutil.copyfile('./res/default_settings.txt', './users/{}/settings.txt'.format(name))
    os.makedirs("./users/{}/pics".format(name))
    saved_photos = 0
    while saved_photos < 5:
        print("here : " + str(saved_photos))
        conf = tk.Toplevel()
        # Create window
        conf.wm_title("Use photo as a reference {}?".format(saved_photos))
        conf.resizable(width=False, height=False)
        conf.geometry('{}x{}'.format(400, 300))

        # Ask if user wants to use that photo as a reference and create buttons as options
        tk.Label(conf, text="Would you like to use that picture as a reference for your face?").pack()
        # Create buttons for the user to confirm or deny the current photo
        tk.Button(conf, text="Confirm", command=lambda:create_map_file(conf, name, saved_photos)).pack()
        tk.Button(conf, text="Use different picture", command=lambda:new_img_prompt(conf, name, saved_photos)).pack()
        
        use_img_prompt(name, saved_photos)

        win.wait_window(conf)

        if os.path.isfile(setup_folder_path + "/{}/{}{}".format(name,name,saved_photos)):
            saved_photos += 1
        print("out")
    sw.refresh()
    win.destroy()

def use_img_prompt(name, index):
    reference_img(name, index)

def new_img_prompt(conf, name, index):
    conf.destroy()

def create_map_file(conf, name, index):
    new_file = open("./users/{}/{}{}".format(name, name, index), 'w')
    
    img = imread("./users/{}/pics/{}.jpg".format(name, index))
    dets = detector(img, 1)
    for k, d in enumerate(dets):
        print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
            k, d.left(), d.top(), d.right(), d.bottom()))
        # Get the landmarks/parts for the face in box d.
        shape = sp(img, d)
        #get face descriptor and save points to the file
        face_descriptor = facerec.compute_face_descriptor(img, shape)
    
        for point in face_descriptor:
            new_file.write(str(point) + "\n")

    new_file.close()
    conf.destroy()

def create_user_prompt():
    conf = tk.Toplevel()
    conf.wm_title("Must Make a User Profile")

    conf.resizable(width=False, height=False)
    conf.geometry('{}x{}'.format(400, 300))

    tk.Label(conf, text="No User profiles found. You must make a user profile first!").pack()
    tk.Button(conf, text="Confirm", command=conf.destroy).pack()

def manage_profile_settings(sw):
    if user_count > 0:
        user = sw.user_option.get()

        conf = tk.Toplevel()
        conf.wm_title("Profile Settings: {}".format(user))

        conf.resizable(width=False, height=False)
        conf.geometry('{}x{}'.format(400, 300))

        if not os.path.exists('./users/{}/settings.txt'.format(user)):
            shutil.copyfile('./res/default_settings.txt', './users/{}/settings.txt'.format(user))

        user_settings_file = open('./users/{}/settings.txt'.format(user), 'r+')
        update_timer = tk.StringVar()
        update_timer.set(user_settings_file.read())

        user_settings_file.close()
        user_settings_file = open('./users/{}/settings.txt'.format(user), 'w')

        seconds_label = tk.Label(conf, text="Seconds")
        seconds_label.grid(row=0, column=1)
        interval_label = tk.Label(conf, text="Recognition Interval")
        interval_label.grid(row=1, column=0)
        interval_entry = tk.OptionMenu(conf, update_timer, *interval_options)
        interval_entry.grid(row=1, column=1)
        confirm_button = tk.Button(conf, text="Confirm", command=lambda: update_settings(conf, update_timer, user_settings_file))
        confirm_button.grid(row=2, column=0, sticky=tk.E)
        cancel_button = tk.Button(conf, text="Cancel", command=conf.destroy)
        cancel_button.grid(row=2, column=1, sticky=tk.W)
    else:
        create_user_prompt()

def get_interval(sw):
    user_settings_file = open('./users/{}/settings.txt'.format(sw.user_option.get()), 'r')

    interval = int(user_settings_file.read())

    user_settings_file.close()
    return interval

def update_settings(parent, new_interval, user_settings_file):
    print(new_interval.get())
    user_settings_file.writelines([new_interval.get()])

    conf = tk.Toplevel()
    conf.wm_title("Confirm")

    conf.resizable(width=False, height=False)
    conf.geometry('{}x{}'.format(400, 300))

    tk.Label(conf, text="Settings Updated!").pack()
    tk.Button(conf, text="Okay", command=conf.destroy).pack()

def delete_user_with_prompt(parent, sw):
    if user_count > 0:
        conf = tk.Toplevel()
        conf.wm_title("Delete User?")

        conf.resizable(width=False, height=False)
        conf.geometry('{}x{}'.format(400, 300))

        user = sw.user_option.get()

        tk.Label(conf, text="Would you like to delete the User profile {}?".format(user)).pack()

        tk.Button(conf, text="Confirm", command=lambda: delete_user(conf, user, sw)).pack()
        tk.Button(conf, text="Cancel", command=lambda: conf.destroy()).pack()
        parent.wait_window(conf)
    else:
        create_user_prompt()

def delete_user(conf, user, sw):
    shutil.rmtree('./users/{}'.format(user))    
    conf.destroy()
    sw.refresh()

class MonitorFace(tk.Frame):
                                                                
    def __init__(self, parent=None, **kw):        
        tk.Frame.__init__(self, parent, kw)
        self._start = 0.0        
        self._elapsedtime = 0.0
        self._running = 0
        self.time_since_last_update = 0.0
        self.current_user = ""
        self.loaded_faces = []
        self.user_option = user_list[0]
        self.makeWidgets()


    def makeWidgets(self):  

        self.toolbar = tk.Frame(self)                       

        self.user_option = tk.StringVar(self.toolbar)
        self.user_option.set(user_list[0]) # default value
        self.w = tk.OptionMenu(self.toolbar, self.user_option , *user_list)
        self.w.config(width=15)
        self.w.pack()

        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def refresh(self):
        # Reset var and delete all old options
        self.user_option.set('')
        self.w['menu'].delete(0, 'end')
        user_list = get_users()
        # Insert list of new options (tk._setit hooks them up to var)
        self.user_option.set(user_list[0])
        for user in user_list:
            self.w['menu'].add_command(label=user, command=tk._setit(self.user_option, user))
   
    def _update(self): 
        update_interval = get_interval(self)
        self._elapsedtime = time.time() - self._start
        self._timer = self.after(1000, self._update)
        self.time_since_last_update += 1
        if self.time_since_last_update >= update_interval:
            self.recog()
            print("loaded faces: " + str(len(self.loaded_faces)))
            self.time_since_last_update = 0
        
    def Start(self):
        if user_count > 0:
            if not self._running:
                status.set("Status: Running")
                if self.current_user != self.user_option.get():
                    self.load_user()
                self._start = time.time() - self._elapsedtime
                self.time_since_last_update = 0.0
                self._update()
                self._running = 1
        else:
            create_user_prompt()
    
    def Stop(self):
        if self._running:
            status.set("Status: Inactive")
            self.after_cancel(self._timer)
            self._elapsedtime = 0
            self._running = 0
            if os.path.isfile('./verify.jpg'):
                os.remove("verify.jpg")

    def take_photo(self):
        s, img = cam.read()
        if s:    # frame captured without any errors
            imwrite("verify.jpg", img) #save image    

    ##
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

    def load_user(self):
        file_num = 0
        self.current_user = self.user_option.get()
        self.loaded_faces = []
        for f in glob.glob(os.path.join(setup_folder_path + "/{}/pics/{}".format(self.user_option.get(), "*.jpg"))):
            print("Processing file: {}".format(f))
            self.loaded_faces.append(self.get_image_landmarks(setup_folder_path + "/{}/{}{}".format(self.user_option.get(), self.user_option.get(), file_num)))

    ##
    # Locks the Operating System
    ##
    def lock(self):
        try:
            ctypes.windll.user32.LockWorkStation()
        except:
            os.popen('/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend')

    ##
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
    # Does Facial recognition things
    ##
    def recog(self):
        self.take_photo()
        distance = 0
        # Now process all the images
        img = imread("verify.jpg")

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
        if avg_distance > 0.6:
            self.lock()
            self.Stop()
        print("distance = {}".format(distance))
        print("average distance = {}".format(avg_distance))

def main():
    root = tk.Tk()
    root.title("I C UR / Face (Integrated Continuous User Recognition / Face)")
    root.resizable(width=False, height=False)
    root.geometry('{}x{}'.format(400, 300))

    #root.wm_attributes("-topmost", 1)      #always on top - might do a button for it
    sw = MonitorFace(root)
    sw.pack()

    start_button = tk.Button(root, text='Start', width=15,command=sw.Start)
    start_button.pack()
    stop_button = tk.Button(root, text='Stop', width=15, command=sw.Stop)
    stop_button.pack()
    create_new_user_button = tk.Button(root, text='Create New User', width=15, command=lambda: create_new_user(root, sw))
    create_new_user_button.pack()
    manage_profile_settings_button = tk.Button(root, text='Manage Profile', width=15, command=lambda: manage_profile_settings(sw))
    manage_profile_settings_button.pack()
    delete_user_button = tk.Button(root, text='Delete Current User', width=15, command=lambda: delete_user_with_prompt(root, sw))
    delete_user_button.pack()
    how_to_button = tk.Button(root, text='How-To', width=15, command=how_to)
    how_to_button.pack()

    global status
    status = tk.StringVar()
    status.set("Status: Inactive")
    status_label = tk.Label(root, textvariable=status)
    status_label.pack()
    
    root.mainloop()

if __name__ == '__main__':
    main()
