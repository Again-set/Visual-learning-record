# from cnocr import CnOcr
#
# img_fp = "C:\\Users\\youyou\\Desktop\\3.png"
# ocr = CnOcr(det_model_name='naive_det')
# out = ocr.ocr(img_fp)
#
# # 这里是关键修改：只提取文本内容
# result_text = ''.join([item['test'] for item in out])
# print(result_text)


import easyocr

reader = easyocr.Reader(['en'], quantize=True)  # this needs to run only once to load the model into memory
result = reader.readtext("C:\\Users\\youyou\\Desktop\\3.png", allowlist='0123456789', detail=0)

print(result)