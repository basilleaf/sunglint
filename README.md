Code for http://sunglint.tumblr.com/

launch.py grabs a random image from the dataset, posts the image+metadata to the tumblr blog, and then updates the list of published images - a file on S3.  

Dataset comes from manual search form submits at http://ntrs.nasa.gov and stored in a google spreadsheet: 
https://docs.google.com/spreadsheet/ccc?key=0AtHxCskz4p33dEhBZ3Jpc1VoTmIzQ0V3ODJ5eVdzcUE

The script runs 2 or more times/day from Heroku with the Scheduler add-on. 