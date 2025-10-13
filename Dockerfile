FROM openjdk:8-jdk-alpine

RUN apk --no-cache add git
RUN wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-5.4.1.tgz && \
    tar -xzf apache-jmeter-5.4.1.tgz -C /opt && \
    rm apache-jmeter-5.4.1.tgz

ENV PATH="/opt/apache-jmeter-5.4.1/bin:${PATH}"

# for local environment
WORKDIR /scraper_Api

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"


