import os
import urllib
import subprocess
import platform
from distutils.dir_util import copy_tree

default_dir = "C:\Program Files (x86)\Katawa Shoujo"
patch_dir = "KatawaShoujoHD"
out_dir = "bin"

#Determine the base game install path
if os.path.exists("paths.txt"):
	f = open("paths.txt", "r")
	path = f.read().rstrip()
	f.close()
elif os.path.exists(default_dir):
	path = default_dir
else:
	while True:
		path = input("Enter the base game's directory: ")
		if os.path.exists(path):
			break
		print("Invalid directory entered.")

print("Found the game files at:",path)

#Exract the rpa file
if not os.path.exists("rpaExtract.exe"):
	print("You need to drop rpaExtract into the same directory as the build script for it to work.")
	print("You can find rpaExtract at https://iwanplays.itch.io/rpaex")
	raise Exception("rpaExtract not found")

print("Found rpaExtract")

#Copy the base game files to the output directory
copy_tree(path, out_dir)

print("Copied base game files")

#Hand the call to rpaExtract to wine if not on windows
user_os = platform.system()

rpa_path = os.path.join(path,'game/data.rpa')
extract_path = os.path.join(out_dir, 'game')

if user_os == "Windows":
	subprocess.call(['rpaExtract.exe', rpa_path, '-o', extract_path])
else:
	subprocess.call(['wine', 'rpaExtract.exe', rpa_path, '-o', extract_path])

print("Extracted rpa")

#Remove the rpa
os.remove(os.path.join(out_dir,"game/data.rpa"))

print("Removed redundant files")

copy_tree(patch_dir,out_dir)
print("Patched the game files, the game is now playable in the folder",out_dir,"by running KatawaShoujo.exe")
