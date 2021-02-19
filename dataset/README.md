# Generating a Target Keywords Dataset
## Overview
Follow the steps below to create your own keyword dataset from the google speech
commands and upload it to your Edge Impulse project. The generated dataset will
consist of your target keyword classes, plus a background noise class ('noise')
and another class ('unknown') that includes all the non-target keywords. The
possible keywords include "Yes" "No", "Up", "Down", "Left", "Right", "On",
"Off", "Stop", "Go", "Zero", "One", "Two", "Three", "Four", "Five", "Six",
"Seven", "Eight", and "Nine".

## Dependencies
Python scripts require python 3.

A Unix-like shell environment is needed for the find/xargs command. If you're
using Windows, I recommend running these commands with Git Bash.

Finally, the upload step assumes you have the Edge Impulse CLI installed and
added to your PATH. See the installation guide
[here](https://docs.edgeimpulse.com/docs/cli-installation).

```
# Get the google and edge impulse datasets and store them in a directory called 'data'
python download_data.py data

# Not all of the samples from the GSC dataset are 1 second long so drop samples with < 16000 points
# Note: assumes 44 byte WAV header size
find data -name '*.wav' -print0 | xargs -0 stat -c '%n %s' | awk '$2 < 32044 { print $1 }' | xargs rm

# Create listing files that split up the data into the target keywords, 'unknown' keywords, and 'noise'
# Here we use the target classes "up" and "down"
python split_data.py data up down

# Use the list files to upload data to edge impulse by class (let EI decide the train/test split)
for i in noise unknown up down; do xargs -0 < ${i}_list.txt edge-impulse-uploader --label ${i} --category split; done

# Clean up the list files
rm *_list.txt
```
