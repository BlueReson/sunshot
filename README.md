# sunshot
Hour angle method via Skyfield Astro catalog in python

Imput: 

a. The lat lon location of the vessel

b. Fixes of the suns angle with timestamps in utc

c. Raw Gyro-heading from software matched with timestamps of the fixes 

Output:

a. Sunshot azimuth Zn, based on utc time of the fixes

b. From the sunshot and the observed solar angle folows the calculated true gyro heading

c. C-O (computed - observed heading): ave c-o  & standard deviation of the C-O  
