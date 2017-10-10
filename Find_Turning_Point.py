import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from tkinter import filedialog
import tkinter as tk
import numpy as np
from tkinter import ttk
from tkinter import *
from scipy.optimize import curve_fit

hm_sigma = 3.0

class Linear_fits:

    def __init__(self, master):
        self.master = master
        self.master.title("Double Linear Fits to Find Turning Point!")
        self.master.minsize(900, 680)
        #self.master.resizable(False, False)
        self.style = ttk.Style()
        self.style.configure('TFrame')
        self.style.configure('TButton')

        ##define a top frame where the canvas will be placed
        self.top_frame = ttk.Frame(self.master, padding = (30, 15))
        self.top_frame.pack()

        self.fig = plt.figure(figsize=(12, 8), dpi=100) ##create a figure; modify the size here
        self.fig.add_subplot()
    
        plt.title("Linear Fit Two Sections of Data to Find Turning Point")
        plt.xlabel("Concentration ug/mL", labelpad = 20, fontsize = 15)
        plt.ylabel("Fluorescence intensity", labelpad = 20, fontsize = 15)

        plt.xticks([])
        plt.yticks([])

        self.canvas = FigureCanvasTkAgg(self.fig, master = self.top_frame)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.top_frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        ##define buttons at bottom frame

        self.bottom_frame = ttk.Frame(self.master, padding = (30, 15))
        self.bottom_frame.pack()

        ttk.Button(self.bottom_frame, text = "Load_Data",
                   command = self.load_data, style = "TButton").pack(side = LEFT)
        
        ttk.Button(self.bottom_frame, text = "Remove_Outlier",
                   command = self.remove_outlier, style = "TButton").pack(side = LEFT)

        ttk.Button(self.bottom_frame, text = "Fit_Data",
                   command = self.fit_data, style = "TButton").pack(side = LEFT)        

        ttk.Button(self.bottom_frame, text = "Clear the Plot",
                   command = self.clear_plot, style = "TButton").pack(side = LEFT)
        
        ttk.Button(self.bottom_frame, text = "Save_Data",
                   command = self.save_data, style = "TButton").pack(side = RIGHT)
        

    def load_data(self):
        self.input_file_name = filedialog.askopenfile(defaultextension = ".txt", mode = "r", 
                                                     filetypes = [("Text Documents", "*.txt")])
        self.data = np.loadtxt(self.input_file_name).transpose()
        
        ##data column number could be up to 9 but minimum number is 1; introduce a parameter called cm: column_number
        self.column_number = len(self.data) - 1 #deduct the first x column

        #print (self.column_number)

        for ind, i in zip(["331", "332", "333", "334", "335", "336", "337", "338", "339" ][:self.column_number], range(self.column_number)):
            self.fig.add_subplot(int(ind))
            plt.plot(self.data[0], self.data[i+1], "bo", markersize=6)

        self.canvas.draw()

    def remove_outlier(self):
        ##the outlier is the one has a value out of the range (mean +/- 2*Sigma) of an array
        
        for ind, i in zip(["331", "332", "333", "334", "335", "336", "337", "338", "339" ][:self.column_number], range(self.column_number)):
            self.fig.add_subplot(int(ind))
        ##first calculate the mean and standard deviation of the array
            mean = np.mean(self.data[i+1], axis = 0)
            std = np.std(self.data[i+1], axis = 0)
            lower_bound = mean - hm_sigma*std
            upper_bound = mean + hm_sigma*std
            temp_index = (self.data[i+1]> lower_bound) & (self.data[i+1]< upper_bound)
            
            self.new_x_axis = self.data[0][temp_index]
            self.new_y_axis = self.data[i+1][temp_index]
            
            plt.plot(self.data[0], self.data[i+1], "bo", markersize=6)
            plt.plot(self.new_x_axis, self.new_y_axis, "ro", markersize=6)

        self.canvas.draw()
        
    def clear_plot(self):
        self.fig.clf()
        plt.title("Linear Fit Two Sections of Data to Find Turning Point")
        plt.xlabel("Concentration ug/mL", labelpad = 20, fontsize = 15)
        plt.ylabel("Fluorescence intensity", labelpad = 20, fontsize = 15)

        plt.xticks([])
        plt.yticks([])

        self.canvas.draw()

    def save_data(self):        
        self.out_file_name = filedialog.asksaveasfile(defaultextension = ".txt", mode = "w",
                                                     filetypes = [("Text Documents", "*.txt")])
        self.out_file_name.write("*************************************************************************")
        self.out_file_name.write("\n")
        self.out_file_name.write("Here are the concentrations from the transition of fluorescence intensity")
        self.out_file_name.write("\n")
        self.out_file_name.write("*************************************************************************")  
        self.out_file_name.write("\n")
        for i in self.turning_points:
            self.out_file_name.write(str(i))
            self.out_file_name.write("\n")
        self.out_file_name.close()        
        

    def fit_data(self): ##take in x, y; arrays, return intersect_x, intersect_y, a_1, b_1, a_2, b_2
        def func(x, a, b):
            return a*x + b

        def squared_error(x, y, a, b):
        ###x, y are arrays, a,b are fitted parameters
            y_fit = a*x + b
            return sum((y - y_fit)**2)

        #initial guess

        def find_intersection(x, y):
            x0 = [1, 20]
            
            ##divide data to two parts
            error_p1 = []
            error_p2 = []
            combined_squared_error = []
            a_b_p1 = []
            a_b_p2 = []
            for index in range(len(x)-2):
                part_1_x = x[:index+2]  ##this is array
                part_1_y = y[:index+2]
                part_2_x = x[index+1:]
                part_2_y = y[index+1:]

                popt_p1, pcov_p1 = curve_fit(func, part_1_x, part_1_y, x0)
                popt_p2, pcov_p2 = curve_fit(func, part_2_x, part_2_y, x0)

                e1 = squared_error(part_1_x, part_1_y, popt_p1[0], popt_p1[1])
                e2 = squared_error(part_2_x, part_2_y, popt_p2[0], popt_p2[1])

                a_b_p1.append(popt_p1)
                a_b_p2.append(popt_p2)
                error_p1.append(e1)
                error_p2.append(e2)
                combined_squared_error.append(e1 + e2)

            ##return the index of the first minimum
            m = min(combined_squared_error)
            first_minimum_index = [i for i, j in enumerate(combined_squared_error) if j==m][0]

            ##calculate the intersection point of two fitted curve
            a_1 = a_b_p1[first_minimum_index][0]
            a_2 = a_b_p2[first_minimum_index][0]
            b_1 = a_b_p1[first_minimum_index][1]
            b_2 = a_b_p2[first_minimum_index][1]

            intersect_x = (b_2 - b_1)/(a_1 - a_2)
            intersect_y = a_1 * intersect_x + b_1

            return intersect_x, intersect_y, a_1, b_1, a_2, b_2

        self.turning_points = []

        for ind, i in zip(["331", "332", "333", "334", "335", "336", "337", "338", "339" ][:self.column_number], range(self.column_number)):

            mean = np.mean(self.data[i+1], axis = 0)
            std = np.std(self.data[i+1], axis = 0)
            lower_bound = mean - hm_sigma*std
            upper_bound = mean + hm_sigma*std
            temp_index = (self.data[i+1]> lower_bound) & (self.data[i+1]< upper_bound)
            self.new_x_axis = self.data[0][temp_index]
            self.new_y_axis = self.data[i+1][temp_index]

            intersect_x, intersect_y, a_1, b_1, a_2, b_2 = find_intersection(self.new_x_axis, self.new_y_axis)
            self.turning_points.append(intersect_x)
            self.fig.add_subplot(int(ind))    
            #plt.plot(self.data[0], self.data[i+1], "bo", markersize=6)
            plt.plot(self.new_x_axis, a_1*self.new_x_axis + b_1, "r-")
            plt.plot(self.new_x_axis, a_2*self.new_x_axis + b_2, "b-")
            plt.plot(intersect_x, intersect_y, 'ro', markersize = 10,
            label='TP:({0:.2f},{1:.2f})'.format(intersect_x, intersect_y))
            plt.legend(loc=0)

        self.canvas.draw()      

def main():        
    root = Tk()
    GUI = Linear_fits(root)
    root.mainloop()
    
if __name__ == "__main__": main()          
