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

## Contribuie
Dacă dorești să contribui la dezvoltarea scraperului, există mai multe modalități prin care poți face acest lucru. În primul rând, poți ajuta la dezvoltarea codului sursă prin adăugarea de noi funcționalități sau prin remedierea de probleme existente. În al doilea rând, poți contribui la îmbunătățirea documentației sau a traducerilor în alte limbi. În plus, dacă dorești să ajuți și nu ești sigur cum să începi, poți verifica lista noastră de probleme deschise și să ne întrebi cum poți ajuta. Pentru a obține mai multe informații, te rugăm să consulți secțiunea "Contribuie" din documentația noastră.

## Autori
 Echipa noastră este formată dintr-un grup de specialiști și entuziaști ai educației, care își doresc să aducă o contribuție semnificativă în acest domeniu. 

- [peviitor team](https://github.com/peviitor-ro)

Suntem dedicați îmbunătățirii și dezvoltării continue a acestui proiect, astfel încât să putem oferi cele mai bune resurse pentru toți cei interesați.
