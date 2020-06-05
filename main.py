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


# all image folders need to be scanned (the script will go through all subfolders)
imgFolders = ['path1', 'path2']
# all image extensions need to be scanned
imgExtensions = ('.jpg', '.JPG', '.DNG', '.CR2', '.NEF', '.ARW')
# exiftool path
exiftoolPath = 'exiftool'


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
        if title == 'Aperture':
            data = {str(x[0]).replace('10000.0', 'Unknown') : x[1] for x in data}
            data = data.items()
        if title == 'Focal Length':
            data = {(str(x[0]) + 'mm') : x[1] for x in data}
            data = data.items()
        if title == 'Shutter Speed':
            data = {(str(x[0]).replace('-', '1/')).replace('.0', '') : x[1] for x in data}
            data = data.items()
        if title == 'Camera Temperature' or title == 'Ambient Temperature':
            data = {(str(x[0]) + 'C').replace('10000C', 'Unknown') : x[1] for x in data}
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
    html = """
        <h2>Scanned number of images: %s (total size: %s, average size: %s)</h2>
        <p>Scanned image folders: %s</p>
        <p>Powered by sunnyspeed studio @ <a href="https://github.com/sunnyspeedstudio/favorite-focal-length">GitHub</a>
        <a href="https://www.youtube.com/sunnyspeedstudio">YouTube</a></p>
    """%(totalImg, fileSize, avergeSize, separator.join(imgFolders))
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


# variables
totalImg = 0
fileSize = 0
avergeSize = 0
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
                # prepare the exif holder
                exifInfo = {}
                exifInfo['Focal Length'] = '0.0 mm'
                exifInfo['Lens ID'] = 'Unknown'
                exifInfo['Focus Distance 2'] = 'Unknown'        # sony
                exifInfo['Focus Distance Lower'] = 'Unknown'    # canon
                exifInfo['ISO'] = 'Unknown'
                exifInfo['Aperture'] = '10000.0'
                exifInfo['Shutter Speed'] = 'Unknown'
                exifInfo['Create Date'] = 'Unknown'
                exifInfo['Faces Detected'] = 'No or Unknown'
                exifInfo['File Size'] = 'Unknown'
                exifInfo['Camera Model Name'] = 'Unknown'
                exifInfo['Camera Temperature'] = '10000 C'
                exifInfo['Ambient Temperature'] = '10000 C'
                exifInfo['Focus Mode'] = 'Unknown'
                exifInfo['Sequence Length'] = 'Unknown'
                exifInfo['Shot Number In Continuous Burst'] = 'Unknown'

                # retrieve exif from each image
                process = subprocess.Popen([exiftoolPath, imgFile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) 
                # create the exif array for the image
                for line in process.stdout:
                    kv = line.strip().split(':', 1)
                    exifInfo[kv[0].strip()] = kv[1].strip()
                process.kill()

                # special treatments on the exif data
                # 1. focal length: remove '35 mm equivalent', eg: 2.7 mm (35 mm equivalent: 30.0 mm)
                kv = exifInfo['Focal Length'].split(' (', 1)
                exifInfo['Focal Length'] = kv[0].replace(' mm', '')
                # 2. hour and day: grab hour and day of the week from the date, eg: 2020:05:02 13:57:57.072-07:00
                kv = exifInfo['Create Date'].split(' ')
                kv1 = kv[0].split(':')
                d = datetime.datetime(int(kv1[0]), int(kv1[1]), int(kv1[2]))
                exifInfo['Create Day'] = d.strftime('%A')   # day of the week
                kv2 = kv[1].split(':')
                exifInfo['Create Hour'] = kv2[0]    # hour
                # 3. focus distance: Canon is different from Sony
                if exifInfo['Focus Distance 2'] == 'Unknown' and exifInfo['Focus Distance Lower'] != 'Unknown':
                    exifInfo['Focus Distance 2'] = exifInfo['Focus Distance Lower']     # canon
                if exifInfo['Focus Distance 2'] != 'Unknown':
                    kv = exifInfo['Focus Distance 2'].split(' ')    # remove 'm'
                    exifInfo['Focus Distance 2'] = kv[0]
                # 4. file size: remove MB in file size, eg: 8.3 MB
                kv = exifInfo['File Size'].split(' ')
                fileSize += float(kv[0])
                # 5. shutter speed: replace 1/ in shutter speed with - for sorting purpose, eg: 1/125
                exifInfo['Shutter Speed'] = exifInfo['Shutter Speed'].replace('1/', '-')
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
                        exifInfo['ISO'], ':', 
                        exifInfo['Aperture'].replace('10000.0', 'Unknown'), ':', 
                        exifInfo['Shutter Speed'].replace('-', '1/'), ':', 
                        exifInfo['Create Day'], ':', 
                        exifInfo['Create Hour'], ':', 
                        exifInfo['Faces Detected'], ':', 
                        (exifInfo['Camera Temperature'] + 'C').replace('10000C', 'Unknown'), ':',
                        (exifInfo['Ambient Temperature'] + 'C').replace('10000C', 'Unknown'), ':',
                        exifInfo['Focus Mode'], ':',
                        exifInfo['Sequence Length'])


# print out final results
print('\nTotal scanned number of images:', totalImg)
avergeSize = str("{:.1f}".format(float(fileSize / totalImg))) + 'MB'
if fileSize < 1024:
    fileSize = str(int(fileSize)) + 'MB'
else:
    fileSize = str(int(fileSize / 1024)) + 'GB'
print('Total size:', fileSize)
print('Average size:', avergeSize)

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

separator = ', '
createHTML()

print('\n\nThe result is saved in folder ' + htmlPath)
print('Thank you for using this tool!\n\n')