"""
    将列表里的对象逐一转化为字典, 对象需提供 dict 方法
"""
def model_list_to_dict(modelList: list):
    result = {}
    for index, model in enumerate(modelList):
        result.update({index: model.dict()})
    return result

