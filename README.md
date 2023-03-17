## Student Management API

### This is a RESTful API for a student management system. The API allows for the management of student data, including personal information and academic records. It can be used as backend for a student management system or any other application that requires management of student's data.

### API Overview <br>

<ul>

#### <li> Authentication </li>
The API uses JWT-based authentication and authorization mechanism to ensure that only authorized users can access protected endpoints. Each request must include a valid access token in the authorization header. This access token is obtained by logging in a user via the `auth/login/` endpoint. The API checks the validity of this token before processing the request.


#### <li> Authorization </li>
The API supports role-based authorization. It restricts access to certain endpoints and operations based on the roles assigned to users. Upon account creation, every user is assigned a role and this role is stored in the JWT token. The role defines what actions the user is allowed to perform within the system.   
The roles includes; _**student**_, **_staff_** and **_admin_**.
The admins have overall access to almost every endpoint.

#### <li> Admin only operations </li>
Some endpoints and operations are only limited to users with admin role as they are users who actually manage the API.  Some of these operations includes;
<ul>
  <li> Creating new accounts for students and teachers </li>
  <li> Generating school ID for students </li>
  <li> Creating and updating courses </li>
  <li> Updating of student or teacher's information </li>
  <li> Deleting a student, teacher or course, etc. </li>
</ul>

<br>
When teachers or students accounts are created by the admin, a default password is set. Students can then use the generated school ID and teachers their email address to log in.


#### <li> Student related operations </li>
Operations that are open to the students who are the primary users of the API are;
<ul>
    <li> Viewing their profile  </li>
    <li> Retrieving a course to view it's details</li>
    <li> Register/enroll for a particular course/courses </li>
    <li> View their grade in all their registered courses and also their CGPA, etc. </li>
</ul>

#### <li> Teacher related operations </li>
<ul>
  <li> View their profile and the course they're handling </li>
  <li> Grade a student in the course they are registered to. </li>
</ul>
</ul>
 

### API Documentation & Usage
A comprehensive and interactive swagger documentation of the API can be accessed at _[https://altacad.pythonanywhere.com](https://altacad.pythonanywhere.com)._ It provides detailed information about all the available endpoints and their parameters. <br> <br>
To use the API;
1. Open your browser to the link above
2. Create an admin account using the `admin/signup/` endpoint.
3. Go to the `auth/login/` endpoint and log in using the email address and password you provided upon signing up and an access token and refresh token would be returned </li>
4. Copy the access token, click on the **_Authorize_** tab on the top right and paste the token in this format:

```
Bearer this12312is98923a9384398random994559ytoken 
```
5. Click on **_Authorize_** and then **_Close_**. You are now authorized to carry out any operation. Create account for students, teachers, create courses, update and even delete them. 


You can also test and use the API using tools like Postman, Insomnia etc.

### Conclusion 
This project was as an exam project from _[Altschool Africa](https://altschoolafrica.com)_ backend engineering track.



