# OpenAI Chatbot

This is a chatbot created using the OpenAI API, Flask and MySQL

## Prerequisites
| Dependency | Documentation | MacOS Installation |
| ------ | ------ | ----- |
| Venv | https://docs.python.org/3/library/venv.html | https://formulae.brew.sh/formula/virtualenv |
| Python 3.7 | https://docs.python.org/3.7/ | https://www.python.org/downloads/release/python-370/ |
| MySQL | https://dev.mysql.com/doc/ | https://formulae.brew.sh/formula/mysql |

## Installation
### Get python 3.7 using pyenv
```sh
brew update
brew isntall pyenv 
pyenv install 3.7
pyenv shell 3.7
```
> Useful links:
> * https://formulae.brew.sh/formula/pyenv
> * https://stackoverflow.com/questions/2547554/multiple-python-versions-on-the-same-machine 

### Get the virtual environment
```sh
pip3 install virtualenv
```
* or
```sh
brew install virtualenv
```
> Useful link:
> * https://formulae.brew.sh/formula/virtualenv
> * https://stackoverflow.com/questions/44158676/remove-virtual-environment-created-with-venv-in-python3

### Get MySQL
```sh
brew install mysql
```
> Useful link:
> * https://formulae.brew.sh/formula/mysql

## Setup
* Create the virtual environment using python 3.7
```sh
python3 -m -venv env
```
### Start the virtual environment
* On MacOS (Option 1)
```sh
source env/bin/activate
```
* On Windows
```sh
venv\Scripts\activate.bat
```
* On MacOS (Option 2), Linux or Windows Git Bash
```sh
source venv/Scripts/activate
```
### To get out from the virtual environment
```sh
deactivate
```
### Install the requirments
```sh
pip install -r requirements.txt
```
## Create the data base
Used for users management and chat recording
### Start mysql
```sh
brew services start mysql
```
* To stop it
```sh
brew services stop mysql
```
### Enter mysql
```sh
mysql -u root
```
* To get out from mysql
```sh
quit();
```
### Create the dabase
```sh
create database chatbot;
```
### Get in the chatbot database
```sh
use chatbot
```
### Create the users table
```sh
CREATE TABLE `users` (
    `id` int(11) NOT NULL,
    `name` varchar(100) NOT NULL,
    `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `users`
    ADD PRIMARY KEY (`id`);

ALTER TABLE `users`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
```
### Create the chats table
```sh
CREATE TABLE `chats` (
  `id` varchar(100) NOT NULL,
  `question` varchar(255) NOT NULL,
  `answer` LONGTEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
## Add the environment variables
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_DB=chatbot
SECRET_KEY=<Any random string>
API_KEY=<Your OpenAI API for gpt-3.5-turbo key>
```

## Start the program
```sh
python3 main.py
```

Go to your web browser and open your `localhost:4000`.
Enjoy it!
