## Flask-Feedback

an application that lets users sign up and log in to their own accounts. Once logged in,   
users can add feedback, edit their feedback, delete their feedback, and see a list of   
all feedback that they’ve given. User can register/update his/her password. It is also  
possible to register as an administrator. It will give one ability to delete any feedbacks  
etc
 
Technologies used in the project:

- Flask - WTForms  
- flask-bcrypt for encrypting passwords for security  
- OOP Models for PostgreSQL  
- Mail: to change password you will be prompt to enter your email in order to  
receive confirmation link. Then and only then you can reset your password  

To get this application running, make sure you do the following in the Terminal:
1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`




