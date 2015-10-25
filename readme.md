#MotionDetector
MotionDetector detects when significant movement has occurs in a parsed video, an image is then saved along with the timestamp when a movement event has occured. The processing image showing what has moved in the frame is also saved. This code was was originally written to detect when a level crossing was down and a train went pass in a video that was several hours long without having to waste time watching the entire video.

It operates using the frame difference across the current frame and previous two frames. The difference frame is given by the maximum of the difference between the current frame and either of the previous two.

```python
def frame_diff(img_vold, img_old, new_img):
    img_diff0 = cv2.absdiff(new_img, img_old)
    img_diff1 = cv2.absdiff(img_old, img_vold)
    return cv2.bitwise_or(img_diff0, img_diff1)
```
The average value of the frame is taken, this is added to an array consisting of the last `n_sample`, by default 1000, if the current average exists `offset` times the standard deviation then an event is said to off occured. A frame will only be saved once initally triggered, the trigger will be set back to false when the critical conditions are no longer met.

## Setup & Quick Start
MotionDetector requires OpenCV and Numpy, it requires a path to the video file to process which must be an AVI or mp4 video, this is parsed via the `-v/--video_path` argument. To save the event images the `-u/--dump_path` argument should be parsed with a valid directory along with the `-i/--dump_images` command. To display the images the `-d/--display` argument should be parsed, and to set the logger to debug mode `-e`. To display help messages then the `-h` argument should be parsed.

```
git clone https://github.com/WillBrennan/MotionDetector MotionDetector
cd MotionDetector

python main.py -v <path to avi/mp4 video file> -u /media/psf/Will/datasets/MotionDetector -i -d -e
```
## Demonstration
![Demo on Level Crossing](https://raw.githubusercontent.com/WillBrennan/MotionDetector/master/demo.png "Demonstration")
