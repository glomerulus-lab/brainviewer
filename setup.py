import os
#mcmodels?

#generate images and colorbar (if necessary)
filename1 = os.path.join(os.getcwd(), "knox_connectivity_models/generate_colorbar_fig.py")
filename2 = os.path.join(os.getcwd(),"knox_connectivity_models/connectome_img_generator.py")
filename3 = os.path.join(os.getcwd(),"knox_connectivity_models/interactive_connectome2.py")
dirname1 = os.path.join(os.getcwd(),"knox_connectivity_models/flatmapImages")


#check if we need to 
if not os.path.exists("knox_connectivity_models/colorbar.png"):
    os.system('{} {}'.format('python', filename1))
else:
    print("knox_connectivity_models/colorbar.png already exists.")
#generate flatmap images if necessary
if not os.path.isdir("knox_connectivity_models/flatmapImages"):
    os.system('{} {} {}'.format('python', filename2, 'flatmap'))
else:
    print("knox_connectivity_models/flatmapImages already exists.")
    
#generate topview images if necessary
if not os.path.isdir("knox_connectivity_models/topviewImages"):
    os.system('{} {} {}'.format('python', filename2, 'topview'))
else:
    print("knox_connectivity_models/topviewImages already exists.")
#launch the program in top view
os.system('{} {} {}'.format('python', filename3, 'topview'))

