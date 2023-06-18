# chia-farm-notif
Chia农场的通知服务

整个通知服务分为两大部分：本地程序和服务端。本人已经将服务端部署在notif.xch.wiki，你可以直接使用，当然你也可以部署自己的服务端。以下是本地客户端的使用文档。

**关于爆块通知**

> 1、本程序有两种检测爆块的方式。当solo时，推荐使用`notif_reward`；加入矿池时，使用`notif_reward_pool`。  
	2、加入矿池时***不能***开启`notif_reward`选项，否则会错误推送爆块通知。

**特别注意**

> 1、本程序免费且开源，请根据本文档自行进行配置。一定**不要**运行其他任何人编译好的版本，否则可能存在被盗币、被盗助记词的风险。  
	2、千万不能将ssl文件夹内的任何文件泄露给任何人，否则后果同上👆。  
	3、免责申明：使用本程序造成的任何后果，本人不承担任何责任！  

# 使用说明

## 1、安装python

安装方法略。

> 如果是Windows系统，记得安装时添加环境变量，以便后期方便操作：勾选 `Add python.exe to PATH`。

## 2、下载chia-farm-notif

``` bash
git clone git@github.com:nongyehezuoshe/chia-farm-notif.git
```
当然，也可以访问https://github.com/nongyehezuoshe/chia-farm-notif 直接下载压缩包后解压到本地。

## 3、安装依赖包

安装python依赖包：

``` bash
pip install websockets requests uuid pySMART
```

安装系统依赖包：

``` bash
sudo apt install smartmontools
```

Windows系统请访问https://www.smartmontools.org/wiki/Download#InstalltheWindowspackage 下载并安装。

> windows系统安装时务必勾选(默认勾选) `Add install dir to PATH`

## 4、修改配置文件

切换到`chia-farm-notif/config`目录，复制其中的`options_zh_CN_sample.json`文件并重命名为`options.json`，然后进行编辑：

```bash
cd chia-farm-notif/client/config
sudo cp options_zh_CN_sample.json options.json
sudo vi options.json
```

> Windows用户使用任意文本编辑器打开做修改即可。

下面对配置文件中的各个选项做解释（其实配置文件里面已经做了简要说明），根据自身情况做相应的修改（修改value字段）。

`chia_server`: chia服务的地址，默认即可，一般不做修改。  

`chia_ssl`: ssl证书文件夹的路径。该文件夹的路径一般在当前用户目录下，Ubuntu系统当前用户为`root`的话，则为：`/root/.chia/mainnet/config/ssl`，普通用户可能在：`/home/<username>/.chia/mainnet/config/ssl`。Windows用户一般在：`C:\\Users\\<username>\\.chia\\mainnet\\config\\ssl`。  

> 注意：请将`<username>`替换为你自己的用户名；Linux系统路径中的斜杠使用`/`，而Windows则使用的时`\`，且需要使用`\`转义，请注意区分，后面不再做说明。  

`lang`: 语言。`en`表示英文，`zh_CN`表示简体中文。    

`url_wechat`: 微信推送服务的网址。这里推荐使用https://xz.qqoq.net 的服务。根据网站的提示，微信扫码关注后进入网页后台的`单点推送》推送信息》接口`，复制这里的网址。  

`url_serve`: 通过服务器端推送的网址。也就是本程序的服务端，如果使用本人部署的服务则保留`https://notif.xch.wiki`不做修改，否则填入自己部署服务的网址。  

`name`: 为每一台机子自定义一个名称，以便于区分。  

`enable_wechat`: 开启微信推送。如不需要则修改为`false`。  

`enable_email`: 开启邮件推送。如不需要则修改为`false`，邮件推送依赖服务端，相关信息将发送到服务端后，由服务端完成发送邮件。 

`email`: 邮件推送的接收邮箱。  

`notif_try`: 程序启动时推送测试通知。如不需要则修改为`false`。  

`notif_reward`: 开启爆块通知（仅solo时有效，非solo时会错误推送爆块通知）。如不需要则修改为`false`。  

`notif_reward_pool`: 启用爆块通知（solo和加入矿池都有效，但是时效性较低，每隔1小时刷新一次数据）。如不需要则修改为`false`。  

`notif_reward_pool_xch`: 1.75奖励所在的XCH地址。 如果`notif_reward_pool`设置为`true`，则此项需填写正确的XCH地址。  

`notif_reward_pool_interval`: `notif_reward_pool`选项检测爆块的间隔时长，单位：分钟。  

`notif_point`: 开启掉算力通知。如不需要则修改为`false`。  

`notif_point_interval`: 如果当前一个小时通过的初筛值比上一个小时低了这个比例则推送通知。默认的`0.2`表示算力降低20%则推送通知。  

`notif_offline`: 开启掉线通知。如不需要则修改为`false`，该通知依赖服务端。  

`notif_offline_interval`: 掉线检测的间隔时长，单位：分钟。如不需要则修改为`false`；要求最小间隔时长为30分钟。  

`notif_sync`: 开启全节点同步异常通知。如不需要则修改为`false`。  

`notif_sync_interval`: 全节点同步异常再次检测间隔时长，单位：分钟。  

`notif_temperature`: 开启硬盘温度异常通知。如不需要则修改为`false`。  

`notif_temperature_interval`: 硬盘温度检查间隔时长，单位：分钟。  

`notif_temperature_temp`: 硬盘温度异常通知的阈值，单位：°C。  

`temperature_exclusion_ssd`: 不检测固态硬盘温度。  

`temperature_content`: 在所有通知后附带硬盘温度信息。如不需要则修改为`false`，开启该选项后，将在推送的每一条信息后面附带硬盘温度信息。

## 5、开始运行

> 由于获取硬盘温度依赖第三方软件`smartmontools`，因此可能需要管理员权限来启动本软件，否则可能无法获取硬盘温度。

回到`chia-farm-notif/client`文件夹，然后运行其中的`notif.py`：  
对于Linux，如果是服务器系统，推荐使用screen来保持程序一直运行：
```bash
screen -R notif
```

桌面系统则直接运行:

```bash
cd ..
./notif.py
```

Windows:

```bash
cd ..
python notif.py
```

程序运行后将发送一条提示信息，请检查确认。

# 支持开发

1、提交bug。

2、请提出你的需求。

3、如果本程序对你有所帮助，欢迎捐赠。  
`xch19arzhau6gjs6lamn6qzy8ene9kt2sdvtkxfujeac34ycjte4l64qse8rg6`
