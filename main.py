# sunnyspeed studio
# GitHub: https://github.com/sunnyspeedstudio/favorite-focal-length
# YouTube: https://www.youtube.com/sunnyspeedstudio
# Bili Bili: http://space.bilibili.com/36609936
# Tested using python 3


import subprocess
import os
import operator

# all image folders need to be scanned (the script will go through all subfolders)
imgFolders = ['full path to the image folder', 'full path to another image folder']
# all image extensions need to be scanned
imgExtensions = ('.jpg', '.JPG', '.DNG', '.CR2', '.NEF', '.ARW')
# exiftool path
exiftoolPath = 'exiftool'


totalImg = 0
focalLength = {}
lensID = {}

for imgFolder in imgFolders:
    for subfolder, folders, files in os.walk(imgFolder):
        for f in files:
            imgFile = subfolder + os.sep + f
            if imgFile.endswith(imgExtensions):
                process = subprocess.Popen([exiftoolPath, imgFile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) 
                exifInfo = {}
                exifInfo['Focal Length'] = 'Unknown'
                exifInfo['Lens ID'] = 'Unknown'

                # create the exif array for the image
                for line in process.stdout:
                    kv = line.strip().split(':', 1)
                    exifInfo[kv[0].strip()] = kv[1].strip()

                process.kill()

                # remove '35 mm equivalent'
                kv = exifInfo['Focal Length'].split(' (', 1)
                exifInfo['Focal Length'] = kv[0]

                if exifInfo['Focal Length'] in focalLength.keys():
                    focalLength[exifInfo['Focal Length']] += 1
                else:
                    focalLength[exifInfo['Focal Length']] = 1

                if exifInfo['Lens ID'] in lensID.keys():
                    lensID[exifInfo['Lens ID']] += 1
                else:
                    lensID[exifInfo['Lens ID']] = 1
                
                totalImg += 1
                print(totalImg, ':', imgFile, ':', exifInfo['Focal Length'], ':', exifInfo['Lens ID'])

# print out results
print('\nTotal Images Scanned: ', totalImg)

print('\nFocal Length:')
sorted_focalLength = sorted(focalLength.items(), key=operator.itemgetter(1), reverse=True)
for x in sorted_focalLength:
    print(x[0], '=', x[1], '-', "{:.2f}".format(x[1] * 100 / totalImg), '%')

print('\nLens:')
sorted_lensID = sorted(lensID.items(), key=operator.itemgetter(1), reverse=True)
for x in sorted_lensID:
    print(x[0], '=', x[1], '-', "{:.2f}".format(x[1] * 100 / totalImg), '%')