#!/usr/bin/env python3

'''
    pam-custom
    Copyright (C) 2013 Loris Tisisno <loris.tissino@gmail.com>
    Copyright (C) 2017-2018 Netsyms Technologies <contact@netsyms.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import requests
import json
import pwd
import crypt
import sys

api_url = "http://localhost/accounthub/api.php"
api_key = "123"

def load_settings():
  global api_url
  global api_key
  if os.path.isfile("/etc/netsyms-business/config.json"):
    with open("/etc/netsyms-business/config.json") as f:
      text = f.read()
      data = json.loads(text)
      api_url = data['apiurl']
      api_key = data['apikey']



def totp_verify(user, totp):
  req = {"key": api_key, "action": "verifytotp", "username": user, "code": totp}
  resp = requests.post(api_url, data=req)
  if resp.json()['status'] == "OK":
    if resp.json()['valid'] == True:
      return True
  return False

def totp_check(user, pamh):
  req = {"key": api_key, "action": "hastotp", "username": user}
  resp = requests.post(api_url, data=req)
  if resp.json()['status'] == "OK":
    if resp.json()['otp'] == True:
      otpmsg = pamh.Message(pamh.PAM_PROMPT_ECHO_ON, "Authentication code: ")
      rsp = pamh.conversation(otpmsg)
      otpcode = rsp.resp
      return totp_verify(user, otpcode)
    else:
      return True
  return False


def try_adduser(user, password):
  try:
    pwd.getpwnam(user)
  except KeyError:
    print('User ' + user + ' does not exist on this machine, creating...')
    # stick this in if you want offline auth, but it isn't updated if the pwd changes in AccountHub
    # -p $(mkpasswd -m sha-512 \"" + password + "\")
    os.system("useradd -s "+ "/bin/bash "+ "-d "+ "/home/" + user + " -m " + user)


def accounthub_auth(user, password, pamh):
  req = {"key": api_key, "action": "auth", "username": user, "password": password}
  resp = requests.post(api_url, data=req)
  if resp.json()['status'] == "OK":
    if totp_check(user, pamh):
      try_adduser(user, password)
      return True
    else:
      return False
  else:
    return False


def pam_sm_authenticate(pamh, flags, argv):
  load_settings()
  try:
    user = pamh.get_user(None)
    if user == None:
      return pamh.PAM_AUTH_ERR

    password = pamh.authtok
    if password == None:
      ## got no password in authtok - trying through conversation...
      passmsg = pamh.Message(pamh.PAM_PROMPT_ECHO_OFF, "Password for " + user + ": ")
      rsp = pamh.conversation(passmsg)
      password = rsp.resp
      # so we should at this point have the password either through the
      # prompt or from previous module

    if accounthub_auth(user, password, pamh):
      return pamh.PAM_SUCCESS
    else:
      return pamh.PAM_AUTH_ERR

  except pamh.exception as e:
    return e.pam_result

def pam_sm_setcred(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
  return pamh.PAM_SUCCESS
