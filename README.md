# Look Out Your Windows

Generate Daytime Translated Images and Change Desktop Wallpaper Over Time.

![Test2_to_afternoon](https://user-images.githubusercontent.com/70506921/131011762-b4a5e378-464b-44b9-8308-a1e94d3069c8.jpg)
![Test2_to_evening](https://user-images.githubusercontent.com/70506921/131011769-3f1e986a-9c9c-4523-97e9-f18bd4ac5127.jpg)
![Test2_to_morning](https://user-images.githubusercontent.com/70506921/131011772-1ee3ad3b-4ad4-4b2f-86ca-469234616f3a.jpg)
![Test2_to_night](https://user-images.githubusercontent.com/70506921/131011776-686a98b6-dd65-47f6-b16a-36012450b847.jpg)

## Installation
**Method 1.**
- Download zip file from release.

**Method 2.**
- Clone this repository.

- Install the requirements.
```
pip install -r requirements.txt
```

- Make exe file using Pyinstaller.
```
pyinstaller --windowed ^
            --name=LookOutYourWindows ^
            --icon=.\icon.ico ^
            --paths=c:\Users\user\Desktop\HiDT\Look-Out-Your-Windows\venv\Lib\site-packages ^
            --add-binary "icon.ico;." ^
            --add-binary "images/styles/morning.jpg;image/styles" ^
            --add-binary "images/styles/afternoon.jpg;image/styles" ^
            --add-binary "images/styles/evening.jpg;image/styles" ^
            --add-binary "images/styles/night.jpg;image/styles" ^
            --add-data "GUI/MainGui.ui;GUI" ^
            --add-data "GUI/SaveGui.ui;GUI" ^
            --add-data "configs/daytime.yaml;config" ^
            --add-data "trained_models/enhancer/enhancer.pth;trained_models/enhancer" ^
            --add-data "trained_models/generator/daytime.pt;trained_models/generator" ^
            WindowsGui.py
```

## Getting Started
1. Excute "LookOutYourWindows.exe".


2. Press 'Browse' button and select an image.


3. Press 'Start' button and select save folder. If you want to save the image and folder, press a checkbox.


4. Press 'OK' button to create images.


5. If there exist previously created images in the save folder, skip the create process.


6. Until pressing 'Stop' or 'Exit' button, it changes the desktop wallpaper over time.
    

- Time slots : 07:00 ~ 13:00, 13:00 ~ 18:00, 18:00 ~ 21:00, 21:00 ~ 07:00

## Caveats
- It may be treated as malware in Windows 10, but it is **NEVER** a malware. (Trying to solve this problem)

- Creating images by CPU needs high CPU utilization, so it could be stuck or spend a long time.

- If you save the image and folder path, "LookOutYourWindows_SavePath.txt" is created in "c:/Users/user".

## Rooms for improvement
- Make higher resolution images.

- Use GPU to create images if possible.

- Make candidate images to pick the favorite one.

- Use more images to separate time slots in detail. 

### Citation
- High-Resolution Daytime Translation Without Domain Labels
    - Authors: Anokhin, Ivan and Solovev, Pavel and Korzhenkov, Denis and Kharlamov, Alexey and Khakhulin,
            Taras and Silvestrov, Alexey and Nikolenko, Sergey and Lempitsky, Victor and Sterkin, Gleb
    - https://github.com/saic-mdal/HiDT

- Icon
    - made by https://www.freepik.com from https://www.flaticon.com/