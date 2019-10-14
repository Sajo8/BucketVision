# 2019 Pipeline

## Installing

### For Testing
  * opencv-python
  `pip install opencv-python==3.4.3.18`
    *This will **not** work if you want to run cscore as well*

  * pynetworktables
  `pip install pynetworktables`

### For Running
  * cscore
    *Note: cscore does not like virtual environments*
    - [Download Windows Port](https://github.com/pixelfelon/robotpy-cscore/releases/latest)
    - Follow instructions in the .pdf file

## Running

### For Testing

* Open command prompt
* cd to `BucketVision/2019 Pipeline`
* Open up OutlineViewer with these settings:
  ![outline viewer](https://i.imgur.com/Jmq1ZRy.png)
* run the file
  `py BucketVision_AngryEyes_2019.py -ip [ip address] -cam [no. of cameras] --test`
  for example:
  `py BucketVision_AngryEyes_2019.py -ip 127.0.0.1 -cam 1 --test`
* A new window should now popup with camera output from your PC. (won't work without a connected camera)

### For Running

*(No idea if this works)*

Do what you do for testing but without the `--test` flag

## More info on output

Check out `Angry_Eyes_Pipeline_ICD_V1.0.pdf` to learn more about the numbers output.

## Mac Build

### virtualenv

```bash
virtualenv -p /usr/local/bin/python3 venv
source venv/bin/activate
pip install numpy
pip install opencv-python==3.4.7.28
pip install Cython
```

### Compile opencv from source

```bash
git clone git@github.com:opencv/opencv.git
cd opencv

# create a build dir for our build config
mkdir -p build
cd build

# compile it with shared libs
cmake -DBUILD_SHARED_LIBS=ON -DCMAKE_BUILD_TYPE=RELEASE ../

# install it on your system
make install
```

### Install robotpy-cscore from source
```bash
git clone git@github.com:robotpy/robotpy-cscore.git
cd robotpy-cscore

# init git submodules
git submodule init
git submodule update

# install to your virtual machine above from robopy-cscore
pip3 install --no-build-isolation .
```
