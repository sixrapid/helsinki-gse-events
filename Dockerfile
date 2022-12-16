FROM python:3.9
ADD main.py .
RUN pip install requests beautifulsoup4 icalendar
CMD ["python", "./main.py"] 