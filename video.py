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


# all video folders need to be scanned (the script will go through all subfolders)
videoFolders = [  'path1',
                'path2' ]
# videoFolders = ['/Volumes/MEDIA/Camera - Old/2016-03 - Sony A6300', '/Volumes/MEDIA/Camera - Old/2016-12 - Sony A6500', '/Volumes/MEDIA/Camera - Old/2019-03 - Sony A6400', '/Volumes/MEDIA/Camera - Current/2018-03 - Sony A7R III']
# all video extensions need to be scanned
videoExtensions = ('.mp4', '.MP4')
# exiftool path
exiftoolPath = 'exiftool'


# funcions:
def formatDuration(s):
    hour = int(s / 3600)
    minute = int((s - hour * 3600) / 60)
    second = s - hour * 3600 - minute * 60
    return str(hour) + ':' + str(minute) + ':' + str(second)

def drawBarChart(title, data):
    value = []
    label = []
    for x in data:
        if ('(time in seconds)' in title):
            label.append(str(x[0]) + ' (' + formatDuration(x[1]) + ' - ' + str("{:.2f}".format(float(x[1]) * 100 / totalDuration)) + '%)')
        else:
            label.append(str(x[0]) + ' (' + str("{:.2f}".format(float(x[1]) * 100 / totalVideo)) + '%)')
            
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
    else:
        data = data.items()
    # printing
    for x in data:
        if ('(time in seconds)' in title):
            print(x[0], '=', x[1], '-', "{:.2f}".format(float(x[1]) * 100 / totalDuration), '%')
        else:
            print(x[0], '=', x[1], '-', "{:.2f}".format(float(x[1]) * 100 / totalVideo), '%')
    # generate chart
    drawBarChart(title, data)

def svgObject(title):
    return '<object type="image/svg+xml" data="svg/' + title.lower().replace(' ', '_') + '.svg"></object>'

def createHTML():
    separator = ', '

    html = """
        <h2>Scanned number of videos: %s</h2>
        <h3>Total size: %s, average size: %s</h3>
        <h3>Total duration: %s, average duration: %s</h3>
        <p>Scanned video folders: %s</p>
        <p>Powered by sunnyspeed studio @ <a href="https://github.com/sunnyspeedstudio/favorite-focal-length">GitHub</a>
        <a href="https://www.youtube.com/sunnyspeedstudio">YouTube</a></p>
    """%(totalVideo, fileSize, averageSize, formatDuration(totalDuration), formatDuration(averageDuration), separator.join(videoFolders))
    html += '<table width="100%">'
    html += '<tr><td width="50%">' + svgObject('Camera') + '</td><td width="50%">' + svgObject('Camera (time in seconds)') + '</td></tr>'
    html += '<tr><td>' + svgObject('Duration') + '</td><td>' + svgObject('Duration (time in seconds)') + '</td></tr>'
    html += '<tr><td>' + svgObject('Bitrate') + '</td><td>' + svgObject('Bitrate (time in seconds)') + '</td></tr>'
    html += '<tr><td>' + svgObject('Frame Rate') + '</td><td>' + svgObject('Frame Rate (time in seconds)') + '</td></tr>'
    html += '<tr><td>' + svgObject('Resolution') + '</td><td>' + svgObject('Resolution (time in seconds)') + '</td></tr>'
    html += '<tr><td>' + svgObject('Created Day') + '</td><td>' + svgObject('Created Day (time in seconds)') + '</td></tr>'
    html += '<tr><td>' + svgObject('Created Hour') + '</td><td>' + svgObject('Created Hour (time in seconds)') + '</td></tr>'
    html += '</table>'
    Html_file= open(htmlPath + "/output.html", "w")
    Html_file.write(html)
    Html_file.close()


# pickle file path
pickleFilePath = 'video.pkl'
# load saved videos info from pickle file to save time
# please delete local pickle file for a fresh new scan
scannedVideo = {}
if os.path.exists(pickleFilePath):
    scannedVideo = pickle.load(open('video.pkl', 'rb'))

# variables
totalVideo = 0
fileSize = 0
averageSize = 0
totalDuration = 0
averageDuration = 0

 # counters
duration = {   'Unknown':0,
                '>1h':0,
                '45m~1h':0,
                '30m~45m':0,
                '20m~30m':0,
                '10m~20m':0,
                '5m~10m':0,
                '1m~5m':0,
                '<1m':0 }
