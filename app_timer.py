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

user_list = ["Doug", "Patrick"]

def create_new_user():
    win = Toplevel()
    win.wm_title("User Creation")

    win.resizable(width=False, height=False)
    win.geometry('{}x{}'.format(400, 300))
    Label(win, text="Enter User Name").pack()
    user_name = Entry(win)
    user_name.pack()

    Button(win, text="Create User", command=lambda:checkUsername(user_name.get(), win)).pack()

def checkUsername(name, win):
    if os.path.isfile("./users/{}/{}4".format(name,name)):
        Label(win, text="There is already a user with this name").pack()
    else:
        user_list.append(name)
        print(user_list)
        create_reference_faces(name)
        win.destroy()

def reference_img(name, index):
    s, img = cam.read()
    if s:
        imshow("Face-Reference-{}".format(index),img)
        waitKey(0)
        destroyWindow("Face-Reference-{}".format(index))
        imwrite("./users/{}/pics/{}.jpg".format(name, index),img) #save image

def create_reference_faces(name):
    os.makedirs("./users/{}".format(name))
    os.makedirs("./users/{}/pics".format(name))
    saved_photos = 0
    if saved_photos < 5:
        print("here : " + str(saved_photos))
        use_img_prompt(name, saved_photos)
        saved_photos += 1
        print("out")

def use_img_prompt(name, index):
    conf = Toplevel()
    conf.wm_title("Use photo as a reference?")

    conf.resizable(width=False, height=False)
    conf.geometry('{}x{}'.format(400, 300))
    Label(conf, text="Would you like to use that picture as a reference for your face?").pack()

    reference_img(name, index)

    Button(conf, text="Confirm", command=lambda:create_map_file(name, index)).pack()
    Button(conf, text="Use different picture", command=lambda:new_img_prompt(conf, name, index)).pack()

def new_img_prompt(conf, name, index):
    conf.destroy()
    use_img_prompt(name, index)

def create_map_file(name, index):
    new_file = open("./users/{}/{}{}".format(name, name, index), 'w')
    
    img = io.imread("./users/{}/pics/{}.jpg".format(name, index))
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


class MonitorFace(Frame):
                                                                
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

    def makeWidgets(self):  

        self.toolbar = Frame(self)                       

        self.user_option = StringVar(self.toolbar)
        self.user_option.set(user_list[0]) # default value
        self.w = OptionMenu(self.toolbar, self.user_option , *user_list)
        self.w.pack()

        self.toolbar.pack(side=TOP, fill=X)
   
    def _update(self): 
        self._elapsedtime = time.time() - self._start
        self._timer = self.after(1000, self._update)
        self.time_since_last_update += 1
        if self.time_since_last_update >= 10:
            self.recog()
            print(len(self.loaded_faces))
            self.time_since_last_update = 0
        
    def Start(self):                                   
        if not self._running:            
            if self.current_user != self.user_option.get():
                self.load_user()
            self._start = time.time() - self._elapsedtime
            self.time_since_last_update = 0.0
            self._update()
            self._running = 1        
    
    def Stop(self):                                    
        if self._running:
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
        for f in glob.glob(os.path.join(setup_folder_path + "/{}/pics".format(self.user_option.get(), "*.jpg"))):
            print("Processing file: {}".format(f))
            self.loaded_faces.append(self.get_image_landmarks(setup_folder_path + "/{}/{}{}".format(self.user_option.get(), self.user_option.get(), file_num)))

    ##
    # Locks the Operating System
    ##
    def lock(self):
        ctypes.windll.user32.LockWorkStation()

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

def main():
    root = Tk()
    root.resizable(width=False, height=False)
    root.geometry('{}x{}'.format(400, 300))

    #root.wm_attributes("-topmost", 1)      #always on top - might do a button for it
    sw = MonitorFace(root)
    sw.pack(side=TOP)

    

    Button(root, text='Start', command=sw.Start).pack(side=LEFT)
    Button(root, text='Stop', command=sw.Stop).pack(side=LEFT)
    Button(root, text='create_new_user', command=create_new_user).pack(side=LEFT)
    
    root.mainloop()

if __name__ == '__main__':
    main()