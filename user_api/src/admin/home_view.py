import base64
from io import BytesIO

import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, select
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView

from src.core.config import settings
from src.models import Device, Message, Site, User


class HomeView(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            request,
            name="home.html",
            context={
                "users": await self.users_count(request, User),
                "sites": await self.sites_count(request, Site),
                "devices": await self.devices_count(request, Device),
                "version": settings.VERSION,
                "messages_img": await self.generate_image(request),
            },
        )

    async def generate_image(self, request: Request) -> str:
        session: Session = request.state.session
        stmt = (
            select(
                func.date_trunc("day", Message.inserted_on).label("day"),
                func.count(Message.id).label("count"),
            )
            .group_by("day")
            .order_by("day")
        )
        result = session.execute(stmt).fetchall()

        data = [
            {"day": row.day.strftime("%m-%d"), "count": row.count} for row in result
        ]

        x = [row["day"] for row in data]
        y = [row["count"] for row in data]

        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot()
        ax.yaxis.set_ticks_position("right")
        ax.yaxis.set_label_position("right")
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        plt.tight_layout(pad=3)
        plt.plot(x, y)
        plt.xlabel("Day")
        plt.ylabel("Count")
        plt.xticks(x[::7], rotation=45, ha="right")

        tmpfile = BytesIO()
        fig.savefig(tmpfile, format="png")

        encoded = base64.b64encode(tmpfile.getvalue()).decode()
        return encoded

    async def users_count(self, request: Request, obj: User) -> int:
        session: Session = request.state.session
        stmt = select(func.count(User.id))
        count = session.execute(stmt).scalar_one()
        return count

    async def sites_count(self, request: Request, obj: Site) -> int:
        session: Session = request.state.session
        stmt = select(func.count(Site.id))
        count = session.execute(stmt).scalar_one()
        return count

    async def devices_count(self, request: Request, obj: Device) -> int:
        session: Session = request.state.session
        stmt = select(func.count(Device.id))
        count = session.execute(stmt).scalar_one()
        return count
