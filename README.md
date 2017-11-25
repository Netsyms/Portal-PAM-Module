# PAM for Business Apps
This is a simple project with the goal of allowing Linux PAM authentication using the AccountHub API.  Use at your own risk.


## Installation

Since working with PAM can lead to problems in authentication, keep a
shell with root access open while experimenting.

Install the package libpam-python:

    sudo apt-get install libpam-python
    
Edit `pam_custom.py` and supply the Portal API URL and a valid API key.
    
Copy the provided `pam_custom.py` to `/lib/security`:

    sudo cp pam_custom.py /lib/security 

Make a backup of the file `/etc/pam.d/common-auth`:

    sudo cp /etc/pam.d/common-auth /etc/pam.d/common-auth.original
    
Edit the file `/etc/pam.d/common-auth` introducing a line in which you
declare your custom authentication method. It should be something like
this:

    auth  [success=2 default=ignore] pam_python.so pam_custom.py

and should be put just before (or after, according to your needs) the
other authentication methods.

Some explanations:

1. "success=2" means that the next two lines should be skipped in case of success (edit as needed)

2. "pam_python.so" is the name of the shared object that will be called by pam

3. "pam_custom.py" is the script in python that we provide

### Sample /etc/pam.d/common-auth

This config file will gather the username and password and attempt a normal login.  If that fails, PAM will try to process the login via this module.

    auth    [success=2 default=ignore]      pam_unix.so nullok_secure
    auth    [success=1 default=ignore]      pam_python.so pam_custom.py
    auth    requisite                       pam_deny.so
    auth    required                        pam_permit.so
