import requests
import json
import argparse
import urllib.parse

def get_blogger_id(blogger_name):
    url = "https://api.coze.cn/v1/workflow/run"
    headers = {
        "Authorization": "Bearer sat_GfT8DESG9et2OjhJrdWnNgl9ULTLpnacbYkf2cT909ZdH7RWYk5sol5rVufhQcTa",
        "Content-Type": "application/json"

    }
    payload = {
        "workflow_id": "7527683419154628646",
        "parameters": {
            "input": blogger_name
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()
        
        if result.get("code") == 0 and "data" in result:
            data_str = result["data"]
            # The 'data' field is a string containing a JSON object, so we need to parse it again
            data_json = json.loads(data_str)
            output_str = data_json.get("output")
            if output_str:
                return output_str
            else:
                print(f"Error: 'output' field not found in data: {data_json}")
                return None
        else:
            print(f"Error from API: {result.get('msg', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
        print(f"Response content: {response.text}")
        return None



def get_blogger_videos(blogger_id, query_count):
    url = "https://api.coze.cn/v1/workflow/run"
    headers = {
        "Authorization": "Bearer sat_GfT8DESG9et2OjhJrdWnNgl9ULTLpnacbYkf2cT909ZdH7RWYk5sol5rVufhQcTa",
        "Content-Type": "application/json"
    }
    all_video_data = []
    last_buffer = ""
    retrieved_count = 0

    print(f"\n正在获取博主ID为 {blogger_id} 的视频数据...")

    while retrieved_count < query_count:
        payload = {
            "workflow_id": "7527840720040853531",
            "parameters": {
                "username": blogger_id,
                "last_buffer": last_buffer
            }
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 0 and "data" in result:
                data_str = result["data"]
                data_json = json.loads(data_str)
                
                videos = data_json.get("output", [])
                all_video_data.extend(videos)
                retrieved_count += len(videos)

                new_last_buffer = data_json.get("last_buffer", "")
                continue_flag = data_json.get("continueFlag", 0)

                if continue_flag == 0 or not new_last_buffer:
                    print("已获取所有可用视频或达到查询数量。")
                    break
                last_buffer = new_last_buffer
            else:
                print(f"Error from video API: {result.get('msg', 'Unknown error')}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Video request failed: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"Failed to decode video JSON response: {e}")
            print(f"Response content: {response.text}")
            break
    
    # Return only up to query_count videos
    return all_video_data[:query_count]

def send_webhook_data(webhook_url, video_data, request_id):
    print(f"\n正在向webhook地址 {webhook_url} 回传视频数据...")
    success_count = 0
    total_count = len(video_data)
    
    for i, video in enumerate(video_data, 1):
        payload = {
            "request_id": request_id,
            "video_index": i,
            "total_videos": total_count,
            "data": video
        }
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            success_count += 1
            print(f"视频 {i}/{total_count} 回传成功")
        except requests.exceptions.RequestException as e:
            print(f"视频 {i}/{total_count} 回传失败: {e}")
    
    print(f"\n回传完成！成功: {success_count}/{total_count}")

def get_video_comments(object_id, object_nonce_id):
    url = "https://api.coze.cn/v1/workflow/run"
    headers = {
        "Authorization": "Bearer sat_GfT8DESG9et2OjhJrdWnNgl9ULTLpnacbYkf2cT909ZdH7RWYk5sol5rVufhQcTa", # 使用与视频数据相同的Token
        "Content-Type": "application/json"
    }
    payload = {
        "parameters": {
            "object_id": object_id,
            "object_nonce_id": object_nonce_id
        },
        "workflow_id": "7543527932590178319" # 评论数据接口的workflow_id
    }
    
    comments_list = []
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 0 and "data" in result:
            data_str = result["data"]
            data_json = json.loads(data_str)
            
            comments = data_json.get("output")
            if comments:
                for comment in comments:
                    content = comment.get("content", "")
                    create_time = comment.get("createtime", "")
                    like_count = comment.get("likeCount", 0)
                    
                    # 格式化评论数据
                    formatted_comment = {
                        "content": content,
                        "create_time": create_time,
                        "like_count": like_count
                    }
                    comments_list.append(formatted_comment)
        else:
            print(f"Error from comments API: {result.get('msg', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        print(f"Comments request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode comments JSON response: {e}")
        print(f"Response content: {response.text}")
    
    return comments_list

def get_tiktok_secuid(tiktok_url):
    """
    从TikTok主页链接获取secuid
    """
    encoded_url = urllib.parse.quote(tiktok_url, safe='')
    api_url = f"https://tiktok-api-miaomiaocompany-c35bd5a6.koyeb.app/api/tiktok/web/get_sec_user_id?url={encoded_url}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") == 200 and "data" in result:
            secuid = result["data"]
            print(f"获取到的secuid: {secuid}")
            return secuid
        else:
            print(f"获取secuid失败: {result}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"获取secuid请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"解析secuid响应失败: {e}")
        return None

def get_tiktok_user_posts(secuid, count, cursor=0):
    """
    使用secuid获取TikTok用户的视频信息
    支持分页获取，返回包含videos、cursor和hasMore的完整结构
    """
    api_url = "https://tiktok-api-miaomiaocompany-c35bd5a6.koyeb.app/api/tiktok/web/fetch_user_post"
    # 确保单次请求不超过30条
    request_count = min(count, 30)
    params = {
        "secUid": secuid,
        "cursor": cursor,
        "count": request_count,
        "coverFormat": 2
    }
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        result = response.json()
        
        print(f"TikTok API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 根据实际API响应结构解析数据
        if result.get("code") == 200 and "data" in result:
            data = result["data"]
            videos = data.get("itemList", [])
            next_cursor = data.get("cursor", "")
            has_more = data.get("hasMore", False)
            
            print(f"获取到 {len(videos)} 个TikTok视频，cursor: {next_cursor}, hasMore: {has_more}")
            
            return {
                "videos": videos,
                "cursor": next_cursor,
                "hasMore": has_more
            }
        else:
            print(f"获取TikTok用户视频失败: {result}")
            return {
                "videos": [],
                "cursor": "",
                "hasMore": False
            }
    except requests.exceptions.RequestException as e:
        print(f"获取TikTok用户视频请求失败: {e}")
        return {
            "videos": [],
            "cursor": "",
            "hasMore": False
        }
    except json.JSONDecodeError as e:
        print(f"解析TikTok用户视频响应失败: {e}")
        return {
            "videos": [],
            "cursor": "",
            "hasMore": False
        }

def main():
    parser = argparse.ArgumentParser(description='Fetch blogger data and send to webhook.')
    parser.add_argument('--platform', type=str, required=True, choices=['wechat', 'tiktok'], help='Platform to scrape (wechat or tiktok).')
    parser.add_argument('--blogger_name', type=str, help='Name of the blogger (for WeChat).')
    parser.add_argument('--tiktok_url', type=str, help='TikTok homepage URL (for TikTok).')
    parser.add_argument('--webhook_url', type=str, required=True, help='Webhook URL to send data to.')
    parser.add_argument('--quantity', type=int, default=10, help='Quantity of data to fetch (default: 10).')
    parser.add_argument('--request_id', type=str, default='', help='Unique request ID.')

    args = parser.parse_args()

    platform = args.platform
    webhook_url = args.webhook_url
    query_count = args.quantity
    request_id = args.request_id

    video_data = []

    if platform == 'wechat':
        if not args.blogger_name:
            print("错误: WeChat平台需要提供blogger_name参数")
            return
        
        blogger_name = args.blogger_name
        blogger_id = get_blogger_id(blogger_name)

        if blogger_id:
            print(f"获取到的博主ID: {blogger_id}")
            video_data = get_blogger_videos(blogger_id, query_count)

            if video_data:
                # 获取并添加评论数据
                for video in video_data:
                    print(f"当前处理视频: {video}") # 添加这行用于调试
                    video_id = video.get('id')
                    object_nonce_id = video.get('objectNonceId') # 假设视频数据中包含 objectNonceId
                    if video_id and object_nonce_id:
                        comments = get_video_comments(video_id, object_nonce_id)
                        video['comments'] = comments
                    else:
                        video['comments'] = []
        else:
            print("未能获取到博主ID。")
    
    elif platform == 'tiktok':
        if not args.tiktok_url:
            print("错误: TikTok平台需要提供tiktok_url参数")
            return
        
        tiktok_url = args.tiktok_url
        print(f"正在处理TikTok链接: {tiktok_url}")
        
        # 获取secuid
        secuid = get_tiktok_secuid(tiktok_url)
        if secuid:
            # 循环获取TikTok视频数据直到hasMore为false或达到指定数量
            all_videos = []
            cursor = 0
            retrieved_count = 0
            
            print(f"\n正在获取TikTok博主的视频数据，目标数量: {query_count}")
            
            while retrieved_count < query_count:
                # 计算本次请求需要获取的数量
                remaining_count = query_count - retrieved_count
                current_request_count = min(remaining_count, 30)  # 单次最多30条
                
                print(f"正在请求第 {len(all_videos) // 30 + 1} 页，cursor: {cursor}，请求数量: {current_request_count}")
                
                # 获取当前页的视频数据
                result = get_tiktok_user_posts(secuid, current_request_count, cursor)
                
                if not result["videos"]:
                    print("未获取到视频数据，停止请求")
                    break
                
                # 添加到总列表
                all_videos.extend(result["videos"])
                retrieved_count += len(result["videos"])
                
                print(f"本次获取 {len(result['videos'])} 个视频，累计: {retrieved_count}/{query_count}")
                
                # 检查是否还有更多数据
                if not result["hasMore"]:
                    print("已获取所有可用视频")
                    break
                
                # 更新cursor用于下次请求
                cursor = result["cursor"]
                if not cursor:
                    print("cursor为空，停止请求")
                    break
            
            video_data = all_videos[:query_count]  # 确保不超过请求数量
            print(f"\n最终获取到 {len(video_data)} 个TikTok视频")
        else:
            print("未能获取到TikTok secuid。")

    # 处理获取到的视频数据
    if video_data:
        # 打印获取到的视频数据
        print(f"\n获取到的{platform}视频数据:")
        for i, video in enumerate(video_data, 1):
            print(f"视频 {i}: {json.dumps(video, indent=2, ensure_ascii=False)}")
        
        if webhook_url:
            send_webhook_data(webhook_url, video_data, request_id)
        else:
            print("未提供webhook地址，跳过数据回传。")
    else:
        print(f"未能获取到{platform}视频数据。")


if __name__ == "__main__":
    main()