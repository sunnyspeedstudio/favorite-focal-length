# sunnyspeed studio
# GitHub: https://github.com/sunnyspeedstudio/favorite-focal-length
# YouTube: https://www.youtube.com/sunnyspeedstudio
# bilibili: http://space.bilibili.com/36609936
# Tested using python 3 under mac and windows


import subprocess
import os
import operator
import datetime
import pygal
import pickle


# all image folders need to be scanned (the script will go through all subfolders)
imgFolders = [  'path1',
                'path2' ]
# imgFolders = ['/Volumes/MEDIA/Camera - Current/2020-07 - Sony ZV-1/2020-07']
# all image extensions need to be scanned
imgExtensions = ('.jpg', '.JPG', '.DNG', '.CR2', '.NEF', '.ARW')
# exiftool path
exiftoolPath = 'exiftool'


# funcions:
def drawBarChart(title, data):
    value = []
    label = []
    for x in data:
        label.append(str(x[0]) + ' (' + str("{:.2f}".format(float(x[1]) * 100 / totalImg)) + '%)')
        value.append(x[1])

    bar_chart = pygal.HorizontalBar(legend_at_bottom=True)
    bar_chart.x_labels =label
    bar_chart.add(title, value)
    bar_chart.render_to_file(svgPath + '/' + title.lower().replace(' ', '_') + '.svg')

def printResult(title, data, sort):
    print('\n')
    print(title)
    # sorting
    if sort == 'value':
        data = sorted(data.items(), key=operator.itemgetter(1), reverse=False)
    elif sort == 'key':
        # convert key to float or int for sorting
        if title == 'Aperture' or title == 'Focal Length' or title == 'Shutter Speed':
            num_data = {float(k) : v for k, v in data.items()}
        else:   # ISO, Camera Temperature, Ambient Temperature
            num_data = {int(k) : v for k, v in data.items()}
        data = sorted(num_data.items(), reverse=True)
        
        # format
        if title == 'Focal Length':
            data = {(str(x[0]) + 'mm') : x[1] for x in data}
            data = data.items()
        if title == 'ISO':
            data = {str(x[0]).replace('99999999', 'Unknown') : x[1] for x in data}
            data = data.items()
        if title == 'Aperture':
            data = {str(x[0]).replace('99999.0', 'Unknown') : x[1] for x in data}
            data = data.items()
        if title == 'Shutter Speed':
            data = {(str(x[0]).replace('-', '1/')).replace('.0', '').replace('99999', 'Unknown') : x[1] for x in data}
            data = data.items()
        if title == 'Camera Temperature' or title == 'Ambient Temperature':
            data = {(str(x[0]) + 'C').replace('99999C', 'Unknown') : x[1] for x in data}
            data = data.items()
    else:
        data = data.items()
    # printing
    for x in data:
        print(x[0], '=', x[1], '-', "{:.2f}".format(float(x[1]) * 100 / totalImg), '%')
    # generate chart
    drawBarChart(title, data)

def svgObject(title):
    return '<object type="image/svg+xml" data="svg/' + title.lower().replace(' ', '_') + '.svg" style="height:90%"></object>'

def createHTML():
    separator = ', '

    html = """
        <h2>Scanned number of images: %s (total size: %s, average size: %s)</h2>
        <p>Scanned image folders: %s</p>
        <p>Powered by sunnyspeed studio @ <a href="https://github.com/sunnyspeedstudio/favorite-focal-length">GitHub</a>
        <a href="https://www.youtube.com/sunnyspeedstudio">YouTube</a></p>
    """%(totalImg, fileSize, averageSize, separator.join(imgFolders))
    html += svgObject('Camera')
    html += svgObject('Focal Length')
    html += svgObject('Lens')
    html += svgObject('Focus Distance')
    html += svgObject('Focus Mode')
    html += svgObject('Shot Mode')
    html += svgObject('ISO')
    html += svgObject('Aperture')
    html += svgObject('Shutter Speed')
    html += svgObject('Faces Detected')
    html += svgObject('Created Day')
    html += svgObject('Created Hour')
    html += svgObject('Ambient Temperature')
    html += svgObject('Camera Temperature')
    Html_file= open(htmlPath + "/output.html", "w")
    Html_file.write(html)
    Html_file.close()


