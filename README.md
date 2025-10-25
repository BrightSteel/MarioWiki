# Module 1 Group Assignment

CSCI 5117, Spring 2023, [assignment description](https://canvas.umn.edu/courses/355584/pages/project-1)

## App Info:

* Team Name: The Internet Explorer
* App Name: Mario-wiki
* App Link: https://mario-wiki-rs18.onrender.com/

### Students

* Zachary Champlin champ169 
* Ryan Exner exner014
* Yiling Tan tan00250
* Cedric Tan tan00205
* Nico Paredes pared055


## Key Features

**Describe the most challenging features you implemented
(one sentence per bullet, maximum 4 bullets):**

* Posts. 
1. Logged in users: users can create and like discussion and wiki posts, users can also comment discussion posts. Every user can edit wiki posts but only the post creator can delete wiki post. Each wiki post has a thumbnail, user can upload their own thumbnail or use our default thumbnail. 
2. Visitors: can view wiki posts and discussion posts, can't comment, edit, delete, or like. 
  Each discussion post has the information about the creator and the post's category, user can click to see creator's profile or the category page.
* Search. Everyone can search, whether logged in or not. 
The search page: User enter input and all related posts will show up, they can also select different filters to choose search results. On the bottom of each page, there are wiki posts[with their thumbnails] from A-Z, user can click on that and they will be directed to the target post.
* Account. Each user signup/login through Auth0, they will have a profile page when they signup. User can update their personal profile[profile photo and bio], view and remove their followers in their profile page, and follow other users. They can only view other user's profile. User's personal profile can be accessed through the drop down bar on the upper right of the page, or through the author name in each post.
  Visitors can only view users's profile.
* We implemented some responsive design styles to our pages so they look good on smaller screens.

## Testing Notes

**Is there anything special we need to know in order to effectively test your app? (optional):**

* Our project is using python 3.8.10


## Screenshots of Site

**[Add a screenshot of each key page (around 4)](https://stackoverflow.com/questions/10189356/how-to-add-screenshot-to-readmes-in-github-repository)
along with a very brief caption:**
* our homepage: shows the recent wiki posts
![](https://project50017.s3.us-east-2.amazonaws.com/screenshots/homepage.png)
* our search page, showing results for the input "luigi"
![](https://project50017.s3.us-east-2.amazonaws.com/screenshots/IMG_2016.jpg)
* our community feed/discussion page
![](https://project50017.s3.us-east-2.amazonaws.com/screenshots/IMG_2017.jpg)
* our profile page: logged in users
![](https://project50017.s3.us-east-2.amazonaws.com/screenshots/profile.png)
* our bottom quick access"
![](https://project50017.s3.us-east-2.amazonaws.com/screenshots/Quick+access.png)

## Mock-up 

There are a few tools for mock-ups. Paper prototypes (low-tech, but effective and cheap), Digital picture edition software (gimp / photoshop / etc.), or dedicated tools like moqups.com (I'm calling out moqups here in particular since it seems to strike the best balance between "easy-to-use" and "wants your money" -- the free teir isn't perfect, but it should be sufficient for our needs with a little "creative layout" to get around the page-limit)

In this space please either provide images (around 4) showing your prototypes, OR, a link to an online hosted mock-up tool like moqups.com

**[Add images/photos that show your paper prototype (around 4)](https://stackoverflow.com/questions/10189356/how-to-add-screenshot-to-readmes-in-github-repository) along with a very brief caption:**
* updated version
![](https://project50017.s3.us-east-2.amazonaws.com/screenshots/IMG_1995.jpg)
![](https://project50017.s3.us-east-2.amazonaws.com/screenshots/IMG_2010.jpg)
![](https://project50017.s3.us-east-2.amazonaws.com/screenshots/IMG_2009.jpg)
![](https://project50017.s3.us-east-2.amazonaws.com/screenshots/IMG_1997.jpg)
* previous version
![](https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif)
![](mockup_images/home.png?raw=true)
![](mockup_images/community_feed.png?raw=true)
![](mockup_images/category.png?raw=true)
![](mockup_images/post.png?raw=true)
![](mockup_images/profile.png?raw=true)
![](mockup_images/search.png?raw=true)

## External Dependencies

**Document integrations with 3rd Party code or services here.
Please do not document required libraries. or libraries that are mentioned in the product requirements**

* Library or service name: description of use
* html-sanitizer : filters potentially dangerous or unwanted content from HTML documents.
* boto3 : access the aws s3 bucket
* htmlparser: for our search feature, parsing HTML documents and to extract information from HTML documents

**If there's anything else you would like to disclose about how your project
relied on external code, expertise, or anything else, please disclose that
here:**

...
