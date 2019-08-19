# Puppet Master

[![Build Status](https://travis-ci.org/qedsoftware/puppet-master.svg?branch=master)](https://travis-ci.org/qedsoftware/puppet-master)

Supported from Python >= 3.6


## Configuration

Django settings required for the package:

`PM__SELENIUM_DRIVER` - Selenium driver object used for testing
`PM__SELENIUM_DRIVER_PATH` - Path to driver executable
`PM__DEFAULT_SCREENSHOT_DIR` - Default screenshot directory

`PM__SERVICE_URL` - External service URL address on which Selenium will be run.
Used only while using SeleniumTestCase.

### Kobotoolbox-module only

`PM__KT_USERNAME`, `PM__KT_PASSWORD` - Credentials used to log in to the app
