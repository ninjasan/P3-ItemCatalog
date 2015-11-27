# P3-ItemCatalog
Project 3 of Udacity Full Stack Web Developer nanodegree

Getting Started
    Pre-requisites
        1) Follow steps 1-3 from the project instructions
           https://www.udacity.com/course/viewer#!/c-nd004/l-3487760229/m-3631038670
            1) Install Vagrant and Virtual Box
            2) Clone the fullstack-nanodegree-vm repository
            3) Launch the Vagrant VM
        2) Create a sub-directory, locally, in the Vagrant directory
            1) Name it whatever you like
            2) Note: you can also put the files in the existing "catalog" directory. 
               But be careful to clean it out to make sure new files won't conflict 
               with existing files in the directory.
        3) Clone project files from:
           https://github.com/ninjasan/P3-ItemCatalog.git
           and place them the Vagrant sub-directory.
        4) SSH into the VM.
        5) Make sure dicttoxml is installed on the VM. Learn more here:
            https://pypi.python.org/pypi/dicttoxml/
        6) Navigate to the sub-directory where the project files are stored.
    Steps
        5) Optional: To start with the provided db, skip this step. However, if you want to 
           start with a clean database, you can rename vacation_catalog_wUsers.db to something
           else. That way a new, clean db will be created.
        5) Then run the following command in the VM commandline
            python application.py
        9) Open a browser and navigate to http://localhost:8000/
    Explore!
        10) Now that the site is up, feel free to explore!

What's included
    - application.py - contains main for application
    - vacation_catalog_wUsers.db - contains state of DB
    - this README.md
    - roadtrip (directory)
        - __init__.py - contains main app definition
        - api (directory)
            - __init__.py - initializes api module as a package
            - controllers.py - contains routes/logic for apis
        - auth (directory)
            - __init__.py - initializes auth module as a package
            - auth.py - contains logic for oauth authentication
            - client_secret.json - contains appid and secret for google sign-in
            - fb_client_secrets.json - contains appid and secret for facebook sign-in
            - templates (directory)
                - login.html - html content for the home page/login page
        - data (directory)
            - __init__.py - initializes data module as a package
            - dbsession.py - initializes session for app
            - models.py - contains schema definitions for the DB
        - main (directory)
            - __init__.py - initializes main module as a package
            - controllers.py - contains routes/logic for html access
            - helpers.py - contains logic for methods to support application
            - templates (directory)
                - about.html - html with the about page content
                - delete_activity.html - html content for deleting an activity
                - delete_city.html - html content for deleting a city
                - edit_activity.html - html content for editing an activity
                - edit_city.html - html content for editing a city
                - list_cities.html - html content to give the user the option to add cities
                                     using the public page as the foundation
                - list_cities_public.html - html content to list/display cities
                - new_activity.html - html content for adding a new activity
                - new_city.html - html content for adding a new city
                - show_activity.html - html content for edit and delete buttons/links,
                                       using the public page as the foundation
                - show_activity_public.html - html content to display an activity
                - show_city.html - html content for edit and delete buttons/links,
                                   using the public page as the foundation
                - show_city_public.html - html content to display a city
        - static (directory)
            - addnew_g.png - image used for adding new items
            - logo_v2.png - image representing the logo for the site
            - styles.css - css file containing formatting for the html pages
        - templates (directory)
            - base.html - html representing the foundation of all the pages on the site
            - error_403.html - html representing what is shown when a user runs into a 403
            - error_404.html - html representing what is shown when a user runs into a 404

Supported Features
    V1.1
        - CSRF protection added to add/edit city, and add/edit activity
            - To reduce repeated code, turned nonce check into decorator function
        - XML APIs to retrieve city and activity content
        - Edit pages now show actual values, instead of placeholders
        - Facebook login changed from dev mode, so now everyone should be able to login via Facebook, not just me.
        - DB schema now cascades on delete (instead of looping through items, like I had before)
    V1
        - Creates a database and tables to store users, cities, and activities to do in the cities
        - Allows user login/registration via Facebook and Google
        - Users that are not logged in can view the content on the site
        - Users that are logged in can view and create content on the site
          - For items the user created, they can also edit/delete them while logged in
          - Nonces in place to protect deleting via CSRF attacks
        - JSON APIs to retrieve city and activity content

