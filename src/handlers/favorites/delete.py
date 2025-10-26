from src.lib.responses import success, error
from src.repositories.favorite_repository import get_favorite_repository
from uuid import UUID


def delete_request(event, _):
    favorite_repo = get_favorite_repository()
    try:
        favorite_id = UUID(event.get("pathParameters", {}).get("favorite_id"))
        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = UUID(claims.get("sub"))

        favorite = favorite_repo.get_by_id(favorite_id=favorite_id)

        if not favorite:
            return True
        if favorite.user_id != user_id:
            return error(
                "Forbidden: you can only delete your own requests", status_code=403
            )

        favorite_repo.delete(favorite_id=favorite_id)

        return success(
            {"message": "Request deleted successfully", "favorite_id": favorite_id}
        )
    except Exception as e:
        return error(str(e))
