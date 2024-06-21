"""
Add a short description of your script here

See https://docs.engineeredarts.co.uk/ for more information
"""


encoding = 'utf-8'

class VisualTasks:
    VQA = 'VQA'
    VideoRecognition = 'VideoRec'
    VideoRecogPoseGen = 'VideoRecPoseGen'  # video recognition with pose generation
    FaceRecognition = 'FaceRec'
    EmoRecognition = 'EmoRecognition'

class ResponseCode:
	KeepSilent = 0
	Success = 1
	Fail = 2


class Config:
    # vpub_addr = 'tcp://0.0.0.0:5001'  # publish video capture data
    face_det_pub_addr = 'tcp://0.0.0.0:6666'  # backed server address
    visual_task_addr = 'tcp://0.0.0.0:2002'  # Ameca host addr
