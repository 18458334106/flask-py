def model_list_to_dict(modelList: list):
    result = {}
    for index, model in enumerate(modelList):
        result.update({index: model.dict()})
    return result
