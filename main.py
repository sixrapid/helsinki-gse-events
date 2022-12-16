import requests
import warnings
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from pathlib import Path

# Create calendar
ical = Calendar()

# Get events page and load to BeautifulSoup
url = "https://www.helsinkigse.fi/events/"
html = requests.get(url, verify = True)
soup = BeautifulSoup(html.text, "html.parser")

# Iterate through events listed in page
for a in soup.find_all("a", class_ = "u-url"):

    # Initialize dict for event
    event = dict()

    # Extract url for event and load to BeautifulSoup
    event["url"] = a["href"]
    event_html = requests.get(event["url"], verify = True)
    event_soup = BeautifulSoup(event_html.text, "html.parser")

    # Title and description
    event_header = event_soup.find("header", class_ = "page-header container max-width-lg")
    event["title"] = event_header.h1.string.strip()
    event["subtitle"] = event_header.h2.string.strip()
    event["description"] = event_soup.find("div", class_ = "intro").text.strip()

    # Loop through event items
    for item in event_soup.find_all("li", class_ = "details-card__list-item"):

        try:
            item_elems = item.div.find_all()
            item_name = item_elems[0].text.strip()
            item_content = item_elems[1].text.strip()
        except:
            warnings.warn("Item with content ", item, "could has less than 2 elements -- skipping.")
            continue

        if item_name == "Date:":
            event["date"] = datetime.strptime(item_content, "%d %b %Y")
        elif item_name == "Time:":
            event["start_time"] = datetime.strptime(item_content[0:5], "%H:%M")
            event["end_time"] = datetime.strptime(item_content[-5:], "%H:%M")
        elif item_name == "Organizer:":
            event["organizer"] = item_content
        elif item_name == "Type:":
            event["type"] = item_content
        elif item_name == "Location:":
            event["location"] = item_content

    # Create iCal Event
    ical_event = Event()

    event_name_str = event["type"] + ": " + event["title"] + " (" + event["subtitle"] + ")"

    ical_event.add("name", event_name_str)
    ical_event.add("X-WR-CALNAME", event_name_str)
    ical_event.add("summary", event_name_str)
    ical_event.add("description", event["description"])
    ical_event.add("X-WR-CALDESC", event["description"])
    ical_event.add("url", event["url"])

    if "location" in event:
        ical_event.add("location", event["location"])

    if ("start_time" in event) and ("end_time" in event):
        ical_event.add("dtstart", datetime.combine(event["date"].date(), event["start_time"].time()))
        ical_event.add("dtend", datetime.combine(event["date"].date(), event["end_time"].time()))
    else:
        ical_event.add("dtstart", event["date"])
        ical_event.add("dtend", event["date"] + timedelta(days = 1))

    ical.add_component(ical_event)

f = open("helsinki-gse-events.ics", "wb")
f.write(ical.to_ical())
f.close()
