# sunnyspeed studio
# GitHub: https://github.com/sunnyspeedstudio/favorite-focal-length
# YouTube: https://www.youtube.com/sunnyspeedstudio
# bilibili: http://space.bilibili.com/36609936
# Tested using python 3 under mac and windows


import subprocess
import os
import operator
import datetime


# all image folders need to be scanned (the script will go through all subfolders)
imgFolders = ['path 1', 'path 2']
# all image extensions need to be scanned
imgExtensions = ('.jpg', '.JPG', '.DNG', '.CR2', '.NEF', '.ARW')
# exiftool path
exiftoolPath = 'exiftool'


def printResult(title, data):
    print('\n')
    print(title)
    sorted_data = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
    for x in sorted_data:
        print(x[0], '=', x[1], '-', "{:.2f}".format(x[1] * 100 / totalImg), '%')


totalImg = 0
focalLength = {}
lensID = {}
focusDistance = {   '0~0.2m':0, 
                    '0.2~0.5m':0,
                    '0.5~1m':0,
                    '1~2m':0,
                    '2~5m':0,
                    '5~10m':0,
                    '>10m':0,
                    'Unknown':0 }
iso = {}
aperture = {}
shutterSpeed = {}
createHour = {}
createDay = {}
facesDetected = {}


for imgFolder in imgFolders:
    for subfolder, folders, files in os.walk(imgFolder):
        for f in files:
            imgFile = subfolder + os.sep + f
            if imgFile.endswith(imgExtensions):
                process = subprocess.Popen([exiftoolPath, imgFile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) 
                exifInfo = {}
                exifInfo['Focal Length'] = 'Unknown'
                exifInfo['Lens ID'] = 'Unknown'
                exifInfo['Focus Distance 2'] = 'Unknown'        # sony
                exifInfo['Focus Distance Lower'] = 'Unknown'    # canon
                exifInfo['ISO'] = 'Unknown'
                exifInfo['Aperture'] = 'Unknown'
                exifInfo['Shutter Speed'] = 'Unknown'
                exifInfo['Create Date'] = 'Unknown'
                exifInfo['Faces Detected'] = 'Unknown'


                # create the exif array for the image
                for line in process.stdout:
                    kv = line.strip().split(':', 1)
                    exifInfo[kv[0].strip()] = kv[1].strip()

                process.kill()

                # Special treatments
                # 1. remove '35 mm equivalent', eg: 2.7 mm (35 mm equivalent: 30.0 mm)
                kv = exifInfo['Focal Length'].split(' (', 1)
                exifInfo['Focal Length'] = kv[0]
                # 2. grab hour from date, eg: 2020:05:02 13:57:57.072-07:00
                kv = exifInfo['Create Date'].split(' ')
                kv1 = kv[0].split(':')
                d = datetime.datetime(int(kv1[0]), int(kv1[1]), int(kv1[2]))
                exifInfo['Create Day'] = d.strftime('%A')
                kv2 = kv[1].split(':')
                exifInfo['Create Hour'] = kv2[0]
                # 3. focus distance, Canon is different from Sony
                if exifInfo['Focus Distance 2'] == 'Unknown' and exifInfo['Focus Distance Lower'] != 'Unknown':
                    exifInfo['Focus Distance 2'] = exifInfo['Focus Distance Lower']
                if exifInfo['Focus Distance 2'] != 'Unknown':
                    kv = exifInfo['Focus Distance 2'].split(' ')
                    exifInfo['Focus Distance 2'] = kv[0]


                if exifInfo['Focal Length'] in focalLength.keys():
                    focalLength[exifInfo['Focal Length']] += 1
                else:
                    focalLength[exifInfo['Focal Length']] = 1

                if exifInfo['Lens ID'] in lensID.keys():
                    lensID[exifInfo['Lens ID']] += 1
                else:
                    lensID[exifInfo['Lens ID']] = 1

                if exifInfo['Focus Distance 2'] == 'Unknown':
                    focusDistance['Unknown'] += 1
                else:
                    if float(exifInfo['Focus Distance 2']) <= 0.2:
                        focusDistance['0~0.2m'] += 1
                    elif float(exifInfo['Focus Distance 2']) > 0.2 and float(exifInfo['Focus Distance 2']) <= 0.5:
                        focusDistance['0.2~0.5m'] += 1
                    elif float(exifInfo['Focus Distance 2']) > 0.5 and float(exifInfo['Focus Distance 2']) <= 1:
                        focusDistance['0.5~1m'] += 1
                    elif float(exifInfo['Focus Distance 2']) > 1 and float(exifInfo['Focus Distance 2']) <= 2:
                        focusDistance['1~2m'] += 1
                    elif float(exifInfo['Focus Distance 2']) > 2 and float(exifInfo['Focus Distance 2']) <= 5:
                        focusDistance['2~5m'] += 1
                    elif float(exifInfo['Focus Distance 2']) > 5 and float(exifInfo['Focus Distance 2']) <= 10:
                        focusDistance['5~10m'] += 1
                    elif float(exifInfo['Focus Distance 2']) > 10:
                        focusDistance['>10m'] += 1

                if exifInfo['ISO'] in iso.keys():
                    iso[exifInfo['ISO']] += 1
                else:
                    iso[exifInfo['ISO']] = 1

                if exifInfo['Aperture'] in aperture.keys():
                    aperture[exifInfo['Aperture']] += 1
                else:
                    aperture[exifInfo['Aperture']] = 1

                if exifInfo['Shutter Speed'] in shutterSpeed.keys():
                    shutterSpeed[exifInfo['Shutter Speed']] += 1
                else:
                    shutterSpeed[exifInfo['Shutter Speed']] = 1

                if exifInfo['Create Hour'] in createHour.keys():
                    createHour[exifInfo['Create Hour']] += 1
                else:
                    createHour[exifInfo['Create Hour']] = 1

                if exifInfo['Create Day'] in createDay.keys():
                    createDay[exifInfo['Create Day']] += 1
                else:
                    createDay[exifInfo['Create Day']] = 1

                if exifInfo['Faces Detected'] in facesDetected.keys():
                    facesDetected[exifInfo['Faces Detected']] += 1
                else:
                    facesDetected[exifInfo['Faces Detected']] = 1
                
                totalImg += 1
                print(totalImg, ':', imgFile, ':', exifInfo['Focal Length'], ':', exifInfo['Lens ID'], ':', exifInfo['Focus Distance 2'], ':', exifInfo['ISO'], ':', exifInfo['Aperture'], ':', exifInfo['Shutter Speed'], ':', exifInfo['Create Day'], ':', exifInfo['Create Hour'], ':', exifInfo['Faces Detected'])


# print out results
print('\nTotal Images Scanned: ', totalImg)

printResult('Focal Length:', focalLength)
printResult('Lens:', lensID)
printResult('Focus Distance:', focusDistance)
printResult('ISO:', iso)
printResult('Aperture:', aperture)
printResult('Shutter Speed:', shutterSpeed)
printResult('Created Hour:', createHour)
printResult('Created Day:', createDay)
printResult('Faces Detected:', facesDetected)