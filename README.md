# Project Description: Belay (a Slack clone)
### Yongfei Lu


### Introduction

As a capstone project for Web Development, we're going to combine the various
front-end and back-end techniques we've learned over the course to produce a
modern, database-backed single-page application. Specifically, we'll be building
our own (significantly smaller in scope) version of the popular workplace
messaging app Slack. We'll call our version [Belay](https://en.wikipedia.org/wiki/Belaying).

### Configuration

1. install all needed packages

`pip install -r requirements.txt`

2. local database configuration

- change your directory path with  `cd /belay/db_config `
- create the database and tables with `mysql -u root -p < *.sql`

3. secrets.cfg configuration

- change the values of DB_NAME, DB_USERNAME, DB_PASSWORD,SENDGRID_API_KEY in `secrets.cfg`

3. run the following code to start the project on port 5000

`flask run`


### Demo

#### Login Page
![img](https://github.com/ruixili/Belay/blob/master/demo/LoginPage.png)
#### Forget Password Page
![img](https://github.com/ruixili/Belay/blob/master/demo/ForgetPassword.png)
#### Sign Up Page
![img](https://github.com/ruixili/Belay/blob/master/demo/RegisterNewAccount.png)
#### Chat Page
![img](https://github.com/ruixili/Belay/blob/master/demo/ChatPage.png)
#### Create New Channel
![img](https://github.com/ruixili/Belay/blob/master/demo/CreateNewChannel.png)
#### Thread Message
![img](https://github.com/ruixili/Belay/blob/master/demo/Thread.png)


### Functions

- Belay lets users send and read real-time chat messages that are organized
  into rooms called Channels. Users see a list of all the channels on the server
  and can click one to enter that channel. Inside, they see all the messages
  posted to that channel by any user, and can post their own messages.
  All messages belong to a channel and all channels are visible to all users; we
  don't need to implement private rooms or direct messages.
- Channel names are unique strings of numbers, letters, and underscores (and no
  spaces). Any user can create a new channel, and the user who created a channel
  can delete it and all messages.
- Like Slack, messages may be threaded as Replies in response to a message in a
  channel. Messages in the channel will display how many replies they have if
  that number is greater than zero. Like in Slack, clicking will open the reply
  thread alongside the current messages in the channel, changing the screen from
  a 2-column layout to a 3-column layout. We don't support nested threads;
  messages either belong directly to a channel or are replies in a thread to a
  message that does, but replies can't have nested replies of their own.
- Like Slack, if a message contains any URLs that point to [valid image formats](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#Supported_image_formats),
  display the images in the chat at the bottom of the message. Unlike Slack,
  we won't support uploading images from the user's computer.
- The channel display shows the number of unread messages in each channel (so
  somewhere you'll have to track the id of the most recent message a user has
  seen in each channel).
- Belay should use responsive styling to render reasonably in a phone browser.
  In particular, on mobile devices, when a user is not in a channel they should
  see the list of channels, and when they are in a channel or in a thread they
  should see just the messages in that channel or thread, with some menu element
  to let them return to the channel list.
- Users should have a display name and an email address, and be able to update
  either in the app. Users authenticate with their email address and a password.
- Belay is a single-page web application. We serve a single HTML request on load
  and do not refresh the page. As users navigate to a channel, the application
  updates the navigation bar to reflect what channel they are in, and navigating
  to the URL for a specific channel opens the single-page application with that
  channel open. You may use Flask's `render_template` to render the page if
  desired.
- Belay automatically sends non-blocking requests to the server to check for new
  channels and new messages in a channel. Like Slack, when it finds new messages
  in a channel, it displays a notification to users in that channel without
  moving the existing messages on the page. Users may click on the notification
  to load the new messages.
- Other than loading the initial page, all interaction with the Belay server is
  handled via JSON API requests. This includes authenticating users, retrieving
  channels and messages, and creating new channels and messages. These requests
  are served by a Flask API.
- All data about users, channels, and messages is stored in a MySQL database. In
  your submission, include a SQL file of commands that can be run to create the
  database and its tables, like [this file](https://mit.cs.uchicago.edu/trevoraustin/mpcs-52553-austin/blob/master/week_8/examples/posts_and_comments/2020-02-24T18:45:00-create_database.sql)
  from Week 3. Start the names of your migration files with [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601)
  datetimes so that graders can run them in order. Make sure when you create
  your database to set it up to handle unicode characters with `CHARACTER SET
  utf8mb4 COLLATE utf8mb4_unicode_ci;`
- You don't need to implement Slack features not listed here, like @-mentioning
  users, avatars, rich text or the like. If you have any questions about what is
  in scope, please ask on the [course Slack](https://app.slack.com/client/T71CT0472/CSE1ZK67N).


### Features

Database (mySQL)
- Create databases and tables with migrations in version control
- Tables for channels, messages, and users
- Store passwords securely by hashing them with bcrypt
- Model the replies_to relationship
- Efficiently store last read message per channel per user

API
- Login endpoint
- Authenticate to other endpoints via session token in request body (not as a URL param)
- Endpoints to create and get channels and messages
- Get new message counts by channel without fetching all the message contents

Responsive Layout
- Login and password reset flows
- Show channels, messages, and replies (when shown) in 3-column grid
- Show/hide threaded replies
- On narrow screens, one-column layout with menu bar (2 points)

Single-Page State
- Only serve one HTML request
- Push channel and thread location to the navigation bar
- Track last read message per channel

Asynchronous Request Handling
- Continuously poll for new messages
- Show new message counts per channel
- Click-to-show new messages in a channel

### In this project, I consulted the following resources:

1. Extracting for URL from string using regex:
    https://stackoverflow.com/questions/31760030/extracting-for-url-from-string-using-regex

2. ParentNode.prepend():
    https://developer.mozilla.org/zh-CN/docs/Web/API/ParentNode/prepend

3. Update React component every second:
    https://stackoverflow.com/questions/39426083/update-react-component-every-second

4. RESTful Services Part I : HTTP in a Nutshell:
   https://www.freecodecamp.org/news/restful-services-part-i-http-in-a-nutshell-aab3bfedd131/

5. URLSearchParams:
    https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams

6. Storage.clear():
    https://developer.mozilla.org/en-US/docs/Web/API/Storage/clear

7. How to get browser width using JavaScript code?:
    https://stackoverflow.com/questions/1038727/how-to-get-browser-width-using-javascript-code

8. How to delete a localStorage item when the browser window/tab is closed?:
    https://www.tutorialspoint.com/how-to-delete-a-localstorage-item-when-the-browser-window-tab-is-closed

9. Number of columns according to screen size - with fluid column width [closed]:
    https://stackoverflow.com/questions/24135964/number-of-columns-according-to-screen-size-with-fluid-column-width

10. Usage of !important:
    https://www.jianshu.com/p/3d1b4a58c3ef:

11. Javascript overriding CSS display property after change of media query:
    https://stackoverflow.com/questions/46054334/javascript-overriding-css-display-property-after-change-of-media-query

12. CSS media queries and !important
    https://stackoverflow.com/questions/10262082/css-media-queries-and-important/19703165
