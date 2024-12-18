import requests
import traceback
import time
import os
import json
from pypushdeer import PushDeer

# API 密钥
CF_API_TOKEN    =   'aZf_02DhPAHwbKHJWCW16jUXikHKI76oWgnWcN0S'
CF_ZONE_ID      =   '00342baa2f44ab70a94d90207726e261'
CF_DNS_NAME     =   'dsn.steady298.cash'

# pushplus_token
PUSHDEER_TOKEN  =   'PDU17847TrbmhGQOx7kIJoyGBL74vS825SEYGjiDT'



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
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            records = response.json()['result']
            for record in records:
                if record['name'] == name:
                    def_info.append(record['id'])
            if not def_info:
                print(f'未找到名为 {name} 的DNS记录')
            return def_info
        else:
            print('获取DNS记录失败:', response.text)
            return None
    except Exception as e:
        print(f'获取DNS记录时发生错误: {str(e)}')
        return None

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
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- MESSAGE: " + str(response.text))
        return "ip:" + str(cf_ip) + "解析" + str(name) + "失败"

# 消息推送
def push_deer(content):
    pushdeer = PushDeer(pushkey=PUSHDEER_TOKEN)
    pushdeer.send_markdown("# IP优选DNSCF推送", desp=content)

    



# 主函数
def main():
    # 获取最新优选IP
    ip_addresses_str = get_cf_speed_test_ip()
    if not ip_addresses_str:
        print("未能获取到IP地址")
        return
        
    ip_addresses = ip_addresses_str.split(',')
    dns_records = get_dns_records(CF_DNS_NAME)
    
    # 检查是否成功获取DNS记录
    if not dns_records:
        print(f"未找到 {CF_DNS_NAME} 的DNS记录，请检查配置")
        return
        
    push_plus_content = []
    
    # 确保只处理与 DNS 记录数量相同的 IP 地址
    for index, ip_address in enumerate(ip_addresses[:len(dns_records)]):
        try:
            dns = update_dns_record(dns_records[index], CF_DNS_NAME, ip_address)
            push_plus_content.append(dns)
        except Exception as e:
            error_msg = f"更新DNS记录失败: {str(e)}"
            print(error_msg)
            push_plus_content.append(error_msg)

    if push_plus_content:
        push_deer('\n'.join(push_plus_content))

if __name__ == '__main__':
    main()
