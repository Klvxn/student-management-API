## Student Management API

### This is a REST API  for a school's student management system built with Flask and Flask-restx
### It includes endpoints for <br>


* #### JWT Authentication

* #### Admin only operations
  1. Sign up 
  2. Create accounts for students and generate school ID for them
  3. Create accounts for teachers with their email address and full name
  4. Create and update courses
  5. Update student or teacher's information
  6. Get all students, teachers and courses
  7. Delete a student, teacher or course, etc.


When teachers or students accounts are created by the admin, a default password is set. Students can then use the generated school ID and teachers their email address to log in.

* #### Student related operations
  1. Login using their school ID and password
  2. View their profile 
  3. Register for a particular course
  4. View their grade in all registered courses and their GPA
 
 
* #### Teacher related operations
  1. Login using their email address and password
  2. View their profile and the course they're handling
  3. Grade a student in the course they are registered to.
