# P3-ItemCatalog
Project 3 of Udacity Full Stack Web Developer nanodegree

Getting Started
    Pre-requisites
        1) Follow steps 1-3 from the project instructions
           https://www.udacity.com/course/viewer#!/c-nd004/l-3487760229/m-3631038670
            1) Install Vagrant and Virtual Box
            2) Clone the fullstack-nanodegree-vm repository
            3) Launch the Vagrant VM
    Steps
        2) Create a sub-directory, locally, in the Vagrant directory
            1) Name it whatever you like
            2) Note: you can also put the files in the existing "catalog" directory. 
               But be careful to clean it out to make sure new files won't conflict 
               with existing files in the directory.
        3) Clone project files from:
           https://github.com/ninjasan/P3-ItemCatalog.git
           and place them the Vagrant sub-directory.
        4) After SSH-ing into the VM, navigate to the sub-directory where the
           files are stored.
        5) Optional: To start with the provided db, skip this step. However, if you want to 
           start with a clean dataabase, you can temporarily rename vacation_catalog_wUsers.db 
           and then run the following command in the VM commandline:
            python database_setup.py
        5) Then run the following command in the VM commandline
            python application.py
        9) Open a browswer and navigate to http://localhost:8000/
    Explore!
        10) Now that the site is up, feel free to explore!

What's included
    - application.py - contains APIs and functions to help client interact with the db
    - database_setup.py - contains schema definitions for the DB
    - client_secret.json - contains appid and secret for google sign-in
    - fb_client_secrets.json - contains appid and secret for facebook sign-in
    - vacation_catalog_wUsers.db - contains state of DB
    - this README.txt
    - static (directory)
      - addnew_g.png - image used for adding new items
      - logo_v2.png - image representing the logo for the site
      - styles.css - css file containing formatting for the html pages
    - templates (directory)
      - base.html - html representing the foundation of all the pages on the site
      - about.html - html with the about page content
      - delete_activity.html - html content for deleting an activity
      - delete_city.html - html content for deleting a city
      - edit_activity.html - html content for editing an activity
      - edit_city.html - html content for editing a city
      - list_cities.html - html content to list/display cities
      - login.html - html content for the home page/login page
      - new_activity.html - html content for adding a new activity
      - new_city.html - html content for adding a new city
      - show_activity.html - html content for edit and delete buttons/links, 
                             using the public page as the foundation
      - show_activity_public.html - html content to display an activity
      - show_city.html - html content for edit and delete buttons/links, 
                         using the public page as the foundation
      - show_city_public.html - html content to display a city

Supported Features
    - Creates a database and tables to store users, cities, and activities to do in the cities
    - Allows user login/registration via Facebook and Google
    - Users that are not logged in can view the content on the site
    - Users that are logged in can view and create content on the site
      - For items the user created, they can also edit/delete them while logged in
      - Nonces in place to protect editing/deleting via CSRF attacks
    - JSON APIs to retrieve city and activity content

Credits
    - The Udacity team (Oauth2.0 class and code!)
    - All the images and text for the cities (see about page for all the links)

Creators
    - Pooja Mathur
