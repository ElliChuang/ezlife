# EzLife

EzLife is a shared account book that supports expense analysis and financial settlement for family and friends who live or travel together to easily keep track of expenses.

Website URL : <https://ezchat-ezlife.com>\
Test **account** and **password** :

    1. test@mail.com / test123
    2. coEdit@mail.com / coEdit123

## Demo

- Supports multi-condition filtering for analyzing expenses and exporting as CSV files.

  ![Image showing analysis](/readme/analysis.gif)

- Easy account settlement at your fingertips and access your records anytime!

  ![Image showing settlement](/readme/settlement.gif)

## Catalog

- [Main Features](#main-features)
- [Backend Technique](#backend-technique)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [Frontend Technique](#frontend-technique)
- [API Doc](#api-doc)
- [Contact](#contact)

## Main Features

- Memebr System
  - User can sign in locally or with Google account (OAuth2.0).
  - User authentication with JSON Web Token.
- Shared Account Book
  - Use Socket.IO for real time co-editing.
  - Invite your friend with email.
- Analyze and Export as CSV file
  - Supports multi-condition filtering for analyzing.
  - Exports expenses as CSV file.
- Financial Settlement
  - User can settle their account easily at their fingertips and access their records anytime.

## Backend Technique

- Deployment
  - Docker
- Language / Web Framework
  - Python / Flask
- Database
  - MySQL
  - Redis
- AWS Cloud Service
  - EC2
  - RDS
  - ElastiCache
  - S3
  - CloudFront
- Networking
  - HTTP & HTTPS
  - Domain Name System (DNS)
  - Nginx
  - SSL (Let's Encrypt)
- Third Party Library
  - Google OAuth 2.0
  - Loader.io
- Version Control
  - Git / GitHub
- Key Points
  - Socket.IO
  - MVC Pattern
  - RESTful API

## Architecture

- ### Server Architecture

  ![Image showing sever architecture](/readme/Server_Architecture.png)

- ### Socket Architecture

  ![Image showing socket architecture](/readme/Socket_Architecture.png)

- ### Cache Architecture

  ![Image showing redis architecture](/readme/Redis_Architecture.png)

## Database Shema

![Image showing database](/readme/database.png)

## Frontend Technique

- JavaScript
- HTML
- CSS
- AJAX
- Third Party Library
  - Chart.js
  - FullCalendar

## API Doc

[API Doc](https://app.swaggerhub.com/apis-docs/ELLI8208/EzLife/1.0.0#/)

## Contact

:bust_in_silhouette: 莊霈虹 Pei Hung Chuang \
:email: Email : elli8208@gmail.com
