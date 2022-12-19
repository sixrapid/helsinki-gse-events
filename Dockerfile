FROM python:3
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD main.py /
EXPOSE 80/tcp
CMD ["python", "./main.py"] 