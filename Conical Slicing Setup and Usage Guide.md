**Setup and Usage Guide**  
This is a guide ment for people who have little to no experience in coding or 3D printing.

**Set up**

1. Download python from:  
2. Go to the GitHub at, and copy the code the from the Main.py into a file of that name on your computer  
3. Go to your command prompt, and type in python \-m pip install STL, and then let it finish downloading.

simple as that it is set up

**Usage**  
**1\. Transform**

1. Open up your command prompt, and follow this formula, python3 “path/file\_name.py” and click enter.  
2. Now type tf for transformation, the first step in the Conical Slicing process.  
3. Now look at the 3d model you want to transform, and see if the overhangs are inward, or outward, and type that in the next spot.  
4. Now decide how many refinements you want, usually 2 or 3 is good, but the more you do, the longer it will take.  
5. Next, input the file path to the STL you want to transform, and put it there.  
6. Input the location of the folder of where you want the transformed file to be stored.  
7. Now wait for it to be done.

**2\. Slice**

1. Now put the transformed model into your slicer of cho, and slicer the slice model. I recommend change these setting first:  
   * Where you have your starter G-code, remove the primer line, and also put the line G90 in to make sure it uses absolute coordinates  
   * Set the bottom to 0 layers  
   * If you are using Prusa slicer, pick an infill with curved lines, not straight. If you are using Cura, you have more leniency.  
   * Change your travel settings to ramping lift, and the cone angle you want to slice at in degrees.  
   * Slow down the printing speed, I have done 20mm/s for infill, and 15mm/s for walls and top.

**3\. Back-Transform**

1. Next open up your command prompt again and type what you did at the start of the transformation step.  
2. Now type bt for back-transformation.  
3. Then type the same cone type you used for the transformation process.  
4. Also say the same cone angle.  
5. Next input the file path, and the file of the G-code file you want to back-transform, and put it there.  
6. Input the location of the folder of where you want the back-transformed file to be stored.  
7. After that say half the size of your printing area of the printer. First the x, then next the y. If you used cura for the slicing, try removing 5 from each the x and the y.  
8. Then just wait for it to be done.

   
I recommend you try to dial these settings in before printing for you first time, and if it doesn’t look right, it probably isn't right. Also, if you are more advanced, instead of saying cone type, you can write default. I have hand coded in my personal settings, and you can change them and save time later.