# pickle file path
pickleFilePath = 'image.pkl'
# load saved images info from pickle file to save time
# please delete local pickle file for a fresh new scan
scannedImg = {}
if os.path.exists(pickleFilePath):
    scannedImg = pickle.load(open('image.pkl', 'rb'))

# variables
totalImg = 0
fileSize = 0
averageSize = 0
 # counters: 14 of them
focalLength = {}
lensID = {}
focusDistance = {   'Unknown':0,
                    '>10m':0,
                    '5~10m':0,
                    '2~5m':0,
                    '1~2m':0,
                    '0.5~1m':0,
                    '0.2~0.5m':0,
                    '0~0.2m':0 }
iso = {}
aperture = {}
shutterSpeed = {}
createHour = {  '23':0,
                '22':0,
                '21':0,
                '20':0,
                '19':0,
                '18':0,
                '17':0,
                '16':0,
                '15':0,
                '14':0,
                '13':0,
                '12':0,
                '11':0,
                '10':0,
                '09':0,
                '08':0,
                '07':0,
                '06':0,
                '05':0,
                '04':0,
                '03':0,
                '02':0,
                '01':0,
                '00':0 }
createDay = {   'Sunday':0,
                'Saturday':0,
                'Friday':0,
                'Thursday':0,
                'Wednesday':0,
                'Tuesday':0,
                'Monday':0,}
facesDetected = {}
camera = {}
cameraTemp = {}
ambientTemp = {}
focusMode= {}
shotMode = { 'Continuous':0, 'Single':0 }


