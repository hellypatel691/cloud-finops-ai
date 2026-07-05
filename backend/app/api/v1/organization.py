from fastapi import APIRouter

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


@router.get("/")
def get_organizations():

    return {
        "message": "Organizations endpoint working!"
    }