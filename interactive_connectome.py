import os
import sys


# validate cmd line args
if(len(sys.argv) != 3 and len(sys.argv) != 5):
    print("Usage : interactive_connectome.py -rt|-pc topview|flatmap [-v 1 | -v 2]") 
    exit()

if(sys.argv[1] not in ["-rt", "-pc"]):
    print("Usage : interactive_connectome.py -rt|-pc topview|flatmap [-v 1 | -v 2]") 
    exit()

if(sys.argv[1] == '-rt'):
    file_name = "real_time_plot.py"
else:
    file_name = "img_lookup_plot.py"
    
if(sys.argv[2] not in ["topview", "flatmap"]):
    print("Usage : interactive_connectome.py -rt|-pc topview|flatmap [-v 1 | -v 2]") 
    exit()

if(len(sys.argv) == 3):
    print("Calling {}".format(file_name))
    os.system('{} {} {}'.format('python', file_name, sys.argv[2]))
    exit()
else:
    if(sys.argv[3] not in ["-v"] or sys.argv[4] not in ["0", "1", "2"]):
        print("Usage : interactive_connectome.py -rt|-pc topview|flatmap [-v 1 | -v 2]") 
        exit()

print("Calling {}".format(file_name))
os.system('{} {} {} {} {}'.format('python', file_name, sys.argv[2], sys.argv[3], sys.argv[4]))


