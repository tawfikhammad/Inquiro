from fastapi import APIRouter, Request, Body, status
from fastapi.responses import JSONResponse
from controllers.chat_controller import ChatController

chat_router = APIRouter()
chat_controller = ChatController()

@chat_router.post("/generate")
async def generate_chat_response(request: Request, prompt: str = Body(...), history: list = Body(default=[])):
    response = await chat_controller.chat(prompt=prompt, chat_history=history)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"response": response})
