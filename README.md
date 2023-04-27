# Aiohttp File Drive 

This was made for personal use primarily and I 
thought let others also use it, so I made this repo
public it has minimal functionality and protection (just a password).

It was created for transferring files across devices.

You can use this code make forks add functionality too.

You can also add functionality and make a pull request, I will check and merge it to master branch _IF IT HELPS MAKE THE PROGRAM BETTER_

this is a minimal implementation and not a full-fledged implementation.
But I am willing to make changes when someone requests a feature **WHEN I HAVE TIME**


<u>**_CURRENT STATUS :_**</u>
<ul>
<li>
The aiohttp server file needs to be updated
</li>
<li>The __fast_api__.py is working perfectly</li>
</ul>

<u>**_Using :_**</u>
<ol>
<li>
Create a project on vercel or any other service (you can fork and use the forked version it is optional)
</li>
<li>
Set environment variable(s) (<b>file_manager_password</b>, <i>file_manager_replace_string</i>)
</li>
<li>
you can visit the hosted site there will be a box at the top left corrnor enter your password there, and you can see the functions(upload, delete, open)
</li>
</ol>
note:

the second env variable is for replacing a string in all files delivered to empty string ' '

i.e. if your second var is "xyz" and file content is "wxyz" the only "w" will be delivered

if you don't set the password environment variable then it will be 'password'
