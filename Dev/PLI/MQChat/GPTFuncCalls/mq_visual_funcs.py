"""
Add a short description of your script here

See https://docs.engineeredarts.co.uk/ for more information
"""
common = system.import_library('../mq_common.py')
encoding = common.encoding
VisualTasks = common.VisualTasks


async def vqa_func(query: str):
    """
        Query the current view of the robot with a natural language question.

        This function has no concept of the names of each person in the image.
        The function will trigger background vqa task and returns immediately.


        Args:
            query: The query to ask to the current view e.g. how many fingers is the person holding up
     """
    system.messaging.post('deal_vtasks', [VisualTasks.VQA.encode(encoding), query.encode(encoding)])


async def face_recog_func():
    """
    Query whether remember the person or ask for the name of the person.
    Respond when being asked whether remember the person, or the name of the person.
    Respond when the person says "How are you"
    The function will trigger background face recognition task and returns immediately.

    """
    system.messaging.post('deal_vtasks', [VisualTasks.FaceRecognition.encode(encoding)])


async def video_recog_func():
    """
    Query what happened or what's going on in the view or ask what the person is doing, or
    describe your observation.
    Respond when being asked about what the person is doing.
    The function will trigger background video recognition task and returns immediately.

    """
    system.messaging.post('deal_vtasks', [VisualTasks.VideoRecogPoseGen.encode(encoding)])
    # system.messaging.post('deal_vtasks', [VisualTasks.VideoRecognition.encode(encoding)])