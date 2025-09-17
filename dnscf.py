import requests
import traceback
import time
import os
import json

# API 密钥
CF_API_TOKEN    =   os.environ["CF_API_TOKEN"]
CF_ZONE_ID      =   os.environ["CF_ZONE_ID"]
CF_DNS_NAME     =   os.environ["CF_DNS_NAME"]
PUSHDEER_KEY    =   os.environ["PUSHDEER_KEY"]

headers = {
    'Authorization': f'Bearer {CF_API_TOKEN}',
    'Content-Type': 'application/json'
}

def get_cf_speed_test_ip(timeout=10, max_retries=5):
    for attempt in range(max_retries):
        try:
            # 发送 GET 请求，设置超时
            response = requests.get('https://ip.164746.xyz/ipTop.html', timeout=timeout)
            # 检查响应状态码
            if response.status_code == 200:
                return response.text
        except Exception as e:
            traceback.print_exc()
            print(f"get_cf_speed_test_ip Request failed (attempt {attempt + 1}/{max_retries}): {e}")
    # 如果所有尝试都失败，返回 None 或者抛出异常，根据需要进行处理
    return None

# 获取 DNS 记录
def get_dns_records(name):
    def_info = []
    url = f'https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        records = response.json()['result']
        for record in records:
            if record['name'] == name:
                def_info.append(record['id'])
        return def_info
    else:
        print('Error fetching DNS records:', response.text)

# 更新 DNS 记录
def update_dns_record(record_id, name, cf_ip):
    url = f'https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records/{record_id}'
    data = {
        'type': 'A',
        'name': name,
        'content': cf_ip
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"cf_dns_change success: ---- Time: " + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- ip：" + str(cf_ip))
        return "ip:" + str(cf_ip) + "解析" + str(name) + "成功"
    else:
        traceback.print_exc()
        print(f"cf_dns_change ERROR: ---- Time: " + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- MESSAGE: " + str(response))
        return "ip:" + str(cf_ip) + "解析" + str(name) + "失败"

# 消息推送
def push_deer(text, desp='', type_='text'):
    try:
        url = "https://api2.pushdeer.com/message/push"
        data = {
            'text': text,
            'desp': desp,
            'type': type_,
            'pushkey': PUSHDEER_KEY
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url, data=data, headers=headers, timeout=10)
        if response.ok:
            print("PushDeer 推送成功:", response.text)
        else:
            print("PushDeer 推送失败:", response.status_code, response.text)
    except Exception as e:
        traceback.print_exc()
        print("PushDeer 推送异常:", e)

# 主函数
def main():
    ip_addresses_str = get_cf_speed_test_ip()
    if not ip_addresses_str:
        print("未能获取优选IP，退出。")
        return

    # 取第一个 IP
    ip_addresses = [ip.strip() for ip in ip_addresses_str.split(',') if ip.strip()]
    if not ip_addresses:
        print("解析到的 IP 列表为空，退出。")
        return

    best_ip = ip_addresses[0]  # 只用第一个 IP
    print(f"选择优选IP: {best_ip}")

    dns_records = get_dns_records(CF_DNS_NAME)
    if not dns_records:
        print(f"未找到 {CF_DNS_NAME} 的 DNS 记录")
        return

    # 更新第一个记录
    record_id = dns_records[0]
    res = update_dns_record(record_id, CF_DNS_NAME, best_ip)

    print(res)
    push_deer("IP优选DNSCF推送", desp=res)

if __name__ == '__main__':
    main()
