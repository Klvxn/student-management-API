## Student Management API

### This is a REST API  for a school's student management system built with Flask and Flask-restx
### It includes endpoints for <br>


<ul>

#### <li> JWT Authentication </li>


#### <li> Admin only operations </li>
<ul>
  <li> Sign up  </li>
  <li> Create accounts for students and generate school ID for them </li>
  <li> Create accounts for teachers with their email address and full name </li>
  <li> Create and update courses </li>
  <li> Update student or teacher's information </li>
  <li> Get all students, teachers and courses </li>
  <li> Delete a student, teacher or course, etc. </li>
</ul>

<br>
When teachers or students accounts are created by the admin, a default password is set. Students can then use the generated school ID and teachers their email address to log in.


#### <li> Student related operations </li>
<ul>
  <li> Login using their school ID and password  </li>
  <li> View their profile  </li>
  <li> Register for a particular course </li>
  <li> View their grade in all registered courses and their GPA </li>
</ul>

#### <li> Teacher related operations </li>
<ul>
  <li> Login using their email address and password </li>
  <li> View their profile and the course they're handling </li>
  <li> Grade a student in the course they are registered to. </li>
</ul>
</ul>
