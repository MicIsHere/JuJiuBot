import difflib
import json
import asyncio
import random
from nonebot import logger, on_message, on_regex
from nonebot.rule import fullmatch
from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment
from httpx import AsyncClient
from nonebot import on_startswith
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

# 指令前缀
command_arg = "牛牛画图"

#启用GPT提示词生成
enable_gpt_prompt = True
# GPT API Key
gpt_api_key = "sk-XHdMxUUwTu5ftmiq553418284b174d33B0D9E890355e9f1d"
# 使用什么GPT模型生成
gpt_api_model = "gpt-3.5-turbo"
# GPT 转发URL
gpt_api_url = "https://api.openai.one/v1/chat/completions"

# 最大图片检查次数
max_check_image_number = 50
# Lora 的总权重
total_weight = 100
# Lora 关键词的匹配值
lora_matcher_ratio = 0.8
# 模型关键词的匹配值
model_matcher_ratio = 0.15
# Kamiya API Key
kamiya_api_key = "sk-4QM9VWd1ACatZiaeuGxGJgpfHkzwnZceJ9FlZcNZrwyoPPMY"


# 以下变量非必要不更改！！！影响执行逻辑！！！
# Kamiya 绘图服务的网址
kamiya_api_draw_url = "https://p0.kamiya.dev/api/image/generate/"
# Kamiya 绘图服务获取配置的网址
kamiya_api_getconfig_url = "https://p0.kamiya.dev/api/image/config"
# 向 Kamiya API 提交的验证Header
kamiya_api_header = {
    'Accept': 'application/json',
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(kamiya_api_key)
}
# 向 Kamiya 绘图服务发送的 Payload 数据
kamiya_api_payload = {
    "type": "text2image",
    "prompts": "None",
    "negativePrompts": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
    "step": 28,
    "cfg": 12,
    "seed": 218506577,
    "sampling": "DPM++ 2M Karras",
    "width": 768,
    "height": 512,
    "model": "anything_v3",
    "LoRAs": [{}]
}
gpt_api_headers = {
   'Authorization': 'Bearer {}'.format(gpt_api_key),
   'Accept': 'application/json',
   'Content-Type': 'application/json'
}
gpt_api_content = '''# Stable Diffusion prompt 助理

你来充当一位有艺术气息的Stable Diffusion prompt 助理。

## 任务

我用自然语言告诉你要生成的prompt的主题，你的任务是根据这个主题想象一幅完整的画面，然后转化成一份详细的、高质量的prompt，让Stable Diffusion可以生成高质量的图像。

## 背景介绍

Stable Diffusion是一款利用深度学习的文生图模型，支持通过使用 prompt 来产生新的图像，描述要包含或省略的元素。

## prompt 概念

- 完整的prompt包含“**Prompt:**”和"**Negative Prompt:**"两部分。
- prompt 用来描述图像，由普通常见的单词构成，使用英文半角"@"做为分隔符。
- negative prompt用来描述你不想在生成的图像中出现的内容。
- 以"@"分隔的每个单词或词组称为 tag。所以prompt和negative prompt是由系列由"@"分隔的tag组成的。

## () 和 [] 语法

调整关键字强度的等效方法是使用 () 和 []。 (keyword) 将tag的强度增加 1.1 倍，与 (keyword$1.1) 相同，最多可加三层。 [keyword] 将强度降低 0.9 倍，与 (keyword$0.9) 相同。

## Prompt 格式要求

下面我将说明 prompt 的生成步骤，这里的 prompt 可用于描述人物、风景、物体或抽象数字艺术图画。你可以根据需要添加合理的、但不少于5处的画面细节。

### 1. prompt 要求

- 你输出的 Stable Diffusion prompt 以“**prompt:**”开头。
- prompt 内容包含画面主体、材质、附加细节、图像质量、艺术风格、色彩色调、灯光等部分，但你输出的 prompt 不能分段，例如类似"medium:"这样的分段描述是不需要的，也不能包含":"和"."。
- 画面主体：不简短的英文描述画面主体, 如 A girl in a garden，主体细节概括（主体可以是人、事、物、景）画面核心内容。这部分根据我每次给你的主题来生成。你可以添加更多主题相关的合理的细节。
- 对于人物主题，你必须描述人物的眼睛、鼻子、嘴唇，例如'beautiful detailed eyes@beautiful detailed lips@extremely detailed eyes and face@longeyelashes'，以免Stable Diffusion随机生成变形的面部五官，这点非常重要。你还可以描述人物的外表、情绪、衣服、姿势、视角、动作、背景等。人物属性中，1girl表示一个女孩，2girls表示两个女孩。
- 材质：用来制作艺术品的材料。 但你不需要，也不能让你输出的 prompt 包含这类描述。
- 附加细节：画面场景细节，或人物细节，描述画面细节内容，让图像看起来更充和合理。这部分是可选的，要注意画面的整体和谐，不能与主题冲突。
- 图像质量：这部分内容开头永远要加上“(best quality@4k@8k@highres@masterpiece$1.2)@ultra-detailed@(realistic@photorealistic@photo-realistic$1.37)”， 这是高质量的标志。其它常用的提高质量的tag还有，你可以根据主题的需求添加：HDR@UHD@studio lighting@ultra-fine painting@sharp focus@physically-based rendering@extreme detail description@professional@vivid colors@bokeh。
- 艺术风格：这部分描述图像的风格。加入恰当的艺术风格，能提升生成的图像效果。你加入的的艺术风格需要尽可能的贴近动漫风格。常用的艺术风格例如：portraits@landscape@horror@anime@sci-fi@photography@concept artists等。
- 色彩色调：颜色，通过添加颜色来控制画面的整体颜色。
- 灯光：整体画面的光线效果。

### 2. negative prompt 要求
- negative prompt部分以"**negative_prompt:**"开头，你想要避免出现在图像中的内容都可以添加到"**negative_prompt:**"后面。
- 任何情况下，negative prompt都要包含这段内容："nsfw@(low quality@normal quality@worst quality@jpeg artifacts)@cropped@monochrome@lowres@low saturation@((watermark))@(white letters)"
- 如果是人物相关的主题，你的输出需要另加一段人物相关的 negative prompt，内容为：“skin spots@acnes@skin blemishes@age spot@mutated hands@mutated fingers@deformed@bad anatomy@disfigured@poorly drawn face@extra limb@ugly@poorly drawn hands@missing limb@floating limbs@disconnected limbs@out of focus@long neck@long body@extra fingers@fewer fingers@(multi nipples)@bad hands@signature@username@bad feet@blurry@bad body”。

### 3.输出要求

- 输出的内容必须是**Json**
- 必须按照以下Json**格式**输出，但其中的prompt和negative_prompt内容信息部分你可以自行填写：{"prompt": "beautiful detailed lips@extremely detailed eyes and face@longeyelashes@hair accessories@blue hair@sparkling eyes@adorable smile@standing pose@front view@studio lighting","negative_prompt": "nsfw@(low quality@normal quality@worst quality@jpeg artifacts)@cropped@monochrome@lowres@low saturation@((watermark))@(white letters)@skin spots"}

### 4. 限制：
- tag 内容用英语单词或短语来描述，并不局限于我给你的单词。注意只能包含关键词或词组。
- 注意不要输出句子，不要有任何解释。
- tag数量限制60个以内，单词数量限制在80个以内。
- tag不要带引号("")。
- 使用英文半角"@"做分隔符。
- tag 按重要性从高到低的顺序排列。
- 我给你的主题可能是用中文描述，你给出的prompt和negative prompt只用英文。
'''