Credits
    - Code help
        - The Udacity team (Oauth2.0 class and code)
        - Sticker Footer from Ryan Fait
        - CSRF Protection from Dan Jacob
        - Structuring Flask applications from Damyan Bogoev
    - Site content
        - Images
            - Login page background, Cities header background, About header background,
              Seattle's Discovery Park image
                - Pictures taken by me, Pooja Mathur
            - Wikimedia Commons - None of these items were altered for the use on this project.
                - Creative Commons Attribution 2.0 Generic License (https://creativecommons.org/licenses/by/2.0/deed.en)
                    - Nitobe Memorial Garden's image by Jennifer C. (https://commons.wikimedia.org/wiki/File:Nitobe_Memorial_Garden_1.jpg)
                    - Powell's City of Books' image by edward stojakovic (https://commons.wikimedia.org/wiki/File:Powell%27s_Books_entry.jpg)
                - Creative Commons Attribution-ShareAlike 2.0 Generic License (https://creativecommons.org/licenses/by/2.0/deed.en)
                    - Vancouver's image by Andrew Raun (https://commons.wikimedia.org/wiki/File:English_Bay_Vancouver.jpg)
                    - Museum of Anthropology's image by goldberg (https://commons.wikimedia.org/wiki/File:UBC_Museum_of_Anthropology_Building_(Vancouver).jpg)
                - Creative Commons Attribution-ShareAlike 3.0 Unported License (https://creativecommons.org/licenses/by-sa/3.0/deed.en)
                    - Seattle's image by Cacophony (https://commons.wikimedia.org/wiki/File:SeattleI5Skyline.jpg)
                    - Pike Place Market's image by Mtaylor444 (https://commons.wikimedia.org/wiki/File:Pike_Place_Market_Entrance.JPG)
                    - Hiram M. Chittenden Locks image by Joe Mabel (https://commons.wikimedia.org/wiki/File:Chittenden_Locks_overview_01.jpg)
                    - Space Needle's image by Cacophony (https://commons.wikimedia.org/wiki/File:SpaceNeedleQAHill.jpg)
                    - Stanley Park's image by Zotium (https://commons.wikimedia.org/wiki/File:Vancouver-stanley-park.jpg)
                    - Portland Japanese Garden's image by Adonelson (https://commons.wikimedia.org/wiki/File:Japanese_Garden_-1.jpg)
                - Creative Commons Attribution 3.0 Unported License (https://creativecommons.org/licenses/by/3.0/deed.en)
                    - Grouse Mountain's image by Ice-Babe (https://commons.wikimedia.org/wiki/File:GrouseMountain.jpg)
                - Images shared into the public domain
                <ul>
                    - H.R. MacMillan Space Centre's image by Bobanny (https://commons.wikimedia.org/wiki/File:Van_museum_space_centre.jpg)
                    - Granville Island's image by Zhatt (https://commons.wikimedia.org/wiki/File:Granville_Island.jpg)
                    - Portland's image by Jami Dwyer (https://commons.wikimedia.org/wiki/File:Portlandbridges.jpg)
                </ul>
            </ul>
        - Text descriptions of cities and activities
            <ul>
                - Seattle description: Visit Seattle website (http://www.visitseattle.org/)
                - Pike Place description: Pike Place website (http://www.pikeplacemarket.org/)
                - Space Needle description: Space Needle website (http://www.spaceneedle.com/hours-directions/)
                - Discovery Park description: Seattle City Parks website (http://www.seattle.gov/parks/environment/discovery.htm)
                - Vancouver description: Hello BC website (http://www.hellobc.com/vancouver.aspx)
                - Grouse Mountain description: Hello BC website (http://www.hellobc.com/activitylisting/4543334/grouse-mountain-resort.aspx)
                - Nitobe Memorial Garden description: Hello BC website (http://www.hellobc.com/activitylisting/4580326/nitobe-memorial-garden.aspx)
                - H.R. MacMillan Space Centre description: Hello BC website (http://www.hellobc.com/activitylisting/100005/h-r-macmillan-space-centre.aspx)
                - Stanley Park description: Tourism Vancouver website (http://www.tourismvancouver.com/do/activities-attractions/hiking/stanley_park_hiking/)
                - Granville Island description: Hello BC website (http://www.hellobc.com/activitylisting/4547354/granville-island.aspx)
                - Museum of Anthropology description: Hello BC website (http://www.hellobc.com/activitylisting/4542191/museum-of-anthropology.aspx)
                - Portland description: Wikipedia (https://en.wikipedia.org/wiki/Portland,_Oregon)
                - Portland Japanese Garden description: Travel Portland website (http://www.travelportland.com/article/portland-japanese-garden/)
                - Powell's City of Books description: Powell's website (http://www.powells.com/info/about-us)

Creators
    - Pooja Mathur
