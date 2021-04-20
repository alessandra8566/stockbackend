FROM python:3.8.2
WORKDIR /stockBack
COPY . /stockBack
# RUN python -m pip install --upgrade pip && pip install pipenv
RUN python -m pip install --upgrade pip && pip install -r requirements.txt && pip install uwsgi
# RUN pipenv install --system --deploy --ignore-pipfile && pip install uwsgi
# RUN pipenv shell
EXPOSE 80
# CMD ["uwsgi", "--http", "0.0.0.0:80", ,"--callable", "app", "--wsgi-file", "app.py"]
# CMD ["uwsgi", "config.ini"]
CMD ["python", "app.py"]
# CMD ["pipenv", "run", "python3", "app.py"]