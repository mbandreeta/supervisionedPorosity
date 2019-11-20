import skimage
import tqdm
import numpy as np
from imageProcessing import *


def segmentSolidPhase(segmented,f,threshold):
	from scipy.ndimage import binary_dilation
	w=1;
	d = binary_dilation(segmented==1);
	d = d-((segmented==1)*1)
	positions = np.where(d>0);
	for idx in (range(positions[0].size)):
		[i,j,k] =  [positions[0][idx],positions[1][idx],positions[2][idx]];
		if f[i,j,k] >= threshold:
			segmented[i,j,k] = 1;



def segmentVoidPhase(segmented,f,threshold):
	from scipy.ndimage import binary_dilation
	w=1;
	d = binary_dilation(segmented==0);
	d = d-((segmented==0)*1)
	positions = np.where(d>0);
	for idx in (range(positions[0].size)):
		[i,j,k] =  [positions[0][idx],positions[1][idx],positions[2][idx]];
		if f[i,j,k] <= threshold:
			segmented[i,j,k] = 0;


def radiusMap(porosity_matrix,unit):
	from scipy.ndimage import median_filter 
	macropores = (porosity_matrix==1)*1;
	intermediate = porosity_matrix.copy();
	intermediate[macropores==1]=0;
	v = intermediate* (unit**3) *(3.0/(4.0*np.pi));
	r_eq = np.cbrt(v)
	surface = (r_eq**2)*np.pi ;
	from scipy.ndimage.morphology import distance_transform_edt as bwt
	dt = bwt(macropores)
	map_radius = r_eq+ (dt*unit);
	aux = (dt<np.sqrt(2))*dt * (unit**2);	
	surface_contact = aux*intermediate;
	map_surface = surface_contact+surface;
	return map_radius,map_surface;


def interactiveCorrectionNaive(Esolid,Evoid,filtered,mask,porosity_estimated=0,tolerance=2):
	porosity=0;
	error = np.abs(porosity_estimated-porosity)*100.0/porosity_estimated;
	step=10;
	segmented = filtered.copy();
	print("PorosityEntered","PorosityCalculated","LowThreshold","UpThreshold","     Error%")
	while(error>tolerance):
		print("      %5.1f            %5.1f           %5.1f            %5.1f            %5.1f" %(porosity_estimated,porosity,Evoid,Esolid,error))
		segmented = filtered.copy();#filtered.copy();
		segmented = ((segmented - Evoid)/(Esolid-Evoid));
		segmented[filtered>=Esolid]=1; # solid region
		segmented[filtered<=Evoid]=0;
		porosity_matrix=(1-segmented)*mask;
		porosity =  100.0*(np.sum(porosity_matrix)/np.sum(mask));
		nerror = np.abs(porosity_estimated-porosity)*100.0/porosity_estimated;
		if(nerror<error):
			error = nerror;
		else:
			step = step/2;
			error = nerror;
		if(porosity>porosity_estimated):
			Esolid=Esolid-step;
		else:
			Esolid=Esolid+step;
	print("      %5.1f            %5.1f           %5.1f            %5.1f            %5.1f" %(porosity_estimated,porosity,Evoid,Esolid,error))
	return porosity_matrix;
	
def run_porosity(img,unit,porosity_estimated,resize=True,plot=False,pos=100):
	from scipy.ndimage import median_filter 
	import SimpleITK as sitk
	print("Applying filter.");
	if(resize):
		sitk_image = resample_image(sitk.GetImageFromArray(img))
		img = sitk.GetArrayFromImage(sitk_image);	
	img = histogram_normalization(img)
	filtered = median_filter(img,2);
	print("Creating mask.");
	mask,obs = createMask(filtered);	
	print("Naive Adjustment");
	Evoid = skimage.filters.threshold_li(filtered);
	y,x = skimage.exposure.histogram(filtered[mask==1]);
	Esolid = np.argmax(y);
	print(Esolid,Evoid)
	porosity_matrix = interactiveCorrectionNaive(Esolid,Evoid,filtered,mask,porosity_estimated)
	segmented =(1-porosity_matrix)*mask;
	map_radius,map_surface = radiusMap(porosity_matrix,unit*2)
	print("Average sample porosity:", np.sum(porosity_matrix)/np.sum(mask))
	if(plot):
		showData(img,filtered,segmented,pos)
		showDataColor(porosity_matrix,map_radius,map_surface,pos)
	return porosity_matrix,map_radius,map_surface