
import tqdm
import numpy as np


def getFilepath():
	from tkinter.filedialog import askopenfilename
	from tkinter import Tk
	import re
	Tk().withdraw()
	filepath = askopenfilename();
	extension = filepath.split(".")[-1];
	dir_names = filepath.split("/");
	filename = dir_names[-1].split("nm")[0];
	unit = [int(s) for s in re.findall(r'\d+', filename)][-1]/1000;
	readfilepath = filepath.replace(dir_names[-1],"*."+extension); 
	return filepath,unit,filename,readfilepath;

def openData():
	import glob
	import skimage
	filepath,unit,filename,readfilepath = getFilepath();
	img = ((np.array([skimage.io.imread(file) for file in sorted(glob.glob(readfilepath))])).transpose(2,1,0))
	img = img[:,:,50:np.min([1550,img.shape[2]-50])];
	return img,unit,filename,filepath;


def getNiftiObject(filepath):
	import nibabel as nib;
	img = nib.load(filepath);
	header = img.header
	pixdim = header.get('pixdim');
	unit = pixdim[1]
	img_array = img.get_data();
	s = img_array.shape;
	if len(s)>3:
		img_array = img_array[:,:,:,0];
	return [img_array,unit];
	
	
def saveNiftiObject(data,unit,filepath):
	import nibabel as nib;
	print(unit);
	header_ = nib.Nifti1Header();
	header_['pixdim'] = np.array([ unit ,unit,unit,unit ,  1. ,  1. ,  1. ,  1. ], dtype=np.float32);
	nifti_img = nib.Nifti1Image(data, affine=None, header=header_);
	nib.save(nifti_img, filepath)