gpt_api_payload = {
   "model": gpt_api_model,
   "messages": [
      {
         "role": "user",
         "content": gpt_api_content
      },
      {
         "role": "user",
         "content": "None"
      },
   ],
   "stream": False
}

matcher = on_startswith(command_arg, ignorecase=True)
lora_matcher = difflib.SequenceMatcher()
model_matcher = difflib.SequenceMatcher()

@matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    
    split_message = str(event.message).split(" ")

    # 将所有中文逗号全部替换为英文，并分割提示词。
    # 该过程出现 IndexError 错误则代表未输入提示词。
    try:
        prompts = split_message[1].replace("，",",")
    except IndexError:
        await matcher.finish("您的输入有误!\n指令用法: 牛牛画图 [提示词]")

    await matcher.send("命令解析成功!\n开始获取Kamiya端侧数据...")

    try:
        async with AsyncClient() as client:
            response = await client.get(kamiya_api_getconfig_url, headers=kamiya_api_header, timeout=10)
    except httpcore.ReadTimeout:
        await matcher.finish("获取数据失败，因为Kamiya端响应超时。")

    if response.status_code != 200:
        await matcher.finish("获取Kamiya端侧数据失败...\n状态码: {}".format(response.status_code))

    # 读取data数据
    raw_data = response.json()["data"]
    
    # 读取服务状态
    busy_status = raw_data["busyStatus"]    

    # 开始匹配Lora模型
    await matcher.send("获取Kamiya端侧数据成功，开始解析数据...\n{}。".format(busy_status))

    # 匹配 Model
    await matcher.send("开始匹配Model...")
    for data_item in prompts.split(","):
        model_found_match = False
    
        for item in raw_data["availableModels"]:
            description = item.get("description", "")
            model_matcher.set_seqs(data_item, description)  # 设置序列
            ratio = model_matcher.ratio() # 计算相似度
        
            if ratio > model_matcher_ratio:  # 设置一个阈值，当相似度大于model_matcher_ratio时认为是匹配项
                id_value = item.get("id", "ID not found")
                await matcher.send("已匹配到Kamiya端侧Model数据!\nlora:{},id:{},raw_prompts{},ratio:{}".format(data_item, id_value, prompts, ratio))
                model_found_match = True
                # 优先拼接Model
                kamiya_api_payload["model"] = id_value
                break  # 找到匹配项后跳出循环
            break

        if not model_found_match:
            await matcher.send("未匹配到Kamiya端侧Model数据，使用默认模型...\nlora:{},ratio:{}".format(data_item,ratio))

    # 定义匹配的Lora字典
    lora_dict = {}

    # 匹配LoRAs
    await matcher.send("开始匹配LoRAs...")
    for data_item in prompts.split(","):
        lora_found_match = False
    
        for item in raw_data["availableLoRAs"]:
            name = item.get("name", "")
            lora_matcher.set_seqs(data_item, name)  # 设置序列
            ratio = lora_matcher.ratio() # 计算相似度
        
            if ratio > lora_matcher_ratio:  # 设置一个阈值，当相似度大于lora_matcher_ratio时认为是匹配项
                id_value = item.get("id", "ID not found")
                await matcher.send("已匹配到Kamiya端侧Lora数据!\nlora:{},id:{},raw_prompts{},ratio:{}".format(data_item, id_value, prompts, ratio))
                lora_found_match = True
                lora_dict[data_item] = id_value # 将匹配成功的lora放入字典
                prompts = prompts.replace(data_item,"")
                break  # 找到匹配项后跳出循环

        if not lora_found_match:
            await matcher.send("未匹配到Kamiya端侧Lora数据!\nlora:{},ratio:{}".format(data_item,ratio))

    lora_dict_length = len(lora_dict)

    if lora_dict_length > 0:
        await matcher.send("总计匹配{}个了Lora，开始计算权重...\nraw_lora:{}".format(lora_dict_length, lora_dict))
        
        weights = {}
        lora_dict_final = {}

        # 计算lora
        weights_sum = sum(range(1, lora_dict_length + 1))
        for idx, key in enumerate(lora_dict.keys()):
            weight = total_weight * (lora_dict_length - idx) / weights_sum
            weights[key] = int(weight)

        # 为lora字典添加权重
        for key, weight in weights.items():
            lora_dict_final[key] = {"id": lora_dict[key], "weight": weight}
    
        lora_dict_values_only = list(lora_dict_final.values())
        await matcher.send("权重计算完毕！\n{}".format(lora_dict_values_only))
    else:
        lora_dict_values_only = []
        await matcher.send("未匹配到Lora，不计算权重...")

    if enable_gpt_prompt:
        await matcher.send("开始生成Prompts...\n\nPrompts生成服务由OriginGPT与起源云业提供服务支持。\nsend_prompts:{}".format(prompts))

        gpt_api_payload["messages"][1]["content"] = "我的第一个主题是：{}".format(prompts)

        try:
            async with AsyncClient() as client:
                response = await client.post(gpt_api_url, headers=gpt_api_headers, data=json.dumps(gpt_api_payload), timeout=20)
        except httpcore.ReadTimeout:
            await matcher.finish("获取数据失败，因为OriginGPT端响应超时。")

        if response.status_code != 200:
            await matcher.finish("获取OriginGPT端侧数据失败...\n状态码: {}".format(response.status_code))

        await matcher.send("获取OriginGPT端侧数据成功，开始解析并转义数据...")

        message = response.json()["choices"][0]["message"]["content"].replace("\n","").replace("\\","")

        gpt_prompts = json.loads(message)["prompt"].replace("@",",").replace("$",":")
        gpt_negative_prompts = json.loads(message)["negative_prompt"].replace("@",",").replace("$",":")

        await matcher.send("prompts: {} \n\nnegative_prompt: {}".format(gpt_prompts, gpt_negative_prompts))

        kamiya_api_payload["prompts"] = gpt_prompts
        kamiya_api_payload["negativePrompts"] = gpt_negative_prompts
    else:
        kamiya_api_payload["prompts"] = prompts

    await matcher.send("拼接Payload...")

    # 拼接Payload
    kamiya_api_payload["LoRAs"] = lora_dict_values_only
    kamiya_api_payload["seed"] = random.randint(1,100000000)

    await matcher.send("Payload拼接结果:\n{}\n预提交数据...".format(json.dumps(kamiya_api_payload)))

    # 提交绘图请求
    await matcher.send("提交中...")
    try:
        async with AsyncClient() as client:
            response = await client.post(kamiya_api_draw_url, headers=kamiya_api_header, data=json.dumps(kamiya_api_payload), timeout=10)
    except httpcore.ReadTimeout:
        await matcher.finish("提交数据失败，因为Kamiya端侧响应超时。")

    if response.status_code != 200:
        await matcher.finish("提交Payload数据失败...\n状态码: {}\n返回数据:{}".format(response.status_code,response.json()))

    if response.json()["status"] != 200:
        await matcher.finish("提交Payload数据失败...\n状态码: {}\n返回数据:{}".format(response.status_code,response.json()))

    try:
        returned_json = response.json()["data"]
        hash_id = returned_json["hashid"]
    except KeyError:
        await matcher.finish("解析返回数据失败，因为Kamiya端侧返回了错误的数据。")

    await matcher.send("提交Payload数据成功!\n等待Kamiya端侧返回数据...")
    
    # 开始异步检测图片绘制状态
    task = asyncio.create_task(check_image(hash_id))

    try:
        success, url = await asyncio.wait_for(task, timeout=180)  # 设置超时时间为60秒
        if success:
            await matcher.finish("图片生成成功!\n{}".format(url))
        else:
            await matcher.finish("图片生成失败。因为已超过{}次最大尝试检测次数，或检测时出现了错误。".format(max_check_image_number))
    except asyncio.TimeoutError:
        await matcher.finish("图片生成失败。因为Kamiya端侧未返回图片数据。")



async def check_image(hash_id: str) -> (bool, str):

    check_number = 0

    while True:
        try:
            logger.info("检查中...")

            # 检查是否超过最大次数
            if check_number >= max_check_image_number:
                logger.info("生成失败，超过最大次数")
                return False, "None"

            async with AsyncClient() as client:
                check_number += 1
                response = await client.get("{}{}".format(kamiya_api_draw_url, hash_id), headers=kamiya_api_header, timeout=5)
        
            raw_data = response.json()["data"]

            # 状态为生成成功
            if raw_data["status"] == "generated":
                logger.info("生成成功")
                meta_data = raw_data["metadata"]

                url = meta_data["jpg"]

                return True, url

            await asyncio.sleep(5)
        except Exception:
            logger.info("生成失败，出现错误")
            return False, "None"

    logger.info("生成失败，不应出现的错误")
    return False, "None"

