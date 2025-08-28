import requests
import json
import argparse

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

def send_webhook_data(webhook_url, video_data):
    print(f"\n正在向webhook地址 {webhook_url} 回传视频数据...")
    try:
        response = requests.post(webhook_url, json=video_data)
        response.raise_for_status()
        print("视频数据回传成功！")
    except requests.exceptions.RequestException as e:
        print(f"视频数据回传失败: {e}")

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
            
            comments = data_json.get("output", [])
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

def main():
    parser = argparse.ArgumentParser(description='Fetch blogger data and send to webhook.')
    parser.add_argument('--blogger_name', type=str, required=True, help='Name of the blogger.')
    parser.add_argument('--webhook_url', type=str, required=True, help='Webhook URL to send data to.')
    parser.add_argument('--quantity', type=int, default=10, help='Quantity of data to fetch (default: 10).')

    args = parser.parse_args()

    blogger_name = args.blogger_name
    webhook_url = args.webhook_url
    query_count = args.quantity

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

            # 打印包含评论的视频数据
            print("\n获取到的包含评论的视频数据:")
            for video in video_data:
                print(json.dumps(video, indent=2, ensure_ascii=False))
            
            if webhook_url:
                send_webhook_data(webhook_url, video_data)
            else:
                print("未提供webhook地址，跳过数据回传。")
        else:
            print("未能获取到视频数据。")
    else:
        print("未能获取到博主ID。")


if __name__ == "__main__":
    main()