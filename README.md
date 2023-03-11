# 如何在抖音上找到漂亮小姐姐----抖音机器人

## 来源
- 参考 [Douyin-Bot](https://github.com/wangshub/Douyin-Bot)

## 配置文件

在config文件夹添加/修改对应的文件中的json文件

```json
"api":{
    "SecretId":"", // 在 [ai.qq.com](https://ai.qq.com) 中找到人脸识别，然后登入控制台即可免费领取一定额度,然后将得到的 `SecretId` 和 `SecretKey` 
    "SecretKey":""
  },
  "star":2, // 点赞方式
  "follow":1, // 关注方式
  "comment":0, // 评论方式
  "comment_contain":"", //评论文本
  "BEAUTY_THRESHOLD":80, // 审美标准
  "GIRL_MIN_AGE":9, // 最小年龄
```

### 配置详解

- star：点赞方式
    - 0：关闭
    - 1：点击爱心点赞（对坐标要求高）
    - 2：双击屏幕中心点赞
- follow：关注方式
    - 0：关闭
    - 1：打开默认方式
- comment：评论方式
    - 0：关闭
    - 1：打开默认方式
