Instruction:

Download the github
```
cd ~
git clone https://github.com/lbaitemple/suiron_raspberrypi/
```

Install RPiHAT
```
cd ~/suiron_raspberrypi/newversion/rpiHAT
sudo python setup.py install
```

Install Suiron
```
cd ~/suiron_raspberrypi/newversion/suiron_raspberrypi
sudo python setup.py install
```

Copy settings.json
```
cp ~/suiron_raspberrypi/newversion/settings.json ~/
```

Copy catkin_ws
```
cp -r ~/suiron_raspberrypi/newversion/catkin_ws  ~/catkin_ws
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```


In three seperated terminals Run ROSfile
```
rosrun  simp_motor Joydrive22Revision2.py
```

```
rosrun web_video_servo web_video_servo 
```


```
rostopic pub /joy sensor_msgs/Joy '{ header: {seq: 10, stamp: {secs: 143122243 nsecs: 345678}, frame_id: "3"}, axes: [1.0, 0.0, 0.0, 0.0, 0.0, 0.0], buttons: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}'
```
