## Requirements

* Raspberry Pi Zero W
* [Waveshare 1.44 ST7735S LCD HAT](https://www.waveshare.com/wiki/1.44inch_LCD_HAT)

### Setup

* Enable SPI in `Interfacting Options > SPI` in `raspi-config`

```bash
$ sudo raspi-config
```

* Add the following lines to `/etc/modules`
```bash
# /etc/modules
spi-bcm2835
fbtft_device
```

* Add the following lines to `/etc/modprobe.d/fbtft.conf`
```bash
# /etc/modprobe.d/fbtft.conf
options fbtft_device name=adafruit18_green gpios=reset:27,dc:25,cs:8,led:24 speed=40000000 bgr=1 fps=60 custom=1 height=128 width=128 rotate=90
```

* Add the following lines to `/boot/config.txt`
```bash
# /boot/config.txt
dtoverlay=pwm-2chan,pin=18,func=2,pin2=13,func2=4
hdmi_force_hotplug=1
hdmi_cvt=128 128 60 1 0 0 0
hdmi_group=2
hdmi_mode=1
hdmi_mode=87
display_rotate=1
```

* Synchroneous copy between `fb0` and `fb1`  
If you want to display console on the screen you will need to use `fbcp`:

```bash
$ sudo apt install git cmake
$ git clone https://github.com/tasanakorn/rpi-fbcp
$ mkdir rpi-fbcp/build
$ cd rpi-fbcp/build/
$ cmake .. && make
$ sudo install fbcp /usr/local/bin/fbcp
```

* Launch `fbcp` automatically at startup  
Add the following lines to `/etc/rc.local` before `exit 0`:
```bash
fbcp&
```

## Software

### Requirements

* Python >= 3.8

```bash
$ sudo apt install python3-pygame python3-gpiozero libsdl2-dev libsdl2-ttf-dev
```

### Usage
You need root access to modify the framebuffer!

```bash
$ sudo python3 main.py
```

Add this to `/etc/rc.local` to run Pixette at startup:
```bash
$ cd /home/pi/stella
$ sudo python3 main.py &
```
