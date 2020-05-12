
# -*- coding: utf-8 -*-
#MIT License

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:


#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.



from read_load import *
from porosityMethods import *
from tkinter.filedialog import askdirectory
import math

if __name__ == '__main__':
    print("\n######### Beginning the image processing #########\n")
    print("Open the image file (select the first image file .tif, or a volume .nii)")
    img,resolution,filename,filepath = openData();
    print("Sample filename:",filename)
    print("Resolution:",resolution,"um")
    resok = input ("Is the resolution correct? (y/n):")
    if(resok=='n'):
        resolution = float(input ("Enter the voxel resolution [micrometer]:"));
    porosity_estimated = float(input ("Enter the expected porosity [%]:"))
    resize_sample = input ("Resize sample? (y/n):")
    if resize_sample == 'y':
        from scipy.ndimage import zoom
        percentage = float(input ("Enter the upscaling percentage(example: 50):"));
        print("Resampling ",percentage,"%, original size:", img.shape);
        percentage = percentage/100;
        img = zoom(img,percentage);
        resolution = resolution *(1/percentage);
        print("Resampled size:", img.shape);
        print("New voxel resolution:", resolution, 'um');
    porosity_matrix,_ = run_porosity(img,resolution,porosity_estimated,resize=False,plot=False)
    filename = filename+'_porosity.nii'
    print("Saving porosity matrix as nifiti file:", filename," voxel resolution:", resolution)
    saveNiftiObject(porosity_matrix,resolution,filename)