from utils import load_model
from fastapi import FastAPI, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from torchvision.models import resnet18
import torch
from PIL import Image
import torchvision.transforms as transforms
import json
import io

# Load the model
filename = './demeter_fruits_v3.1_weights_best_acc.tar'
model = resnet18(num_classes=172)
load_model(model, filename=filename)
model.eval()

# Preprocessing steps
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Initialize FastAPI app
app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)



# Define API endpoint
@app.post("/predict")
async def create_upload_file(request: Request):
    body = await request.body()
    img = Image.open(io.BytesIO(body)).convert("RGB") 

    img_tensor = preprocess(img)
    img_tensor = img_tensor.unsqueeze(0) 
    with torch.no_grad():
        output = model(img_tensor)
        _, predicted = torch.max(output, 1)

    class_label = predicted.item()


    with open('./fruits_name.json', 'r', encoding='utf-8') as file:
        class_names_dict = json.load(file)
    
    # with open('./commom_name_vietnamese.json', 'r', encoding='utf-8') as file:
    #     class_common_dict = json.load(file)
   
    # class FungiData:
    #     def __init__(self, json_file_path):
    #     # Mở và đọc dữ liệu từ tệp JSON
    #         with open(json_file_path, 'r', encoding='utf-8') as file:
    #             self.class_names_dict = json.load(file)
    
    #     def get_fungi_name(self, class_label):
    #     # Chuyển class_label thành chuỗi để làm khóa
    #         class_label_str = str(class_label)
    #     # Kiểm tra xem khóa có tồn tại trong từ điển không
    #         if class_label_str in self.class_names_dict:
    #             return self.class_names_dict[class_label_str]
      
    # json_file_path = './fungi_name.json'
    # fungi_data = FungiData(json_file_path)

   

    # the_name = list(class_names_dict.values())[class_label]
    # common_name = list(class_common_dict.values())[class_label]
    the_name = list(class_names_dict.values())[class_label][0]
    common_name = list(class_names_dict.values())[class_label][1]
    # common_name = fungi_data.get_fungi_name(class_label)
    # print(class_label)
    return {'common_name': common_name, 'name': the_name}
    # return{'name': common_name}
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,port=8000)
