#! /usr/bin/env python3
import asyncio
import ssl
import websockets,requests
import os,json,uuid,datetime,time,sys
import lib.chiahzs as chiahzs
import pySMART

lang={}
maindata={
    "id":str(uuid.uuid4()).replace("-",""),
    "passed_filter":0,
    "passed_filter_last_hour":0,
    "passed_filter_current_hour":0,
    "passed_filter_min":0,
    "time_start":time.time(),
    "time_start_hour":time.time(),
    "time_heartbeat":time.time(),
    "time_sync":None,
    "server_ok":None,
    "rewards_amount":None
}

def tool_lang(text):
    return lang[text][chiahzs.opt_get("lang")]

def notification(data):
    if chiahzs.opt_get("enable_wechat"):
        notif_wechat(data)
    if chiahzs.opt_get("enable_email"):
        notif_mail(data)

def notif_wechat(data):
    url_wechat = chiahzs.opt_get("url_wechat")
    headers = {'Content-Type': 'application/json'}
    new_data={
        "title":data["title"],
        "content":data["content"]
    }
    if chiahzs.opt_get("temperature_content") and tool_lang("title_temperature") not in new_data["title"]:
        new_data=temperature_content(new_data)

    flag=0
    while True:
        try:
            if flag>5:
                print("notif_wechat_err")
                break
            else:
                flag+=1
            response = requests.post(url_wechat, data=json.dumps(new_data), headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print('error:', e)
            time.sleep(10)
        else:
            if response.status_code==200:
                print("wechat notif response:", response.json())
                break
            else:
                print("notif_wechat_err")
                time.sleep(10)

def notif_mail(data):
    url_serve=chiahzs.opt_get("url_serve")
    headers = {'Content-Type': 'application/json'}
    new_data = {
        "type":"email",
        "title": data["title"], 
        "content": data["content"],
        "email":chiahzs.opt_get("email")
    }
    if chiahzs.opt_get("temperature_content") and not new_data["title"]==tool_lang("title_temperature"):
        new_data=temperature_content(new_data)

    flag=0
    while True:
        try:
            if flag>5:
                print("notif_mail_err")
                break
            else:
                flag+=1
            response = requests.post(url_serve, data=json.dumps(new_data), headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print('error:', e)
            print(tool_lang("err_serve"))
            time.sleep(10)
        else:
            if response.status_code==200 and response.json()["success"]:
                print("notif_mail_response:", response.json())
                break
            else:
                print("notif_mail_err")
                time.sleep(10)

def show_filter(message):
    if message["data"]["farming_info"]["passed_filter"]>0:
        maindata["passed_filter_current_hour"]+=message["data"]["farming_info"]["passed_filter"]
        maindata["passed_filter"]+=message["data"]["farming_info"]["passed_filter"]
        maindata["passed_filter_min"]=maindata["passed_filter"]/((time.time()-maindata["time_start"])/60)
        
        result = ''.join((tool_lang("filter_min"), str(maindata["passed_filter_min"]), "; ",tool_lang("filter_lasthour"), str(maindata["passed_filter_last_hour"]), "; ",tool_lang("filter_currenthour"), str(maindata["passed_filter_current_hour"])))

        chiahzs.log_show(str(sys._getframe().f_lineno)+" "+tool_lang("filter"),result)

def notif_reward(message):
    info=message["data"]["farming_info"]
    if chiahzs.opt_get("notif_reward") and info["proofs"]>0:
        date_string = datetime.datetime.fromtimestamp(info["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
        data = {
            "type":"reward",
            "title": chiahzs.opt_get("name")+": "+tool_lang("title_farmd"), 
            "content": tool_lang("content_reward")+" @ "+date_string+" !  \n"+tool_lang("content_filter_1")+str(maindata["passed_filter_min"])+"  \n"+tool_lang("content_filter_2")+str(maindata["passed_filter_current_hour"])+"  \n"+tool_lang("content_filter_3")+str(maindata["passed_filter_last_hour"])+"  \n"+tool_lang("content_filter_4")+"  \n"+json.dumps(info, indent=4)
        }
        print("notif_reward:",data)
        notification(data)

def notif_point(message):
    info=message["data"] if message["data"].get("farming_info") is None else message["data"].get("farming_info")
    if (time.time()-maindata["time_start_hour"])/60/60>1:
        if chiahzs.opt_get("notif_point") and maindata["passed_filter_last_hour"]>0 and (maindata["passed_filter_last_hour"]-maindata["passed_filter_current_hour"])/maindata["passed_filter_last_hour"]>0.2:
            data = {
                'type':'point',
                'title': chiahzs.opt_get("name")+": "+tool_lang("title_point"), 
                "content": tool_lang("content_point")+"  \n"+tool_lang("content_filter_1")+str(maindata["passed_filter_min"])+"  \n"+tool_lang("content_filter_2")+str(maindata["passed_filter_current_hour"])+"  \n"+tool_lang("content_filter_3")+str(maindata["passed_filter_last_hour"])+"  \n"+tool_lang("content_filter_4")+"  \n"+json.dumps(info, indent=4)
            }
            print("notif_point",data)
            notification(data)

        maindata["passed_filter_last_hour"]=maindata["passed_filter_current_hour"]
        maindata["passed_filter_current_hour"]=0
        maindata["time_start_hour"]=time.time()

def notif_sync(message):
    info = message["data"]["blockchain_state"]
    synced = info["sync"]["synced"]

    if not synced:
        print('{0} blockchain_state : {1}'.format(datetime.datetime.now(),info))

        if maindata.get("time_sync") is None or (time.time() - maindata["time_sync"]) / 60 > chiahzs.opt_get("notif_sync_interval"):
            maindata["time_sync"] = None
            data = {
                "type": "sync",
                "title": chiahzs.opt_get("name") + ": " + tool_lang("title_sync"),
                "content": tool_lang("content_sync") + "  \n" + json.dumps(info, indent=4)
            }
            print("notif_sync:", data)
            notification(data)
            maindata["time_sync"] = time.time()
    else:
        if maindata.get("time_sync") is not None:
            maindata["time_sync"] = None
            data = {
                "type": "sync",
                "title": chiahzs.opt_get("name") + ": " + tool_lang("title_sync_ok"),
                "content": tool_lang("title_sync_ok") + "  \n" + json.dumps(info, indent=4)
            }
            print("notif_sync:", data)
            notification(data)
        else:
            maindata["time_sync"] = None

def get_disk_temperature():
    try:
        disks = pySMART.DeviceList()
        temperatures = {}
        for disk in disks.devices:
            temperature = disk.temperature
            temperatures[disk] = temperature
        return temperatures
    except Exception as e:
        print("Failed to retrieve disk temperatures:", str(e))
        return None

def temperature_content(data):
    flag_temp=False
    disk_temperatures = get_disk_temperature()
    data["content"]+="  \n"+tool_lang("content_temperature_cotent")
    if disk_temperatures is not None:
        for disk, temperature in disk_temperatures.items():
            if disk.is_ssd and chiahzs.opt_get("temperature_exclusion_ssd"):
                continue
            data["content"]+=f"  \n{disk.name} ({disk.model}) {tool_lang('content_temperature_temp')} {str(temperature)} ℃"
    return data

async def notif_try():
    if chiahzs.opt_get("notif_try")==False:
        return
    data = {
        'title': chiahzs.opt_get("name")+": "+tool_lang("title_try"), 
        "content": tool_lang("content_try")
    }
    notification(data)

async def notif_temperature():
    if not chiahzs.opt_get("notif_temperature"):
        return False

    def temperature():
        flag_temp=False
        disk_temperatures = get_disk_temperature()
        data = {
            'title': chiahzs.opt_get("name")+": "+tool_lang("title_temperature"), 
            "content": tool_lang("content_temperature")
        }
        if disk_temperatures is not None:
            for disk, temperature in disk_temperatures.items():
                if disk.is_ssd and chiahzs.opt_get("temperature_exclusion_ssd"):
                    continue
                if temperature >= chiahzs.opt_get("notif_temperature_temp"):
                    flag_temp=True
                    data["content"]+=f"  \n{disk.name} ({disk.model}) {tool_lang('content_temperature_temp')} {str(temperature)} ℃"
        if flag_temp:
            print("temperature",data)
            notification(data)
  
    while True:
        temperature()
        await asyncio.sleep(chiahzs.opt_get("notif_temperature_interval")*60)
    return False

async def connect():
    while True:
        if not (chiahzs.opt_get("notif_reward") or chiahzs.opt_get("notif_point") or chiahzs.opt_get("notif_sync")):
            return

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.load_cert_chain(os.path.join(chiahzs.opt_get("chia_ssl"),"wallet","private_wallet.crt"), os.path.join(chiahzs.opt_get("chia_ssl"),"wallet","private_wallet.key"))

        url = chiahzs.opt_get("chia_server")
        sendMesasge = {"destination": "daemon", "command": "register_service", "request_id": maindata["id"], "origin": "", "data": {"service": 'wallet_ui'}}

        timeout = 5  # 超时时长（秒）

        try:
            # 创建一个协程用于建立连接
            connect_coroutine = websockets.connect(url, ssl=ssl_context)

            # 使用asyncio.wait_for函数设置超时时长
            websocket = await asyncio.wait_for(connect_coroutine, timeout=timeout)

            print('{0}: Sent Message {1}'.format(datetime.datetime.now(), sendMesasge))
            await websocket.send(json.dumps(sendMesasge))
            while True:
                response = await websocket.recv()
                wsmsg = json.loads(response)

                if wsmsg.get("command") == "get_blockchain_state":
                    notif_sync(wsmsg)

                if wsmsg["command"] == "new_farming_info":
                    print('{0} farming_info : {1}'.format(datetime.datetime.now(), wsmsg["data"]["farming_info"]))
                    show_filter(wsmsg)
                    notif_point(wsmsg)
                    notif_reward(wsmsg)

            # 关闭连接
            # await websocket.close()

        except asyncio.TimeoutError:
            print("connect timeout")
            continue

        except websockets.WebSocketException as e:
            print(f"connect error: {e}")
            continue

async def notif_offline(type):
    if not chiahzs.opt_get("notif_offline"):
        return False
    url_serve=chiahzs.opt_get("url_serve")
    headers = {'Content-Type': 'application/json'}
    data = {
        "type":"offline",
        "subtype":type,
        "title": chiahzs.opt_get("name")+": "+tool_lang("title_offline"), 
        "content": tool_lang("content_offline_error") if type=="error" else tool_lang("content_offline"),
        "notif_offline_interval":chiahzs.opt_get("notif_offline_interval"),
        "id":maindata["id"],
        "enable_wechat":chiahzs.opt_get("enable_wechat"),
        "url_wechat":chiahzs.opt_get("url_wechat"),
        "enable_email":chiahzs.opt_get("enable_email"),
        "email":chiahzs.opt_get("email")
    }
    def push(data):
        def server_fail():
            if not maindata["server_ok"] and chiahzs.opt_get("enable_wechat") :
                data = {
                    "title": chiahzs.opt_get("name")+": "+tool_lang("title_server_fail"), 
                    "content": tool_lang("content_server_fail")
                }
                print("notif_offline:",data)
                maindata["server_ok"]=False
                notif_wechat(data)

        flag=0
        while True:
            try:
                if flag>5:
                    server_fail()
                    break
                else:
                    flag+=1
                response = requests.post(url_serve, data=json.dumps(data), headers=headers)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print('error:', e)
                print(tool_lang("err_serve"))
                time.sleep(10)
            else:
                if response.status_code==200 and response.json()["success"]:
                    print("offline_push_response:", response.json())
                    maindata["server_ok"]=True
                    break
                else:
                    # server_fail()
                    time.sleep(10)
                
    if type=="exit" or type=="error":
        push(data)
        return True

    while True:
        push(data)
        await asyncio.sleep(chiahzs.opt_get("notif_offline_interval")*60)

async def notif_reward_pool():
    print("notif_reward_pool")
    if not chiahzs.opt_get("notif_reward_pool"):
        return

    ts = chiahzs.opt_get("notif_reward_pool_interval") * 60
    xch_address = chiahzs.opt_get("notif_reward_pool_xch")

    def get_amount():
        url=f"https://api2.spacescan.io/1/xch/balance/{xch_address}"
        flag=0
        while True:
            try:
                if flag>5:
                    return None
                    break
                else:
                    flag+=1
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print('notif_reward_pool error:', e)
                time.sleep(10)
            else:
                if response.status_code==200 and response.json()["status"]=="Success":
                    return response.json()["data"]["received"]
                    break
                else:
                    # server_fail()
                    time.sleep(10)

    def get_rewards(num):
        url=f"https://api2.spacescan.io/1/xch/address/txns/{xch_address}?page=1&count=50"
        flag=0
        while True:
            try:
                if flag>5:
                    return None
                    break
                else:
                    flag+=1
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print('notif_reward_pool error:', e)
                time.sleep(10)
            else:
                if response.status_code==200 and response.json()["status"]=="Success":
                    rewards=[]
                    coins = response.json()["data"]["coins"]
                    num=int(min(num,len(coins)))
                    for i in range(0,num):
                        if coins[i]["coinbase"] :
                            rewards.append(coins[i])
                    return rewards
                    break
                else:
                    time.sleep(10)

    def rewards():
        amount= get_amount()
        print("amount:",amount)
        if maindata["rewards_amount"] is None:
            maindata["rewards_amount"] = amount
            return
        if amount > maindata["rewards_amount"] :
            rewards = get_rewards((amount-maindata["rewards_amount"])//1.75)
            print("rewards:",rewards)
            if rewards:
                data = {
                    "type":"reward",
                    "title": chiahzs.opt_get("name")+": "+tool_lang("title_farmd"), 
                    "content": tool_lang("content_reward")+":"
                }
                for coin in rewards:
                    data['content']=f"{data['content']}  \n{tool_lang('content_reward_time')}: {datetime.datetime.fromtimestamp(int(coin['timestamp'].strip())).strftime('%Y-%m-%d %H:%M:%S')}, {tool_lang('content_reward_height')}: {coin['confirmed_index']}"
                notification(data)
            maindata["rewards_amount"] = amount
        return

    while True:
        rewards()
        await asyncio.sleep(ts)

async def main():
    await asyncio.gather(connect(), notif_offline("heartbeat"), notif_temperature(), notif_try(), notif_reward_pool())

if __name__ == "__main__":
    # options=json.loads(open("config/options.json","rb").read())
    lang=json.loads(open("config/lang.json","rb").read())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Keyboard exit")
        asyncio.run(notif_offline("exit"))
    except Exception:
        print("err")
        print(Exception)
        asyncio.run(notif_offline("error"))