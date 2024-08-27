from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
import os
from quart import Quart
from typing import List
from quart_schema import QuartSchema, validate_request, validate_response
from dataclasses import dataclass

app = Quart(__name__)
QuartSchema(app)

async def get_teacher_info(prof_link):
    asession = AsyncHTMLSession()
    URL = prof_link
    res = await asession.get(URL)
    await res.html.arender()

    soup = BeautifulSoup(res.html.html, "lxml")
    ratings = []

    teachers_rating_card = soup.find(
        "div", class_="TeacherRatingsPage__TeacherBlock-sc-1gyr13u-1 jMpSNb"
    )
    if teachers_rating_card:
        teachers_rating = (
            teachers_rating_card.find(
                "div", class_="RatingValue__Numerator-qw8sqy-2 liyUjw"
            ).text
            if teachers_rating_card.find(
                "div", class_="RatingValue__Numerator-qw8sqy-2 liyUjw"
            )
            else "Unknown"
        )
        teachers_firstn = (
            teachers_rating_card.find(
                "div", class_="NameTitle__Name-dowf0z-0 cfjPUG"
            ).span.text
            if teachers_rating_card.find(
                "div", class_="NameTitle__Name-dowf0z-0 cfjPUG"
            )
            else "Unknown"
        )
        teachers_lastn = (
            teachers_rating_card.find(
                "span", class_="NameTitle__LastNameWrapper-dowf0z-2 glXOHH"
            ).text
            if teachers_rating_card.find(
                "span", class_="NameTitle__LastNameWrapper-dowf0z-2 glXOHH"
            )
            else "Unknown"
        )
        teachers_dep = (
            teachers_rating_card.find(
                "a", class_="TeacherDepartment__StyledDepartmentLink-fl79e8-0 iMmVHb"
            ).text
            if teachers_rating_card.find(
                "a", class_="TeacherDepartment__StyledDepartmentLink-fl79e8-0 iMmVHb"
            )
            else "Unkown"
        )
        teachers_school = (
            teachers_rating_card.find(
                "div", class_="NameTitle__Title-dowf0z-1 iLYGwn"
            ).a.text
            if teachers_rating_card.find(
                "div", class_="NameTitle__Title-dowf0z-1 iLYGwn"
            )
            and teachers_rating_card.find(
                "div", class_="NameTitle__Title-dowf0z-1 iLYGwn"
            ).a
            else "Unknown"
        )
        teachers_wta = (
            teachers_rating_card.find(
                "div", class_="FeedbackItem__FeedbackNumber-uof32n-1 kkESWs"
            ).text
            if teachers_rating_card.find(
                "div", class_="FeedbackItem__FeedbackNumber-uof32n-1 kkESWs"
            )
            else "Unknown"
        )
        teachers_lod = (
            teachers_rating_card.find(
                "div", class_="TeacherFeedback__StyledTeacherFeedback-gzhlj7-0 cxVUGc"
            )
            .findAll("div", class_="FeedbackItem__StyledFeedbackItem-uof32n-0 dTFbKx")[
                1
            ]
            .div.text
            if teachers_rating_card.find(
                "div", class_="TeacherFeedback__StyledTeacherFeedback-gzhlj7-0 cxVUGc"
            ).findAll("div", class_="FeedbackItem__StyledFeedbackItem-uof32n-0 dTFbKx")
            else "Unknown"
        )

        teachers_rating_list = soup.find("ul", id="ratingsList").findAll("li")

        for li in teachers_rating_list:
            rating_card = li.find(
                "div", class_="Rating__RatingBody-sc-1rhvpxz-0 dGrvXb"
            )

            if rating_card:
                course = rating_card.find(
                    "div", class_="RatingHeader__StyledClass-sc-1dlkqw1-3 eXfReS"
                ).text
                date = rating_card.find(
                    "div",
                    class_="TimeStamp__StyledTimeStamp-sc-9q2r30-0 bXQmMr RatingHeader__RatingTimeStamp-sc-1dlkqw1-4 iwwYJD",
                ).text

                quality_num = "0.0"
                difficulty_num = "0.0"
                q_d_cards = rating_card.find(
                    "div", class_="RatingValues__StyledRatingValues-sc-6dc747-0 gFOUvY"
                ).findAll(
                    "div", class_="RatingValues__RatingContainer-sc-6dc747-1 DObVa"
                )
                q_card = q_d_cards[0]

                if q_card and q_card.div.div.text.lower() == "quality":
                    quality_num = q_card.div.findAll("div")[1].text

                d_card = q_d_cards[1]

                if d_card and d_card.div.div.text.lower() == "difficulty":
                    difficulty_num = d_card.div.findAll("div")[1].text

                if (
                    rating_card.find(
                        "div", class_="CourseMeta__StyledCourseMeta-x344ms-0 fPJDHT"
                    )
                    and rating_card.find(
                        "div", class_="CourseMeta__StyledCourseMeta-x344ms-0 fPJDHT"
                    ).div
                    and rating_card.find(
                        "div", class_="CourseMeta__StyledCourseMeta-x344ms-0 fPJDHT"
                    ).div.span
                ):
                    textbook = rating_card.find(
                        "div", class_="CourseMeta__StyledCourseMeta-x344ms-0 fPJDHT"
                    ).div.span.text
                else:
                    textbook = "No"

                if rating_card.find(
                    "div", class_="Comments__StyledComments-dzzyvm-0 gRjWel"
                ):
                    comment = rating_card.find(
                        "div", class_="Comments__StyledComments-dzzyvm-0 gRjWel"
                    ).text
                else:
                    comment = "No Comment"

                rating = {
                    "course": course,
                    "date": date,
                    "quality": quality_num,
                    "difficulty": difficulty_num,
                    "textbook": textbook,
                    "comment": comment,
                }
                ratings.append(rating)

    return ratings

@dataclass
class ProfInput:
    prof_link: str

@dataclass
class Rating:
    course: str
    date: str
    quality: str
    difficulty: str
    textbook: str
    comment: str

@app.post("/rating")
@validate_request(ProfInput)
@validate_response(list[Rating])
async def get_rating(data: ProfInput) -> list[Rating]:
    ratings = await get_teacher_info(data.prof_link)
    return ratings

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)