# scan through all image files
for imgFolder in imgFolders:
    for subfolder, folders, files in os.walk(imgFolder):
        for f in files:
            imgFile = subfolder + os.sep + f
            
            if imgFile.endswith(imgExtensions):
                exifInfo = {}
                if imgFile in scannedImg.keys():    # this image was already scanned
                    exifInfo = scannedImg[imgFile]
                else:
                    # prepare the exif holder
                    exifInfo['File Size'] = 'Unknown'               # not for charting

                    # the following strange numbers, such as 99999, is for handling the edge cases
                    # if the exifInfo is changed below, please delete pickle file to do a fresh new scan
                    exifInfo['Focal Length'] = '0.0 mm'
                    exifInfo['Lens ID'] = 'Unknown'
                    exifInfo['Focus Distance 2'] = 'Unknown'        # 1 of 2: sony
                    exifInfo['Focus Distance Lower'] = 'Unknown'    # 2 of 2: canon
                    exifInfo['ISO'] = '99999999'
                    exifInfo['Aperture'] = '99999.0'
                    exifInfo['Shutter Speed'] = '99999'
                    exifInfo['Create Date'] = 'Unknown'             # break down to hour and day
                    exifInfo['Faces Detected'] = 'No or Unknown'
                    exifInfo['Camera Model Name'] = 'Unknown'
                    exifInfo['Camera Temperature'] = '99999 C'
                    exifInfo['Ambient Temperature'] = '99999 C'
                    exifInfo['Focus Mode'] = 'Unknown'
                    exifInfo['Sequence Length'] = 'Unknown'                     # 1 of 2: sony
                    exifInfo['Shot Number In Continuous Burst'] = 'Unknown'     # 2 of 2: canon

                    # retrieve exif from each image
                    process = subprocess.Popen([exiftoolPath, imgFile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) 
                    # create the exif array for the image
                    for line in process.stdout:
                        kv = line.strip().split(':', 1)
                        if kv[0].strip() in exifInfo:   # only save the tags we need
                            exifInfo[kv[0].strip()] = kv[1].strip()
                    process.kill()

                    # update scannedImg with raw exif info, and save it back to pickle file
                    scannedImg[imgFile] = exifInfo
                    pickle.dump(scannedImg, open(pickleFilePath, "wb"))


                # special treatments on the exif data
                # 1. file size: remove MB in file size, eg: 8.3 MB
                kv = exifInfo['File Size'].split(' ')
                fileSize += float(kv[0])

                # 2. focal length: remove '35 mm equivalent', eg: 2.7 mm (35 mm equivalent: 30.0 mm) or 0.0 mm
                kv = exifInfo['Focal Length'].split(' ', 1)
                exifInfo['Focal Length'] = kv[0]

                # 3. focus distance: Canon is different from Sony
                if exifInfo['Focus Distance 2'] == 'Unknown' and exifInfo['Focus Distance Lower'] != 'Unknown':
                    exifInfo['Focus Distance 2'] = exifInfo['Focus Distance Lower']     # canon
                if exifInfo['Focus Distance 2'] != 'Unknown':
                    exifInfo['Focus Distance 2'] = exifInfo['Focus Distance 2'].replace(' m', '')   # remove 'm'

                # 4. shutter speed: replace 1/ in shutter speed with - for sorting purpose, eg: 1/125
                exifInfo['Shutter Speed'] = exifInfo['Shutter Speed'].replace('1/', '-')

                # 5. hour and day: grab hour and day of the week from the date, eg: 2020:05:02 13:57:57.072-07:00
                kv = exifInfo['Create Date'].split(' ')
                kv1 = kv[0].split(':')
                d = datetime.datetime(int(kv1[0]), int(kv1[1]), int(kv1[2]))
                exifInfo['Create Day'] = d.strftime('%A')   # day of the week
                kv2 = kv[1].split(':')
                exifInfo['Create Hour'] = kv2[0]    # hour

                # 6. temperature: remove C in the camera temperature, eg: 14 C
                exifInfo['Camera Temperature'] = exifInfo['Camera Temperature'].replace(' C', '')
                exifInfo['Ambient Temperature'] = exifInfo['Ambient Temperature'].replace(' C', '')
                
                # 7. shot mode
                if exifInfo['Sequence Length'] == 'Continuous' or (exifInfo['Shot Number In Continuous Burst'] != '0' and exifInfo['Shot Number In Continuous Burst'] != 'Unknown'):
                    exifInfo['Sequence Length'] = 'Continuous'
                else:
                    exifInfo['Sequence Length'] = 'Single'


                # counting
                # focal length
                if exifInfo['Focal Length'] in focalLength.keys():
                    focalLength[exifInfo['Focal Length']] += 1
                else:
                    focalLength[exifInfo['Focal Length']] = 1

                # lens
                if exifInfo['Lens ID'] in lensID.keys():
                    lensID[exifInfo['Lens ID']] += 1
                else:
                    lensID[exifInfo['Lens ID']] = 1

                # focus distance
                if exifInfo['Focus Distance 2'] == 'Unknown':
                    focusDistance['Unknown'] += 1
                elif exifInfo['Focus Distance 2'] == 'inf':
                    focusDistance['>10m'] += 1
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

                # iso
                if exifInfo['ISO'] in iso.keys():
                    iso[exifInfo['ISO']] += 1
                else:
                    iso[exifInfo['ISO']] = 1

                # aperture
                if exifInfo['Aperture'] in aperture.keys():
                    aperture[exifInfo['Aperture']] += 1
                else:
                    aperture[exifInfo['Aperture']] = 1

                # shutter speed
                if exifInfo['Shutter Speed'] in shutterSpeed.keys():
                    shutterSpeed[exifInfo['Shutter Speed']] += 1
                else:
                    shutterSpeed[exifInfo['Shutter Speed']] = 1

                # create hour
                createHour[exifInfo['Create Hour']] += 1

                # create day
                createDay[exifInfo['Create Day']] += 1

                # faces detected
                if exifInfo['Faces Detected'] == '0':
                    exifInfo['Faces Detected'] = 'No or Unknown'
                if exifInfo['Faces Detected'] in facesDetected.keys():
                    facesDetected[exifInfo['Faces Detected']] += 1
                else:
                    facesDetected[exifInfo['Faces Detected']] = 1

                # camera
                if exifInfo['Camera Model Name'] in camera.keys():
                    camera[exifInfo['Camera Model Name']] += 1
                else:
                    camera[exifInfo['Camera Model Name']] = 1

                # camera temperature
                if exifInfo['Camera Temperature'] in cameraTemp.keys():
                    cameraTemp[exifInfo['Camera Temperature']] += 1
                else:
                    cameraTemp[exifInfo['Camera Temperature']] = 1

                # ambient temperature
                if exifInfo['Ambient Temperature'] in ambientTemp.keys():
                    ambientTemp[exifInfo['Ambient Temperature']] += 1
                else:
                    ambientTemp[exifInfo['Ambient Temperature']] = 1

                # focus mode
                if exifInfo['Focus Mode'] in focusMode.keys():
                    focusMode[exifInfo['Focus Mode']] += 1
                else:
                    focusMode[exifInfo['Focus Mode']] = 1

                # continuous shot
                if exifInfo['Sequence Length'] == 'Continuous':
                    shotMode['Continuous'] += 1
                else:
                    shotMode['Single'] += 1
                
                # total image counter
                totalImg += 1

                # print each image's exif info
                print(  totalImg, ':', 
                        imgFile, ':', 
                        (exifInfo['Focal Length'] + 'mm'), ':', 
                        exifInfo['Lens ID'], ':', 
                        exifInfo['Focus Distance 2'], ':', 
                        exifInfo['ISO'].replace('99999999', 'Unknown'), ':', 
                        exifInfo['Aperture'].replace('99999.0', 'Unknown'), ':', 
                        exifInfo['Shutter Speed'].replace('-', '1/').replace('99999', 'Unknown'), ':', 
                        exifInfo['Create Day'], ':', 
                        exifInfo['Create Hour'], ':', 
                        exifInfo['Faces Detected'], ':', 
                        exifInfo['Camera Model Name'], ':',
                        (exifInfo['Camera Temperature'] + 'C').replace('99999C', 'Unknown'), ':',
                        (exifInfo['Ambient Temperature'] + 'C').replace('99999C', 'Unknown'), ':',
                        exifInfo['Focus Mode'], ':',
                        exifInfo['Sequence Length'])


# print out final results
print('\nTotal scanned number of images:', totalImg)
if (totalImg == 0):
    print('\nNo image is found.')
else:
    averageSize = str("{:.1f}".format(float(fileSize / totalImg))) + 'MB'
    if fileSize < 1024:
        fileSize = str(int(fileSize)) + 'MB'
    else:
        fileSize = str(int(fileSize / 1024)) + 'GB'
    print('Total size:', fileSize)
    print('Average size:', averageSize)

    # create a new folder to store charts and html
    htmlPath = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    os.makedirs(htmlPath)
    svgPath = htmlPath + '/svg'
    os.makedirs(svgPath)

    printResult('Focal Length', focalLength, 'key')
    printResult('Lens', lensID, 'value')
    printResult('Camera', camera, 'value')
    printResult('Focus Distance', focusDistance, 'no')
    printResult('ISO', iso, 'key')
    printResult('Aperture', aperture, 'key')
    printResult('Shutter Speed', shutterSpeed, 'key')
    printResult('Created Hour', createHour, 'no')
    printResult('Created Day', createDay, 'no')
    printResult('Faces Detected', facesDetected, 'value')
    printResult('Camera Temperature', cameraTemp, 'key')
    printResult('Ambient Temperature', ambientTemp, 'key')
    printResult('Focus Mode', focusMode, 'value')
    printResult('Shot Mode', shotMode, 'no')

    createHTML()

    print('\n\nThe result is saved in folder ' + htmlPath)

print('Thank you for using this tool!\n\n')