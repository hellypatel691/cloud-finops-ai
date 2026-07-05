# # # from fastapi import FastAPI

# # # app = FastAPI(
# # #     title="Cloud FinOps AI",
# # #     version="1.0.0",
# # #     description="AI Powered Cloud Cost Intelligence Platform"
# # # )


# # # @app.get("/")
# # # def root():

# # #     return {
# # #         "status": "Healthy",
# # #         "application": "Cloud FinOps AI",
# # #         "version": "1.0.0"
# # #     }


# # # @app.get("/health")
# # # def health():

# # #     return {
# # #         "server": "Running",
# # #         "database": "Not Connected Yet",
# # #         "ml_service": "Not Loaded Yet"
# # #     }
# # # # def root():

# # # #     return {
# # # #         "message": "Welcome to Cloud FinOps AI 🚀"
# # # #     }


# # # from fastapi import FastAPI

# # # app = FastAPI(
# # #     title="Cloud FinOps AI",
# # #     version="1.0.0"
# # # )


# # # @app.get("/")
# # # def root():

# # #     return {
# # #         "message": "Cloud FinOps AI Backend Running 🚀"
# # #     }


# # # @app.get("/health")
# # # def health():

# # #     return {
# # #         "status": "healthy",
# # #         "database": "Connecting Soon..."
# # #     }


# # from fastapi import FastAPI

# # app = FastAPI(
# #     title="Cloud FinOps AI",
# #     version="1.0.0",
# #     description="AI Powered Cloud Cost Intelligence Platform"
# # )


# # # @app.get("/")
# # @app.get("/")
# # def root():

# #     return {
# #         "status": "Healthy",
# #         "application": "Cloud FinOps AI",
# #         "version": "1.0.0"
# #     }


# # @app.get("/health")
# # def health():

# #     return {
# #         "server": "Running",
# #         "database": "Not Connected Yet",
# #         "ml_service": "Not Loaded Yet"
# #     }
# # def root():

# #     return {
# #         "message": "Welcome to Cloud FinOps AI 🚀"
# #     }


# from fastapi import FastAPI

# app = FastAPI(
#     title="Cloud FinOps AI",
#     version="1.0.0"
# )


# @app.get("/")
# def root():

#     return {
#         "message": "Cloud FinOps AI Backend Running 🚀"
#     }


# @app.get("/health")
# def health():

#     return {
#         "status": "healthy",
#         "database": "Connecting Soon..."
#     }

from fastapi import FastAPI

from backend.app.api.v1.organization import router as organization_router

app = FastAPI(
    title="Cloud FinOps AI",
    version="1.0.0"
)

app.include_router(
    organization_router,
    prefix="/api/v1"
)


@app.get("/")
def root():

    return {
        "application": "Cloud FinOps AI"
    }