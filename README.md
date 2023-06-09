# Automatic Scraper API
![Pe Viitor logo](https://peviitor.ro/static/media/peviitor_logo.df4cd2d4b04f25a93757bb59b397e656.svg)

This API will take care of scrapers in case any of them fail.

The Automatic Scraper API is a web service that allows you to automate the process of web scraping and file updating. With this API, you can run scrapers that collect data from various websites, and have those scrapers automatically update your files when changes are detected.

Only supports Python or JavaScript files

## API Endpoints 
The Automatic Scraper API provides the following endpoints:

### Add Scraper [`POST scraper/add/`](https://dev.laurentiumarian.ro/scraper/add/ "`POST scraper/add/`")

on Site

<img width="auto" alt="Screenshot 2023-05-07 at 12 28 47" src="https://user-images.githubusercontent.com/67306273/236669416-291958be-2c23-4940-aba0-9808a8405bbd.png">

or Bash script

```bash
curl -X POST -d '{"url":"https://github.com/your_repository.git"}' https://dev.laurentiumarian.ro/scraper/add/

```
Clone a GitHub repository

To ensure that the files can be read, you need to create a folder within the repository called "sites" and ensure that all files are stored in this folder. Also for dependencies you need the file "requirements.txt" for python or "packange.json" for Javascript in the root folder of the project

### Running a scraper `GET/POST scraper/your_github_repository/`

on Site

<img width="auto" alt="Screenshot 2023-05-07 at 13 01 29" src="https://user-images.githubusercontent.com/67306273/236670911-9ede6d3d-74a5-4512-823b-96a41c6a1a3b.png">

or Bash script

#### GET All files

```bash
curl -X GET https://dev.laurentiumarian.ro/scraper/your_repository_root_folder/
```

#### Run Scraper

```bash
curl -X POST -d '{"file":"your_file.extension"}' https://dev.laurentiumarian.ro/scraper/your_repository_root_folder/

```

#### Run Forced Scraper

```bash
curl -X POST -d '{"file":"your_file.extension","force":"true"}' https://dev.laurentiumarian.ro/scraper/your_repository_root_folder/

``` 

#### Running Tests

Each scraper includes a dedicated section for logging activities

[comment]: <> (image here)

This section allows you to review the results of the scraper's automated test. The test is separate from the scraper itself and can be implemented in any programming language.

##### Test endpoint

### Test Pass or Fail

```bash
curl -X POST -d '{"is_succes":"Fail or Pass", "logs":"your message"}' https://dev.laurentiumarian.ro/scraper/your_repository_root_folder/scraper.extension
```

This endpoint serves the purpose of sending test results to the scraper. A request is sent to the endpoint with two parameters: "is_success" and "logs." The "is_success" parameter is used to indicate the success or failure of the test. The "logs" parameter allows sending a custom message to the scraper. The scraper will display this message in the "Logs" section, providing visibility into the test execution process.

You can enhance the functionality by including a manual test feature with an "Add Test" button. When a test is added, the scraper's behavior can be controlled based on the test status. If the status is set to "Pass," the scraper will run automatically. On the other hand, if the status is marked as "Fail," the scraper will not run and will be deactivated.

[comment]: <> (image here)

Running a Scraper from the "sites" folder

### Update Files`POST scraper/your_github_repository/`

The function called "update" verifies whether there are any modifications in the primary branch and updates them if any changes are found.

on Site 

<img width="auto" alt="Screenshot 2023-05-07 at 13 14 38" src="https://user-images.githubusercontent.com/67306273/236671691-45dab3d1-9f6e-4ae3-927c-247adbf5e021.png">

or Bash script 

```bash
curl -X POST -d '{"update":"true"}' https://dev.laurentiumarian.ro/scraper/your_repository_root_folder/
```

### Remove Repository [`GET/POST scraper/remove/`](https://dev.laurentiumarian.ro/scraper/remove/ "`GET/POST scraper/remove/`")


The function named "remove" is responsible for completely deleting the repository from the server.

on Site

<img width="auto" alt="Screenshot 2023-05-07 at 13 30 18" src="https://user-images.githubusercontent.com/67306273/236672271-5fa2c717-f2f3-42ef-92b0-84a6477bf944.png">

or Bash script 

```bash
curl -X POST -d '{"repo":"your_repository_folder"}' https://dev.laurentiumarian.ro/scraper/remove/
```

## Contributions
If you want to contribute to the development of the scraper, there are several ways you can do so. Firstly, you can help develop the source code by adding new functionalities or fixing existing issues. Secondly, you can contribute to improving the documentation or translations into other languages. Additionally, if you want to help but are unsure where to start, you can check our list of open issues and ask us how you can help. For more information, please refer to the "Contribute" section in our documentation.

## Authors
 Our team is composed of a group of specialists and education enthusiasts who aim to make a significant contribution in this field.

- [peviitor team](https://github.com/peviitor-ro)

We are dedicated to the continuous improvement and development of this project, so that we can provide the best resources for everyone interested.
