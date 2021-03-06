import matplotlib.pyplot as plt
import skimage
import numpy as np
import tqdm


# def resample_image(sitk_image, out_spacing=(2, 2, 2), is_label=False):
	# import SimpleITK as sitk
	# original_spacing = sitk_image.GetSpacing()
	# original_size = sitk_image.GetSize()

	# out_size = [int(np.round(original_size[0]*(original_spacing[0]/out_spacing[0]))),
				# int(np.round(original_size[1]*(original_spacing[1]/out_spacing[1]))),
				# int(np.round(original_size[2]*(original_spacing[2]/out_spacing[2])))]

	# resample = sitk.ResampleImageFilter()
	# resample.SetOutputSpacing(out_spacing)
	# resample.SetSize(out_size)
	# resample.SetOutputDirection(sitk_image.GetDirection())
	# resample.SetOutputOrigin(sitk_image.GetOrigin())
	# resample.SetTransform(sitk.Transform())
	# resample.SetDefaultPixelValue(sitk_image.GetPixelIDValue())

	# if is_label:
		# resample.SetInterpolator(sitk.sitkNearestNeighbor)
	# else:
# #		resample.SetInterpolator(sitk.sitkBSpline)
		# resample.SetInterpolator(sitk.sitkLinear)

	# return resample.Execute(sitk_image)


def histogram_normalization(img):
	img = (img/np.max(img));
	for z in tqdm.tqdm(range(img.shape[2])):
		# val = skimage.filters.threshold_otsu(img[:,:,z]);
		# obs = img[:,:,z].copy()
		# obs = obs[obs>val]
		# h,v = np.histogram(obs,100);
		# intensity = (v[1:]+v[:-1])/2.0;
		# cutoff = h[np.argmax(h)]*0.3;
		# p = np.where(h>cutoff);
		# min_intensity = intensity[p[0][0]];
		# max_intensity = intensity[p[0][-1]];	
		p2, p98 = np.percentile(img[:,:,z], (0.5, 99.5))
		img[:,:,z] = skimage.exposure.rescale_intensity(img[:,:,z], in_range=(p2, p98), out_range=(0,255));
	return img;

def createMask(filtered):
	from scipy.ndimage import label,binary_erosion
	from scipy.ndimage import distance_transform_edt as bwdist
	from skimage.filters import threshold_otsu
	val = threshold_otsu(filtered);
	mask = np.zeros(filtered.shape);
	for z in tqdm.tqdm(range(filtered.shape[2])):
		label_img = label(filtered[:,:,z]<=val)[0];
		mask[:,:,z] = binary_erosion(1-((label_img==label_img[0,0])*1));	
	dist_mask  = bwdist(mask[:,:,0]);
	radius = np.max(dist_mask);
	[x,y] = np.where(dist_mask==radius);
	x=int(x[0]);
	y=int(y[0]);
	z = int(filtered.shape[2]/2.0);
	radius = int(radius/2.0);
	# obs = filtered[:,:,100:500].copy();
	# mobs = mask[:,:,100:500].copy()
	# mobs = mobs==1;
	# obs = obs[mobs].flatten()
	masked = filtered*mask;
	obs = np.zeros([filtered.shape[0],filtered.shape[1],60])
	obs[:,:,:20] = masked[:,:,:20]
	obs[:,:,20:40] = masked[:,:,z-10:z+10]
	obs[:,:,40:60] = masked[:,:,filtered.shape[2]-20:filtered.shape[2]]
	obs = obs[obs>0]	
	return mask,obs;

def showData(img,filtered,segmented,pos=100):
	fig, axs = plt.subplots(2, 3)
	axs[0, 0].imshow(img[:,:,pos],cmap='gray');
	axs[0, 0].set_title('Original Image')
	axs[0, 1].imshow(filtered[:,:,pos],cmap='gray');
	axs[0, 1].set_title('Contrast and noise correction')	
	axs[0, 2].imshow(segmented[:,:,pos],cmap='gray');
	axs[0, 2].set_title('Segmented (1 = solid, 0 = pores)')	
	axs[1, 0].hist(img.flatten(),bins=100);
	axs[1, 1].hist(filtered.flatten(),bins=100);
	axs[1, 2].hist(segmented.flatten(),bins=100);	
	plt.show();
	
def showDataColor(porosity_matrix,radius_map,surface_map,pos=100):
	fig, axs = plt.subplots(2, 3)
	axs[0, 0].imshow(porosity_matrix[:,:,pos],cmap='gray');
	axs[0, 0].set_title('Porosity Matrix')
	axs[0, 1].imshow(radius_map[:,:,pos]);
	axs[0, 1].set_title('Pore Radius Map (m)')	
	axs[0, 2].imshow(surface_map[:,:,pos]);
	axs[0, 2].set_title('Surface Map (m2)')
	axs[1, 0].hist(porosity_matrix.flatten(),bins=100);
	axs[1, 1].hist(radius_map.flatten(),bins=100);
	axs[1, 2].hist(surface_map.flatten(),bins=100);	
	plt.show();	
