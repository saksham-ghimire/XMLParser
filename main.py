from fastapi import FastAPI,  UploadFile
from pydantic import BaseModel
from handler import ProcessFile
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/")
async def index():
    return {"message":"This is just an simple api nothing has been made above it yet. Please refer to http://localhost:8000/docs for accessing"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    writeable = f'{file.filename.split(".")[0]}.xml'
    with open(writeable,'w') as f:
        content = await file.read()
        f.write(content.decode())
    
    ProcessFile(writeable)
    
    return FileResponse(path=f'outputs/{writeable.split(".")[0]}.xlsx', filename=f'{writeable.split(".")[0]}.xlsx', media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')