# farm-notif
Notification Service for Chia Farm

[中文说明](README_zh_CN.md)

The notification service consists of two main parts: the local program and the server. The server has already been deployed on notif.xch.wiki, which you can directly use, or you can deploy your own server. Here is the usage documentation for the local client.

**About Block Rewards Notification:**

1. This program has two methods for detecting block rewards. When operating in solo mode, it is recommended to use `notif_reward`. When joining in a mining pool, use `notif_reward_pool`.
2. When joining a mining pool, ***do not*** enable the `notif_reward` option, as it will result in incorrect block reward notifications.

**Important Note**
> 1. This program is free and open source. Please configure it according to this documentation. **Do not** run any pre-compiled versions from other individuals, as it may pose risks of coin theft or mnemonic phrase theft.
> 2. Under no circumstances should any files within the "ssl" folder be disclosed to anyone, as the consequences are the same as mentioned above👆. 
> 3. Disclaimer: I do not assume any responsibility for any consequences resulting from the use of this program.

# Instructions

## 1. Install Python

Installation methods are omitted.

> If you're using Windows, remember to add the environment variable during installation for easier operations later: check `Add install dir to PATH`.

## 2. Download chia-farm-notif

``` bash
git clone git@github.com:nongyehezuoshe/chia-farm-notif.git
```

Alternatively, you can visit https://github.com/nongyehezuoshe/chia-farm-notif, download the compressed package directly, and then extract it locally.

## 3. Install Dependencies

Install Python dependencies:

``` bash
pip install websockets requests uuid pySMART
```

Install system dependencies:

``` bash
sudo apt install smartmontools
```

For Windows systems, please visit https://www.smartmontools.org/wiki/Download#InstalltheWindowspackage to download and install.

> For Windows installation, make sure to check (default checked) `Add install dir to PATH`

## 4. Modify Configuration File

Navigate to the `chia-farm-notif/config directory`, copy the `options_en_sample.json` file and rename it to `options.json`, then edit it:

```bash
cd chia-farm-notif/client/config
sudo cp options_zh_CN_sample.json options.json
sudo vi options.json
```
> Windows users can open it with any text editor to make modifications.

Below are explanations for each option in the configuration file (brief explanations are already provided in the file). Make the necessary modifications (modify the value field) based on your specific situation.

`chia_server`: The address of the Chia service, usually no need to modify.

`chia_ssl`: The path to the SSL certificate folder. The folder path is usually in the current user directory. For Ubuntu systems, if the current user is `root`, it would be `/root/.chia/mainnet/config/ssl`, while regular users may find it at `/home/<username>/.chia/mainnet/config/ssl`. For Windows users, it is generally located at `C:\Users\<username>\.chia\mainnet\config\ssl`.

> Note: Please replace `<username>` with your own username. In Linux paths, use `/` as the slash, while in Windows paths, use `\`. Please pay attention to this distinction, which will not be further explained.

`lang`: Language. `en` for English, `zh_CN` for Simplified Chinese.

`url_wechat`: The URL of the WeChat push service. Here, it is recommended to use the service at https://xz.qqoq.net. Follow the instructions on the website, scan the QR code to subscribe, then go to the webpage backend's `"Single Push" > "Push Information" > "Interface"`, and copy the URL from there.

`url_serve`:  The URL for server-side push, which refers to the server of this program. If you are using the server deployed by the author, keep it as https://notif.xch.wiki without modifications. Otherwise, enter the URL of your own deployed server.

`name`: Customized name for each machine to distinguish them.

`enable_wechat`: Enable WeChat push. If not needed, change it to `false`.  

`enable_email`: Enable email push. If not needed, change it to `false`. Email push relies on the server. The relevant information will be sent to the server, which will handle the email sending.

`email`: The receiving email address for email push. 

`notif_try`: Sending a test notification when the program starts. If not needed, change it to `false`.

`notif_reward`: Enable block reward notification (only applicable in solo mode, incorrect block reward notifications may be sent in non-solo mode). If not needed, change it to `false`.

`notif_reward_pool`: Enable block reward notification (effective for both solo and joining mining pools, but with low real-time accuracy, data refreshed every 1 hour). If not needed, change it to `false`.

`notif_reward_pool_xch`: The XCH address where the 1.75 (7/8) reward will send to. If `notif_reward_pool` was set to `true`, should give the right xch address.

`notif_reward_pool_interval`: The `notif_reward_pool` option determines the interval for checking block rewards in minutes.

`notif_point`: Enable plotting point notifications. If not needed, change it to `false`.

`notif_point_interval`:  If the sieved points passed in the current hour decrease by this percentage compared to the previous hour, a notification will be pushed. The default value of `0.2` means a 20% decrease in plotting point will trigger the notification. 

`notif_offline`:  Enable offline notifications. If not needed, change it to `false`. This notification relies on the server. 

`notif_offline_interval`: Interval for offline detection, in minutes. If not needed, change it to `false`. The minimum interval required is 30 minutes.

`notif_sync`: Enable full node synchronization anomaly notifications. If not needed, change it to `false`.

`notif_sync_interval`: Interval for rechecking full node synchronization anomaly, in minutes.

`notif_temperature`: Enable disk temperature anomaly notifications. If not needed, change it to `false`.

`notif_temperature_interval`:  Interval for checking disk temperature, in minutes. 

`notif_temperature_temp`: Threshold temperature for disk temperature anomaly notifications, in °C.

`temperature_exclusion_ssd`: Not detecting the temperature of ssd-type hard drives.  

`temperature_content`: Include disk temperature information in all notifications. If not needed, change it to `false`. When this option is enabled, disk temperature information will be attached after each notification.

## 5. Start Running

> Since obtaining the hard drive temperature relies on the third-party software "smartmontools," it may be necessary to run this software with administrator privileges in order to obtain the hard drive temperature. Otherwise, it may not be possible to retrieve the temperature information.

Go back to the `chia-farm-notif/client folder`, then run `notif.py`:

For Linux, if it's a server system, it is recommended to use `screen` to keep the program running continuously:

```bash
screen -R notif
```

For desktop systems, simply run:

```bash
cd ..
./notif.py
```

For Windows:

```bash
cd ..
python notif.py
```

Once the program is running, it will send a prompt message. Please check and confirm.

# Development Support

1、Submit bugs.

2、Share your requirements.

3、If this program has been helpful to you, donations are welcome.
`xch19arzhau6gjs6lamn6qzy8ene9kt2sdvtkxfujeac34ycjte4l64qse8rg6`

