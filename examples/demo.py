"""Demonstration of the scholarship automation framework using an in-memory driver."""
from __future__ import annotations

import asyncio

from scholar_automation import (
    ApplicationNavigator,
    AutomationController,
    FormInteractor,
    PageUnderstandingEngine,
    ScholarshipDiscoveryEngine,
    SubmissionManager,
    TransparencyLogger,
    UserProfile,
)
from scholar_automation.drivers import FakePage, InMemoryDriver
from scholar_automation.page_understanding import PageElement


async def main() -> None:
    profile = UserProfile(
        name="Ada Lovelace",
        email="ada@example.com",
        phone="555-0100",
        gpa=3.9,
        major="Computer Science",
        school="Analytical Engine University",
        metadata={"leadership": "Student Council"},
    )

    pages = {
        "https://start": FakePage(
            url="https://start",
            text="STEM Scholars Program\nEligibility: Computer Science majors",
            links=[("#apply", "https://application")],
            elements=[
                PageElement(selector="#apply", role="button", text="Apply"),
            ],
        ),
        "https://application": FakePage(
            url="https://application",
            text="Scholarship Application Form",
            links=[],
            elements=[
                PageElement(selector="#input-name", role="input", text="Name"),
                PageElement(selector="#input-email", role="input", text="Email"),
                PageElement(selector="#input-major", role="input", text="Major"),
                PageElement(selector="#essay-purpose", role="textarea", text="Essay prompt: Describe your goals."),
            ],
        ),
    }

    driver = InMemoryDriver(pages=pages, start_url="https://start")
    logger = TransparencyLogger()
    understanding = PageUnderstandingEngine()
    navigator = ApplicationNavigator(driver=driver, understanding=understanding, logger=logger)
    discovery = ScholarshipDiscoveryEngine(driver=driver, logger=logger, seeds=["https://start"])
    forms = FormInteractor(driver=driver, logger=logger)
    submissions = SubmissionManager(logger=logger)
    controller = AutomationController(
        profile=profile,
        discovery=discovery,
        navigator=navigator,
        form_interactor=forms,
        submissions=submissions,
        logger=logger,
    )

    await controller.run()
    await submissions.submit_all()

    for event in logger.events:
        print(f"[{event.timestamp:%H:%M:%S}] {event.message} {event.context}")


if __name__ == "__main__":
    asyncio.run(main())
