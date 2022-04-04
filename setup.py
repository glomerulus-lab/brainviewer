import os

#mcmodels install necessary??

#generate images and colorbar (if necessary)
filename1 = os.path.join(os.getcwd(), "src/generate_colorbar_fig.py")
filename2 = os.path.join(os.getcwd(),"src/connectome_img_generator.py")
filename3 = os.path.join(os.getcwd(),"interactive_connectome2.py")

#check if we need to
if not os.path.exists("data/colorbar.png"):
    os.system('{} {}'.format('python', filename1))
    print("Colorbar generated.")
else:
    print("data/colorbar.png already exists.")
#generate flatmap images if necessary
if not os.path.isdir("data/flatmapImages"):
    os.system('{} {} {}'.format('python', filename2, 'flatmap'))
    print("Flatmap Images  Generated.")
else:
    print("data/flatmapImages already exists.")
    
#generate topview images if necessary
if not os.path.isdir("data/topviewImages"):
    os.system('{} {} {}'.format('python', filename2, 'topview'))
    print("Topview Images  Generated.")
else:
    print("data/topviewImages already exists.")
#launch the program in top view
os.system('{} {} {}'.format('python', filename3, 'topview'))
