## Khod Fekra

Khod Fekra is an automated Twitter account which collects best deals from different online stores and posts tweets about them without any human interfering. It built with Python, Selenium and Gecko Driver.

## Take a Look

Follow Us [@KhodFekraStore](https://twitter.com/KhodFekraStore)

## Learn 

I made an online course to demonstrate how I made this as a good example to explain Python-Selenium [in Arabic].

[YouTube Course](https://www.youtube.com/playlist?list=PLvLvlVqNQGHD1XUJSYfYezvs9gLdaWHId)

## Automate Your Own Account

1. Edit `config.py` to set your configurations.
2. You have to provide a Mongo DB connection. Ask [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) to give you a free one.
3. Install Python 3.6 or later using [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
4. Install the required dependencies

`conda install selenium dnspython pymongo`

5. Run `jumia.py` to collect last deals from Jumia online stores.
6. Run `twitter.py` to post tweets about the collected deals. You will set your Twitter account credentials in the `config.py` file.