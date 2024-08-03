from PIL import Image
import imagehash

def model_list_to_dict(modelList: list):
    result = {}
    for index, model in enumerate(modelList):
        result.update({index: model.dict()})
    return result

def img_simi(img_url,arr):
    simi = 0
    simi_img = ''
    for img in arr:
        # 生成图像的感知哈希
        hash1 = imagehash.average_hash(Image.open(img_url))
        hash2 = imagehash.average_hash(Image.open(img))
        # 计算相似度
        similarity = 1 - (hash1 - hash2) / len(hash1.hash)  # 范围为0到1，值越大表示相似度越高
        if similarity > simi:
            simi = similarity
            simi_img = img

    return simi_img
