from src.repositories.interfaces import RequestRepositoryInterface
from src.db.session import get_db_session
from src.schemas.request import RequestType
from src.models.request import (
    Request,
    BuyAndDeliverRequest,
    PickupAndDeliverRequest,
    OnlineServiceRequest,
)

from typing import Optional, List
from src.schemas.request import RequestCreate
from uuid import UUID

_request_repo_instance = None


# NOTE: for now I keep this as a singleton, though it does not mean that
# DB sessions are the same across same AWS lambda calls. Actually, get_db_session,
# for now creates a new session for every call, so we are safe. I am keeping this
# in case I move out from Lambda to something like FlaskAPI/FastAPI, where I can
# reuse long running sessions. AWS Lambda are short lived/running environments.
def get_request_repository() -> "RequestRepository":
    global _request_repo_instance
    if _request_repo_instance is None:
        _request_repo_instance = RequestRepository()
    return _request_repo_instance


class RequestRepository(RequestRepositoryInterface):
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
                raise ValueError("New request type was added but not integrated here")

            # NOTE: we are still inside of a context manager block
            # So still no commit. The commit happends automatically
            # in the wrapper

            # SINGLE OPERATION - cascade handles everything
            db.add(request)
            return request

    def get_by_id(self, request_id: UUID) -> Optional[Request]:
        with get_db_session() as db:
            return db.query(Request).filter(Request.id == request_id).first()

    def get_batch_from_last_item(
        self,
        limit: int = 20,
        last_id: Optional[UUID] = None,
    ) -> List[Request]:
        with get_db_session() as db:
            query = db.query(Request)

            if last_id:
                # Look up the last item securely in the database
                last_request = db.query(Request).filter(Request.id == last_id).first()

                if last_request:
                    # Use the actual values from the database to construct the query
                    if last_request.due_date is not None:
                        query = query.filter(
                            (Request.due_date > last_request.due_date)
                            | (
                                (Request.due_date == last_request.due_date)
                                & (Request.created_at > last_request.created_at)
                            )
                            | (
                                (Request.due_date == last_request.due_date)
                                & (Request.created_at == last_request.created_at)
                                & (Request.id > last_request.id)
                            )
                        )
                    else:
                        # Last item had NULL due_date
                        query = query.filter(
                            (Request.due_date.is_(None))
                            & (
                                (Request.created_at > last_request.created_at)
                                | (
                                    (Request.created_at == last_request.created_at)
                                    & (Request.id > last_request.id)
                                )
                            )
                        )
                # If last_id not found, ignore it and start from beginning

            return (
                query.order_by(
                    Request.due_date.asc().nulls_last(),
                    Request.created_at.asc(),
                    Request.id.asc(),
                )
                .limit(limit)
                .all()
            )

    def update(self, request_id, data: dict) -> Request:
        with get_db_session() as db:
            req = db.query(Request).filter(Request.id == request_id).first()
            if not req:
                raise Exception("Workflow should not be happening")
            for k, v in data.items():
                setattr(req, k, v)
            return req

    def delete(self, request_id) -> bool:
        with get_db_session() as db:
            req = db.query(Request).filter(Request.id == request_id).first()
            if not req:
                return True
            db.delete(req)
            return True
