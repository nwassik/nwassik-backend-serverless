"""Request Repository."""

import base64
import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, asc, or_

from src.db.session import get_db_session
from src.models.request import (
    BuyAndDeliverRequest,
    OnlineServiceRequest,
    PickupAndDeliverRequest,
    Request,
)
from src.repositories.interfaces import RequestRepositoryInterface
from src.schemas.request import RequestCreate, RequestType, RequestUpdate

_request_repo_instance = None


# NOTE: for now I keep this as a singleton, though it does not mean that
# DB sessions are the same across same AWS lambda calls. Actually, get_db_session,
# for now creates a new session for every call, so we are safe. I am keeping this
# in case I move out from Lambda to something like FlaskAPI/FastAPI, where I can
# reuse long running sessions. AWS Lambda are short lived/running environments.
def get_request_repository() -> "RequestRepository":
    """Get a request repository instance."""
    global _request_repo_instance  # noqa: PLW0603
    if _request_repo_instance is None:
        _request_repo_instance = RequestRepository()
    return _request_repo_instance


class RequestRepository(RequestRepositoryInterface):
    """Request Repository containing all necessary methods."""

    def create(self, user_id: "UUID", input_request: "RequestCreate") -> Request:
        with get_db_session() as db:
            request = Request(
                user_id=user_id,
                type=input_request.type,
                title=input_request.title,
                description=input_request.description,
                due_date=input_request.due_date,
            )

            if input_request.type == RequestType.BUY_AND_DELIVER:
                subtype = BuyAndDeliverRequest(
                    request_id=request.id,
                    dropoff_latitude=input_request.dropoff_latitude,
                    dropoff_longitude=input_request.dropoff_longitude,
                )
                request.buy_and_deliver = subtype

            elif input_request.type == RequestType.PICKUP_AND_DELIVER:
                subtype = PickupAndDeliverRequest(
                    request_id=request.id,
                    pickup_latitude=input_request.pickup_latitude,
                    pickup_longitude=input_request.pickup_longitude,
                    dropoff_latitude=input_request.dropoff_latitude,
                    dropoff_longitude=input_request.dropoff_longitude,
                )
                request.pickup_and_deliver = subtype

            elif input_request.type == RequestType.ONLINE_SERVICE:
                subtype = OnlineServiceRequest(
                    request_id=request.id,
                    meetup_latitude=input_request.meetup_latitude,
                    meetup_longitude=input_request.meetup_longitude,
                )
                request.online_service = subtype

            else:
                exception_msg = "New request type was added but not integrated here"
                raise ValueError(exception_msg)

            # NOTE: we are still inside of a context manager block
            # So still no commit. The commit happends automatically
            # in the wrapper

            # SINGLE OPERATION - cascade handles everything
            db.add(request)
            return request

    def get_by_id(self, request_id: UUID) -> Request | None:
        with get_db_session() as db:
            return db.query(Request).filter(Request.id == request_id).first()

    def get_user_requests(self, user_id: UUID) -> list[Request]:
        with get_db_session() as db:
            return db.query(Request).filter(Request.user_id == user_id).all()

    # FIXME: The list is not working properly, and has a bug when create_at and due_date are
    # the same in two requests. This is expected as they are necessarly unique (though it is
    # a possible rare case due to millisecond precision on both attributes)
    def list_of_requests(
        self,
        request_type: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List Requests in pagination mode.

        Fetch paginated requests with proper cursor-based pagination.
        Earlier due dates show first, later due dates show after.
        Requests without due_date come last, ordered by created_date ASC (oldest first).
        Uses only date fields for ordering (UUIDs are random).
        """
        try:
            # Build base query
            query = self.db.query(Request)

            # Apply type filter if provided
            if request_type:
                query = query.filter(Request.type == request_type)

            # Apply cursor-based pagination
            if cursor:
                cursor_data = self._decode_cursor(cursor)
                query = self._apply_cursor_filter(query, cursor_data)

            # Order by due_date ASC (earlier first), NULLS LAST, then created_date ASC
            # No ID ordering since UUIDs are random
            query = query.order_by(
                asc(Request.due_date).nulls_last(),  # Earlier due_dates first, NULLs last
                asc(
                    Request.created_date,
                ),  # Older requests first for same due_date AND for NULL due_dates
            )

            # Get one extra item to check if there's more
            requests = query.limit(limit + 1).all()

            # Check if there are more items
            has_more = len(requests) > limit
            if has_more:
                requests = requests[:-1]  # Remove the extra item

            # Generate next cursor
            next_cursor = None
            if has_more and requests:
                next_cursor = self._generate_next_cursor(requests[-1])

            return {
                "requests": requests,
                "pagination": {
                    "next_cursor": next_cursor,
                    "has_more": has_more,
                    "limit": limit,
                },
            }

        except Exception as e:
            exception_msg = f"Error listing requests: {e!r}"
            raise Exception(exception_msg) from e

    def update(self, request_id: UUID, request_update: RequestUpdate) -> Request:
        with get_db_session() as db:
            # Apply updates
            request = db.query(Request).filter(Request.id == request_id).first()
            if not request:
                exception_msg = "Workflow should not be happening"
                raise Exception(exception_msg)

            for attr, value in request_update.model_dump(exclude_unset=True).items():
                setattr(request, attr, value)
            return request

    def delete(self, request_id: UUID) -> bool:
        with get_db_session() as db:
            req = db.query(Request).filter(Request.id == request_id).first()
            if not req:
                return True
            db.delete(req)
            return True

    def _generate_next_cursor(self, last_request: Request) -> str:
        """Generate Next Cursor For List Pagination.

        Generate cursor from the last request in the current page.
        Only uses date fields since IDs are random UUIDs.
        """
        cursor_data = {
            "due_date": last_request.due_date.isoformat() if last_request.due_date else None,
            "created_date": last_request.created_at.isoformat(),
        }

        cursor_json = json.dumps(cursor_data)
        return base64.b64encode(cursor_json.encode()).decode()

    def _decode_cursor(self, cursor: str) -> dict[str, Any]:
        """Decode and parse cursor data."""
        try:
            cursor_json = base64.b64decode(cursor.encode()).decode()
            cursor_data: dict = json.loads(cursor_json)

            # Parse dates back to datetime objects
            if cursor_data.get("due_date"):
                cursor_data["due_date"] = datetime.fromisoformat(cursor_data["due_date"])
            cursor_data["created_date"] = datetime.fromisoformat(cursor_data["created_date"])

            return cursor_data
        except (ValueError, json.JSONDecodeError) as e:
            exception_msg = "Invalid cursor"
            raise ValueError(exception_msg) from e

    def _apply_cursor_filter(self, query, cursor_data):  # noqa
        """Apply cursor filter using only date fields.

        Since UUIDs are random, we accept that items with identical dates might have minor
        pagination issues.
        """
        due_date = cursor_data["due_date"]
        created_date = cursor_data["created_date"]

        if due_date:
            # Case 1: due_date is not NULL in cursor
            condition = or_(
                # Requests with later due_date (should come after)
                Request.due_date > due_date,
                # Requests with same due_date but newer created_date (should come after)
                and_(Request.due_date == due_date, Request.created_at > created_date),
                # Requests with NULL due_date (these come last)
                Request.due_date.is_(None),
            )
        else:
            # Case 2: cursor had NULL due_date (we're in the NULL section)
            # Simply get requests with newer created_date
            condition = Request.created_date > created_date

        return query.filter(condition)