durationT = {   'Unknown':0,
                '>1h':0,
                '45m~1h':0,
                '30m~45m':0,
                '20m~30m':0,
                '10m~20m':0,
                '5m~10m':0,
                '1m~5m':0,
                '<1m':0 }
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
createHourT = {  '23':0,
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
createDayT = {   'Sunday':0,
                'Saturday':0,
                'Friday':0,
                'Thursday':0,
                'Wednesday':0,
                'Tuesday':0,
                'Monday':0,}
resolution = {}
resolutionT = {}
camera = {}
cameraT = {}
bitrate= {}
bitrateT= {}
frameRate = {}
frameRateT = {}


# scan through all video files
for videoFolder in videoFolders:
    for subfolder, folders, files in os.walk(videoFolder):
        for f in files:
            videoFile = subfolder + os.sep + f
            
            if videoFile.endswith(videoExtensions):
                exifInfo = {}
                if videoFile in scannedVideo.keys():    # this video was already scanned
                    exifInfo = scannedVideo[videoFile]
                else:
                    # prepare the exif holder
                    exifInfo['File Size'] = 'Unknown'               # not for charting

                    # the following strange numbers, such as 99999, is for handling the edge cases
                    # if the exifInfo is changed below, please delete pickle file to do a fresh new scan
                    exifInfo['Duration'] = 'Unknown'        # sony
                    exifInfo['Create Date'] = 'Unknown'             # break down to hour and day
                    exifInfo['Video Size'] = 'Unknown'
                    exifInfo['Device Model Name'] = 'Unknown'
                    exifInfo['Video Avg Bitrate'] = 'Unknown'
                    exifInfo['Video Avg Frame Rate'] = 'Unknown'

                    # retrieve exif from each video
                    process = subprocess.Popen([exiftoolPath, videoFile, '-api', 'largefilesupport=1'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) 
                    # create the exif array for the video
                    for line in process.stdout:
                        kv = line.strip().split(':', 1)
                        if kv[0].strip() in exifInfo:   # only save the tags we need
                            exifInfo[kv[0].strip()] = kv[1].strip()
                    process.kill()

                    # update scannedVideo with raw exif info, and save it back to pickle file
                    scannedVideo[videoFile] = exifInfo
                    pickle.dump(scannedVideo, open(pickleFilePath, "wb"))


                # special treatments on the exif data
                # 1. file size: remove MB in file size, eg: 8.3 MB
                kv = exifInfo['File Size'].split(' ')
                fileSize += float(kv[0])

                # 3. duration: from 0:01:17 to seconds
                durationInSecond = 0
                if ('s' in exifInfo['Duration']):
                    kv = exifInfo['Duration'].split('.')
                    durationInSecond = kv[0]
                else:
                    kv = exifInfo['Duration'].split(':')
                    durationInSecond = int(kv[0]) * 3600 + int(kv[1]) * 60 + int(kv[2])
                totalDuration += int(durationInSecond)

                # 5. hour and day: grab hour and day of the week from the date, eg: 2020:05:02 13:57:57.072-07:00
                kv = exifInfo['Create Date'].split(' ')
                kv1 = kv[0].split(':')
                d = datetime.datetime(int(kv1[0]), int(kv1[1]), int(kv1[2]))
                exifInfo['Create Day'] = d.strftime('%A')   # day of the week
                kv2 = kv[1].split(':')
                exifInfo['Create Hour'] = kv2[0]    # hour


                # counting
                t = int(durationInSecond)

                # duration
                if exifInfo['Duration'] == 'Unknown':
                    duration['Unknown'] += 1
                    durationT['Unknown'] += t
                else:
                    if int(durationInSecond) <= 60:
                        duration['<1m'] += 1
                        durationT['<1m'] += t
                    elif int(durationInSecond) > 60 and int(durationInSecond) <= 300:
                        duration['1m~5m'] += 1
                        durationT['1m~5m'] += t
                    elif int(durationInSecond) > 300 and int(durationInSecond) <= 600:
                        duration['5m~10m'] += 1
                        durationT['5m~10m'] += t
                    elif int(durationInSecond) > 600 and int(durationInSecond) <= 1200:
                        duration['10m~20m'] += 1
                        durationT['10m~20m'] += t
                    elif int(durationInSecond) > 1200 and int(durationInSecond) <= 1800:
                        duration['20m~30m'] += 1
                        durationT['20m~30m'] += t
                    elif int(durationInSecond) > 1800 and int(durationInSecond) <= 2700:
                        duration['30m~45m'] += 1
                        durationT['30m~45m'] += t
                    elif int(durationInSecond) > 2700 and int(durationInSecond) <= 3600:
                        duration['45m~1h'] += 1
                        durationT['45m~1h'] += t
                    elif int(durationInSecond) > 3600:
                        duration['>1h'] += 1
                        durationT['>1h'] += t

                # camera
                if exifInfo['Device Model Name'] in camera.keys():
                    camera[exifInfo['Device Model Name']] += 1
                    cameraT[exifInfo['Device Model Name']] += t
                else:
                    camera[exifInfo['Device Model Name']] = 1
                    cameraT[exifInfo['Device Model Name']] = t

                # create hour
                createHour[exifInfo['Create Hour']] += 1
                createHourT[exifInfo['Create Hour']] += t

                # create day
                createDay[exifInfo['Create Day']] += 1
                createDayT[exifInfo['Create Day']] += t

                # resolution
                if exifInfo['Video Size'] in resolution.keys():
                    resolution[exifInfo['Video Size']] += 1
                    resolutionT[exifInfo['Video Size']] += t
                else:
                    resolution[exifInfo['Video Size']] = 1
                    resolutionT[exifInfo['Video Size']] = t

                # bitrate
                if exifInfo['Video Avg Bitrate'] in bitrate.keys():
                    bitrate[exifInfo['Video Avg Bitrate']] += 1
                    bitrateT[exifInfo['Video Avg Bitrate']] += t
                else:
                    bitrate[exifInfo['Video Avg Bitrate']] = 1
                    bitrateT[exifInfo['Video Avg Bitrate']] = t

                # frame rate
                if exifInfo['Video Avg Frame Rate'] in frameRate.keys():
                    frameRate[exifInfo['Video Avg Frame Rate']] += 1
                    frameRateT[exifInfo['Video Avg Frame Rate']] += t
                else:
                    frameRate[exifInfo['Video Avg Frame Rate']] = 1
                    frameRateT[exifInfo['Video Avg Frame Rate']] = t
                
                # total video counter
                totalVideo += 1

                # print each video's exif info
                print(  totalVideo, ':', 
                        videoFile, ':', 
                        exifInfo['Duration'], ':', 
                        exifInfo['Create Day'], ':', 
                        exifInfo['Create Hour'], ':', 
                        exifInfo['Video Size'], ':', 
                        exifInfo['Device Model Name'], ':',
                        exifInfo['Video Avg Bitrate'], ':',
                        exifInfo['Video Avg Frame Rate'])


# print out final results
print('\nTotal scanned number of videos:', totalVideo)
if (totalVideo == 0):
    print('\nNo Video is found.')
else:
    averageSize = str("{:.1f}".format(float(fileSize / totalVideo))) + 'MB'
    if fileSize < 1024:
        fileSize = str(int(fileSize)) + 'MB'
    else:
        fileSize = str(int(fileSize / 1024)) + 'GB'
    print('Total size:', fileSize)
    print('Average size:', averageSize)
    print('Total duration:', formatDuration(totalDuration))
    averageDuration = int(totalDuration / totalVideo)
    print('Average duration:', formatDuration(averageDuration))

    # create a new folder to store charts and html
    htmlPath = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    os.makedirs(htmlPath)
    svgPath = htmlPath + '/svg'
    os.makedirs(svgPath)

    printResult('Camera', camera, 'value')
    printResult('Duration', duration, 'no')
    printResult('Created Hour', createHour, 'no')
    printResult('Created Day', createDay, 'no')
    printResult('Resolution', resolution, 'value')
    printResult('Bitrate', bitrate, 'value')
    printResult('Frame Rate', frameRate, 'value')

    printResult('Camera (time in seconds)', cameraT, 'value')
    printResult('Duration (time in seconds)', durationT, 'no')
    printResult('Created Hour (time in seconds)', createHourT, 'no')
    printResult('Created Day (time in seconds)', createDayT, 'no')
    printResult('Resolution (time in seconds)', resolutionT, 'value')
    printResult('Bitrate (time in seconds)', bitrateT, 'value')
    printResult('Frame Rate (time in seconds)', frameRateT, 'value')

    createHTML()

    print('\n\nThe result is saved in folder ' + htmlPath)

print('Thank you for using this tool!\n\n')