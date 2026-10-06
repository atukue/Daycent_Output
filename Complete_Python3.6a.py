"""This script moves daycent input files from several folders into the
daycent folder (python working directory) and runs the daycent model. All the .lis
(output)files are moved into the output folder and all other reulting files from the
model run deleted.

The lis_Reader function then reads the DayCent .lis output files and returns lists of time
elapsed and change in soil organic carbon, as well as the average rate of change. 

Args-
    lis_fpath (str):  file/path to .lis file to be read
    time_column (int):  'time' column in the .lis file.
        Note that python starts counting from 0, not 1!
    somtc_column (int):  'somtc' column in the .lis file.
    head_skip (int):  number of header lines to skip over
        before starting to read data
    tail_skip (int):  number of lines to skip over at end
        of file (DayCent .lis files always include an extra
        repeated line!)
        
Finally, the main script computes average rates of change in soil carbon, plots all
change in soil carbon vs. time, and archives all results.
"""

# import statements allow you to access useful functions defined
# in other modules outside this one
import os
import glob
import shutil
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def list_files(path):
    # returns a list of names (with extension, without full path) of all files 
    # in folder path
    files = []
    for name in os.listdir(path):
        if os.path.isfile(os.path.join(path, name)):
            files.append(name.lower())
    return files

rootInput="Rotations\\"
inputList=list_files(rootInput)
absolutePath=os.getcwd()
dest=""
output="output\\"
print(inputList)

# common six input files to both rotion sites
for f in inputList:
    src=rootInput+f
    print (os.system("copy %s %s /y" % (src,dest)))# copy all the input files (parameter files)from rootInput folder to the daycent folder 


# first site rotation system (fww(NP))files
#nat = "natgrass"
root="rotations\\fww(NP)\\"
schFileList=list_files(root)
for f in schFileList:
    src=root+f
    name=f.split(".")[0]
    print (os.system("copy %s %s /y"% (src,dest)))# copy all the .sch input files (schedule files) from (fww(NP)) folder to the daycent folder
    print (os.system(dest+"DDCent -s %s -n %s"% (dest+f,name)))
#    print (os.system(dest+"ddcent -s %s -n %s -e %s"% (dest+f,name, nat))) # daycent will run using the .sch (schedule) files in the (fww(NP)) folder and create binary output files rotation_name.bin.
    print (os.system(dest+"DDlist100 %s %s outvars_aru.txt"%(name, name))) # LIST100 will extract output values from the .bin files and create the .lis ASCII files using the list of variable names in the var_list.txt file.
    nameWithTime=name+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")+".lis" # Add datestamp to the rotation name.lis
    print (os.system("copy %s %s /y"% (dest+name+".lis",output+nameWithTime)))# Copy .lis files to the output folder
    print (os.system("del %s"% (dest+name+".lis")))
    print (os.system("del %s"% (dest+name+".bin")))
print(schFileList)


listOfFilesToDelete=["crop.100","FERT.100","HARV.100","SOILS.IN","",""]
for f in listOfFilesToDelete:
    print (os.system("del %s"%(f)))
    



# You should define functions for operations that will be repeated
# multiple times or re-used in different modules.  These functions
# won't be run until they are called in the main body of the code
# below.  Each function can have its own 'docstring' description.

def lis_reader(lis_fpath, time_column, somtc_column, head_skip, tail_skip):

    # This opens the target .lis file as an object called
    # 'lis_file' and reads its data line-by-line, selectively
    # saving time data and somtc data into lists of floating-point
    # (i.e. decimal) values, skipping header rows as needed and
    # trimming redundant data at the end.
    lis_file = open(lis_fpath, 'r')
    time_values = []
    somtc_values = []
    for i in range(head_skip):
        next(lis_file)
    for line in lis_file:
        time_values.append(float(line.split()[time_column]))
        somtc_values.append(float(line.split()[somtc_column]))
    for j in range(tail_skip):
        del time_values[-1]
        del somtc_values[-1]
    # Next, we note the initial soil organic level and simulation
    # starting time and re-compute our 'somtc_values' and
    # 'time_values' lists as relative changes.
    initial_time = time_values[0]
    initial_somtc = somtc_values[0]
    for k in range(len(time_values)):
        time_values[k] = time_values[k]
#        time_values[k] = time_values[k]
        somtc_values[k] = somtc_values[k]

    # Now we compute the average rate of change in soil organic
    # carbon by subtracting the first somtc value from the last
    # somtc value, and dividing by the time elapsed
    somtc_rate = (somtc_values[-1] - somtc_values[0]) / time_values[-1]

    # Finally, we send our results back to the main program from
    # which this function was called
    return time_values, somtc_values, somtc_rate

    # This is where the main body of the code starts- when you run the
    # script it starts executing line-by-line from this point.  This
    # first statement prints out the contents of the docstring for the
    # user's reference.
print (__doc__)
print()
# We'll want to save all of our average somtc change rate results
# in a comma-separated-value file format.  We'll start by defining
# a text string we'll use to hold that data, beginning with a
# header of column labels separated by commas and the new-line
# character (\n) at the end.
results_string = "file, somtc change rate (g/m2/y) \n"

# Next, we prompt the user for the location of the DayCent output
# data they wish to analyze.  For each .lis file found there we
# run our lis_reader() function, add the results to a plot using
# the .lis file name as a label, and write the results at the end
# of our results text string.

data_path = ("output\\")

for f in glob.glob(os.path.join(data_path, '*.lis')):
     # First, note the name of the .lis file being read
#    file_name = f.split("/")[-1]
    file_name = f[7:13]
    # In my .lis files, time is reported in the 1st column and somtc in
    # the 2nd column, and I have 3 header lines and 1 redundant
    # trailing line I need to skip:
    time, somtc, rate = lis_reader(f, 0, 1,2,1)
    # This adds my results as an x-y series to a plot
    plt.plot(time, somtc, label=file_name)
    # Display the results to the screen, and add the data to the
    # results string
    print (file_name,"average rate of somtc change: ", rate, "g/m2/y")
    results_string += "%s, %f \n" % (file_name, rate)

# After having lopped through and analyzed all the data, we create
# a time-stamped results directory within our data directory....
time_stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M")
results_path = data_path+"/"+time_stamp
if not os.path.exists(results_path):
    os.mkdir(results_path)
# ... add a title, legend, and axis labels to our plot and save...
plt.title("DayCent-Simulated Change in Soil Organic Carbon")
plt.legend(fontsize=10, loc=5).set_visible(True)
axes = plt.gca()
axes.set_xlim([1800,2120])
plt.xlabel("Time (Year)")
plt.ylabel("Soil Organic Carbon (g/m2/y)")
plt.savefig(results_path+"/plot.png")
# ... save our average somtc rate change data in .csv format...
results_file = results_path+"/results.csv"
output = open(results_file, "w")
output.write(results_string)
output.close()
# ... and archive a copy of the analysis script itself for future
# reference.
#shutil.copy(__file__, results_path)
print()
# THE END!

