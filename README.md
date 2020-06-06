# Favorite Focal Length
Find out your favorite camera focal length and many other interesting facts about you and your cameras by scanning all your photos. Demo result: http://sunnyspeed.com/share/20200605-sony-a7r3/output.html


## Quick Guide
1. Install exiftool for retrieving exif info from photo https://exiftool.org/

2. Install pygal for generating charts `pip install pygal` http://www.pygal.org/

3. Check out this repo

4. Make changes
   * **[imgFolders]** It can be a list of folders, but no need to include subfolders. (Subfolders are scanned automatically)
   * **[imgExtensions]** Add as needed
   * **[exiftoolPath]** Include the full path with .exe if running on Windows
   
5. Run
   * `python3 main.py` or `python main.py`
   
6. The result is also generated as an HTML file in the same directory


## Notes
   * Python 3 is recommended.
   * Try to scan one camera at a time, or cameras with same sensor size.
   * **The focal length is not converted if it is not in 35mm full frame.**
   * Only tested for very limited cameras. (Sony and Canon)
