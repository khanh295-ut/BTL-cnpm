from fastapi import FastAPI
from src.routes import project, proposal, review
from src.config.database import Base, engine

# import models để tạo bảng
from src.models import project as project_model
from src.models import proposal as proposal_model
from src.models import review as review_model

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AITasker Backend")

app.include_router(project.router)
app.include_router(proposal.router)
app.include_router(review.router)