Code for http://sunglint.tumblr.com/

launch.py grabs a random image from the google spreadsheet, posts the image+metadata to the tumblr blog, and then updates the list of published images (a text file on S3).  

Dataset comes from manual search form submits at http://ntrs.nasa.gov and stored in this google spreadsheet: 
https://docs.google.com/spreadsheet/ccc?key=0AtHxCskz4p33dEhBZ3Jpc1VoTmIzQ0V3ODJ5eVdzcUE

The script runs 2 or more times/day on Heroku with the Scheduler add-on. 