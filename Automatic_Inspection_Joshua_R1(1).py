import astropy.io.fits as fits 
import numpy as np 
import matplotlib.pyplot as plt 
from photutils.background import Background2D , MedianBackground
from photutils.segmentation import detect_sources
from astropy.convolution import convolve
from photutils.segmentation import make_2dgaussian_kernel
from photutils.segmentation import deblend_sources
from skimage.transform import rescale  , resize 
from matplotlib import gridspec 
from astropy.modeling import models , fitting
import matplotlib.image as mpimg
import os 
import shutil

#files from the loop go through get_Data 
#callback is initialized here for deblend_Data()

def get_Data (files , callback):
        

        #opening fits file and reading data
        Star = fits.open(files) 
        Data = Star[0].data

       #Adding dimenstions in shape to a variable to help plot the gaussian later 
        nx , ny = Data.shape 

        y , x = np.mgrid[:ny , :nx] 

        #go somewhere near the center of image
        star_x = 16 
        star_y = 16

        #set the max value to this point 
        Newmaxpix = Data[star_x,star_y] 

        #look around to see if we can find a greater max val 
        for pixx in range (star_x - 5 , star_x + 5):
                for pixy in range (star_y - 5 , star_y + 5):
                        if Newmaxpix < Data[pixx , pixy]:
                                #new max val
                                Newmaxpix = Data[pixx , pixy]
                                Newpixx = pixx
                                Newpixy = pixy


        #deblend the image by using deblend funciton  
        result , Object_Num = deblend_Data(Data) 
        
        if Object_Num == 1:
                d_gaus = gaussian_factory(Data , Newmaxpix, Newpixx , Newpixy)
                figure , axis = plt.subplots(1, 3)


                axis[0].imshow(d_gaus(x , y), origin = 'lower')
                axis[1].imshow(Data , origin = 'lower')
                axis[2].imshow(result , origin = 'lower')

                # print(files)

        else:
                Figure_1 , Axis = plt.subplots(1, 2)
                Axis[0].imshow(result , origin = 'lower')
                Axis[1].imshow(Data , origin = 'lower')
               
                

       #title as well as centereing
        plt.title(files , loc = 'right' )
       
       #get rid of the numbers and ticks on x and y axis
        plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[])
        plt.show()
        
        #close fits file 
        Star.close()

        #return Deblended Image
        return(Object_Num)

def gaussian_factory (Data , Newmaxpixel, Newpixx , Newpixy):
       #gaussian model making 
        #shape of the image

        nx , ny = Data.shape 

        y , x = np.mgrid[:ny , :nx] 

        fit_prod = fitting.LevMarLSQFitter() #fitting choices 

        #fixed value for the objects that are detected, in this case two 
        FWHMGuess = 1.5

        #insert any fixed settings here 
        fixedsettings = {}

        #Creating a Gaussian model 
        Img_Gaussian = models.Gaussian2D (x_mean= Newpixx , y_mean= Newpixy , x_stddev= FWHMGuess , y_stddev= FWHMGuess,
                                        amplitude = Newmaxpixel , fixed = fixedsettings)

        #fitting the model 
        Gaussian_fit = fit_prod(Img_Gaussian , x , y, Data)
        
        # gaussian_scaleup = rescale(Gaussian_fit , 5)
        return(Gaussian_fit)
       
        
        
#deblend function, returns a deblended version of fits image

def deblend_Data (Data):
        #setting threshold value for out detect sources function
        threshhold = 0.9
    

      #rescale image by a factor of 3 
        data_scaleup = rescale(Data , 5) 


        kernel = make_2dgaussian_kernel (1.5, size = 15)
        convolved_data = convolve(Data , kernel)

        #detecting how many sources there are in the image
        segment_mp = detect_sources(data_scaleup , threshhold , npixels = 2 )

        #deblend the sources found in the image
        deblend = deblend_sources(data_scaleup , segment_mp , npixels = 5 , 
                                nlevels = 50, contrast = 0.01, progress_bar = False)
        
        segment_mp_Objects = segment_mp.data 
        Object_Num = len(segment_mp.labels)

        #return deblended Image
        return (deblend , Object_Num) 
    

#Main function, loops through files and goes through get_data() and Utilizes a callback for deblend_Data()
for Images in os.listdir('C:/Users/Neuron Upload/Star_Images'):
        get_Data(Images , deblend_Data)
        
       
                



    