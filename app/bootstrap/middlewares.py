from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.configs.origins import origins


def middlewares_config(app:FastAPI):
	app.add_middleware(
	    CORSMiddleware,
	    allow_origins=origins,
	    allow_credentials=True,
	    allow_methods=["*"],
	    allow_headers=["*"],
	)
