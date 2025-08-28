# 视频号博主视频信息获取工具

这是一个Python脚本，用于根据视频号博主名称获取其发布的视频信息，并通过webhook回传。

## 功能

1.  根据博主名称获取博主ID。
2.  根据博主ID获取博主视频数据（包含评论数据）。
3.  将获取到的视频数据通过webhook回传。

## 使用方法

1.  **安装依赖**

    在项目根目录下打开终端，运行以下命令安装所需库：

    ```bash
    pip install -r requirements.txt
    ```

2.  **运行脚本**

    ```bash
    python main.py
    ```

    脚本会提示您输入以下信息：

    *   `请输入视频号博主名称:`：您要查询的视频号博主的名称。
    *   `请输入查询数量:`：您希望获取的视频数量。
*   请注意，视频数据中现在会包含每条视频的评论数据。评论数据将包含评论内容、评论时间和点赞数。
    *   `请输入webhook地址:`：用于接收视频数据的webhook URL。

## 注意事项

*   请确保您有权访问 `https://api.coze.cn/v1/workflow/run` 接口，并且 `Authorization` 头中的 `Bearer Token` 是有效的。当前使用的 Token 为 `sat_GfT8DESG9et2OjhJrdWnNgl9ULTLpnacbYkf2cT909ZdH7RWYk5sol5rVufhQcTa`。
*   评论数据获取使用的 `workflow_id` 为 `7543527932590178319`。