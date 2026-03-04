import json
import re


def clean_trailing_commas(s: str) -> str:
    # 去掉 } ] 前面紧挨着的多余逗号：",}" -> "}" ，",]" -> "]"
    s = re.sub(r',(\s*[}\]])', r'\1', s)
    return s


parsed_result = json.loads(clean_trailing_commas("""
{
  "thought": [
    "10:08:20-10:08:26连续帧中，检测到店员将热菜放入绿框烤箱；10:08:33-10:08:36连续帧中，检测到店员将炸品类放入绿框烤箱；两次放入均满足有效放入动作全部条件，商品类别均可清晰辨认，未发现包子/玉米与热菜同炉的混合违规，放入商品均与目标分类热菜匹配（炸品放入不影响合规判定）",
  ],
  "keyPutPicCount": 8,
  "process": [
    "10:08:20-10:08:26, 店员将热菜连同烤盘推入烤箱",
    "10:08:33-10:08:36, 店员将炸品连同烤盘推入烤箱"
  ],
  "timeRange": "10:08:20-10:08:46",
  "itemCategory": "热菜,炸品",
  "qualified": "pass",
  "ret": "pass"
}
"""))

print(parsed_result)
