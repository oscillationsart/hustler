# ABOUT #

Hustler is a VR-specific video production workflow that will help on-set by ensuring your machines are busy (and your people are free for other tasks).

The primary goals are:
- Reduce time it takes to identify any issues with the footage (e.g. missing or corrupted files) to minutes
- Organize your footage neatly for your post-production team
- Get your dailies done, well, daily

# SYSTEM REQUIREMENTS #

While most custom code in this project is cross-platform as much as possible, the only supported OS at this point is Windows 10. In real life, codek and stitching software compatibility is much greater in Windows environment, and GPU performance is typically higher in Windows as compared to MacOS.

You can probably make everything work under MacOS with minor modifications.

Stitching parts of the workflow will certainly benefit from a strong GPU (or potentially a couple of them), but you can always tweak the settings and/or the workflow to run this on anything that provides comfortable web browsing experience.

# INSTALLATION #

- Install Chocolatey https://chocolatey.org/install
- Install Python 3 `choco install python`
- Upgrade pip `python -m pip install --upgrade pip`
- Install pipenv `pip install --user pipenv`
- Install Jenkins `choco install jenkins`
- Install ffmpeg `choco install ffmpeg`
- Install MediaInfo CLI `choco install mediainfo-cli`
- Move to the directory where you cloned hustler `cd c:\osc\hustler`
- Install Python dependencies: `python -m pipenv install`

# USAGE #

The following steps are supported in the workflow:

## TODO sort through footage
Processes input of raw camera folders, and creates a folder structure with symlinks to simplify navigation and management while maintaining source files untouched 

## create_wonder_batch.py
Go over the folder structure and creates batch files for WonderStitch

## burn_in_timecodes.py
Burns in timecode, frame number and file name information in each file (around nadir)

