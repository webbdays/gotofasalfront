# GotoFasal front and back

gotofasalfront is an open source code that makes it easy to search movies and collect the fav movie cards.

Website Link: [Movie Cards website](https://gotofasalfront.vercel.app/)


Licence: MIT

### Download and Install

#### Run From Source

* Visit https://github.com/webbdays/gotofasalfront and get the latest source code
* Install the python dependencies with poetry or pip
* cd to root directory and Run flask app with the command `flask run`
* Grab the displayed url like for example (localhost:3000) and open in the browser and one can then see the website running there.

#### Example Usage of the website
* User need to register (verify their email) and login.
* Loggined user can perform movie search and collect fav cards.
* Users fav cards are displayed in the profile page.
* Search functionality is based on the api from OMDB

#### Tech stack
* Programming languages Used: Python,  JavaScript, HTML, little bit CSS
* API is implemented via flask routes (But, I have initially implemented the api in golang, here it is: https://github.com/webbdays/gotofasal)
* Authentication(Login): Using Email, Password. (Not sure whether its is secure or not right now. Need to analyse in deep for any security issues.)
* For subsequent authentication after login, JWT tokens are used with expiry set to around 30 min as of now.
* Auth packages: Used bcrypt (for password hashing), pyjwt (for jwt token encoding and decoding).
* Database : Used Mongodb. To store user data like credentials and fav movies. Reason: Seems obvious for website data that was being handled.
* Host : Hosted on vercel. Website Link: [Movie Cards website](https://gotofasalfront.vercel.app/)
* 


### More details
#### About search functionality
* Used pythons asyncio module to make async requests to the OMDB api.
* This helps in avoiding blockage of the python script to perform next request.
* As a result webpage loads relatively fast.

#### Thanks for OMDB movie collection api
* Thanks for the api


### Contributing

I welcome any type of contribution to this code base.
To contribute, please read the contribution guidelines at (yet to add contributing guide lines)

[cc3-by]: https://creativecommons.org/licenses/by/3.0/
