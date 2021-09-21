# Look Out Your Windows

Create a __Time-varying__ Wallpaper for your Windows/UNIX device!

<img src="https://user-images.githubusercontent.com/70506921/131011772-1ee3ad3b-4ad4-4b2f-86ca-469234616f3a.jpg" width="350" height="200" margin="5"/> <img src="https://user-images.githubusercontent.com/70506921/131011762-b4a5e378-464b-44b9-8308-a1e94d3069c8.jpg" width="350" height="200"/>
<img src="https://user-images.githubusercontent.com/70506921/131011769-3f1e986a-9c9c-4523-97e9-f18bd4ac5127.jpg" width="350" height="200" margin="5"/> <img src="https://user-images.githubusercontent.com/70506921/131011776-686a98b6-dd65-47f6-b16a-36012450b847.jpg" width="350" height="200"/>

## Installation

### Method 1.
- Download zip file from release.

### Method 2.
- Clone this repository.

- Install the requirements.
```
pip install -r requirements.txt
```

- Make exe file using Pyinstaller.   
###### For Windows
```
pyinstaller --windowed ^
            --name=LookOutYourWindows ^
            --icon=.\icon.ico ^
            --paths=c:\Users\user\Desktop\HiDT\Look-Out-Your-Windows\venv\Lib\site-packages ^
            --add-binary "icon.ico;." ^
            --add-binary "images/styles/morning.jpg;images/styles" ^
            --add-binary "images/styles/afternoon.jpg;images/styles" ^
            --add-binary "images/styles/evening.jpg;images/styles" ^
            --add-binary "images/styles/night.jpg;images/styles" ^
            --add-data "GUI/MainGui.ui;GUI" ^
            --add-data "GUI/SaveGui.ui;GUI" ^
            --add-data "configs/daytime.yaml;configs" ^
            --add-data "trained_models/enhancer/enhancer.pth;trained_models/enhancer" ^
            --add-data "trained_models/generator/daytime.pt;trained_models/generator" ^
            WindowsGui.py
```

## Getting Started
1. Excute "LookOutYourWindows.exe".


2. Press the 'Browse' button and select an image.


3. Press the 'Start' button and select save folder. If you want to save the image and folder, press a checkbox.


4. If you want to use GPU, press a 'GPU' checkbox. (If your GPU is unavailable, the checkbox is not enabled.)


5. Press  the 'OK' button to create images.


6. If there exist a previously created images in the save folder, skip the create process.


7. Before pressing the 'Stop' or 'Exit' button, the process automatically changes the desktop wallpaper in the correct time.
    

8. If you press the 'X' button in the upper right corner, it will be executed in the system tray.

&nbsp;  &nbsp;  &nbsp;  &nbsp;  &nbsp;  &nbsp;  &nbsp;  &nbsp; &nbsp; <img src="https://user-images.githubusercontent.com/70506921/131242206-f334f748-dd30-409b-8966-860e20551d24.png">


> ### FYI)

- Choose your preferred fit for the image.

&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <img src="https://user-images.githubusercontent.com/70506921/131244213-e049dd7a-25c6-4b8e-9404-e8e16a76197f.gif">


- Time slots : 07:00 ~ 13:00, 13:00 ~ 18:00, 18:00 ~ 21:00, 21:00 ~ 07:00

## Caveats
- It may be treated as malware in Windows 10, but this software is **NEVER** a malware. (Trying to solve this problem)

- Creating images with CPU requries high CPU utilization and memory resources, so take your time when creating the initial images. (This is only for generating images, once the images are generated, it doesn't require much CPU/RAM resources!)

- You can use GPU to create images faster, but it still requires a lot of GPU memories.

## Rooms for improvement
- Use the server GPU to create the image instead of the local GPU.

- Select the resolution of the generated images.

- Make candidate images to pick the favorite one.

- Use more images to separate time slots in detail. 

## Citation
- High-Resolution Daytime Translation Without Domain Labels
    - Authors: Anokhin, Ivan and Solovev, Pavel and Korzhenkov, Denis and Kharlamov, Alexey and Khakhulin,
            Taras and Silvestrov, Alexey and Nikolenko, Sergey and Lempitsky, Victor and Sterkin, Gleb
    - https://github.com/saic-mdal/HiDT

- Icon
    - made by https://www.freepik.com from https://www.flaticon.com/
