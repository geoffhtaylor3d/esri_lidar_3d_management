# esri_lidar_3d_management
Esri tools supporting the management of LiDAR and 3D Data

Example 3D web-based download app using the results of the following scripts.
https://arcg.is/0Kb1ib

** DOCUMENTAION IN PROGRESS

Recommended workflow for preparing LiDAR and generating Image Surface Tiles as input to the below tools:
https://community.esri.com/t5/3d-blog/leveraging-lidar-template/ba-p/901767

<b>LiDAR & Imagery Data Processing Tools:</b>

1.) zip image tiles.... zip .tif, jpg, and non-folder based structured files files:
- Note GDB and folder zipping functions are complete but just need to be incorporated in codebase with conditional logic.
- Be sure to zip imagery tiles that have auxillary files ( > 1 file per image) prior to running # 3 below.
- Once imagery is zipped and zipped imagery + lidar tiles uploaded to the s3 bucket then run step 2.

2.) Get Tiled URL's from S3 Bucket:
- Process for recursively crawling a s3 bucket and writing all files to excel xlsx file.... optionally, supports writing existing Folders if enabled. Requires Boto3

3.) Attribute LiDAR or Image Polygon tiles with URL's:
- The process takes the output xlsx file from step 1 and attributes the tiles with the full https:// file paths in the AWS S3 Bucket. 

<b>3D Multipatch Data Management Tools:</b>

1.) Tile Multpiatch Models by Polgyon.. ex: LiDAR or Image Tile Grid:
- Uses best-fit area of the model to determing which polygon the model should be attributed for

2.) Batch Export Multipatch models for Data Management needs:
- Supports Zipped and Unzipped MultipatchSHP, MultipatchGDB, Colladae DAE files.

Again, this is in dev but all above scripts should be fully functional as described.
