from Tkinter import *
import time

class MonitorFace(Frame):  
    """ Implements a stop watch frame widget. """                                                                
    def __init__(self, parent=None, **kw):        
        Frame.__init__(self, parent, kw)
        self._start = 0.0        
        self._elapsedtime = 0.0
        self._running = 0
        self.time_since_last_update = 0.0
   
    def _update(self): 
        self._elapsedtime = time.time() - self._start
        self._timer = self.after(1000, self._update)
        self.time_since_last_update += 1
        if self.time_since_last_update >= 5:
            print("hey");
            self.time_since_last_update = 0
        
    def Start(self):                                   
        if not self._running:            
            self._start = time.time() - self._elapsedtime
            self.time_since_last_update = 0.0
            self._update()
            self._running = 1        
    
    def Stop(self):                                    
        if self._running:
            self.after_cancel(self._timer)            
            self._elapsedtime = 0
            self._running = 0
            
def main():
    root = Tk()
    root.wm_attributes("-topmost", 1)      #always on top - might do a button for it
    sw = MonitorFace(root)
    sw.pack(side=TOP)

    Button(root, text='Start', command=sw.Start).pack(side=LEFT)
    Button(root, text='Stop', command=sw.Stop).pack(side=LEFT)
    
    root.mainloop()

if __name__ == '__main__':
    main()