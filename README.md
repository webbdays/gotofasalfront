# GotoFasal front and back

gotofasalfront is an open source code that makes it easy to search movies and collect the fav movie cards.

![Movie Cards website]()


Licence: MIT

### Download and Install

#### Run From Source

* Visit https://github.com/webbdays/gotofasalfront and get the latest source code
* Install the python dependencies with poetry or pip
* cd to root directory and Run flask app with the command `flask run`
* Grab the displayed url like for example (localhost:3000) and open in the browser and one can then see the website running there.

#### Example Usage of the website
* User need to register and login to perform movie search and for collecting fav cards
* Users fav cards are displayed in the profile page.
* Search functionality is based on the api from OMDB

#### Tech stack
* Programming languages Used: Python, Js, html, css
* API is implemented via flask routes (I have initially thought of implementing the api in golang, here it is: https://github.com/webbdays/gotofasal)
* Authentication: Email,Password. (Not secure right now. Need to analyse in deep of any security issues.)
* For subsequent authentication after login, JWT tokens are used with expiry set to around 30 min as of now.
* Auth packages used: bcrypt, pyjwt.
* Database : Used Mongodb. To store user data like credentials and fav movies.
* Host : Not yet Done. But currently able to host privately on gitpod.io workspace website. Will temp host there and get the public links for temp time.
* 

### Contributing

I welcome any type of contribution to this code base.
To contribute, please read the contribution guidelines at (yet to add contributing guide lines)

[cc3-by]: https://creativecommons.org/licenses/by/3.0/
